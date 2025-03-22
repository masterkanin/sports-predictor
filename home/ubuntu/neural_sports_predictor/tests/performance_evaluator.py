"""
Performance evaluation module for the neural network-based sports predictor.
This module contains functions for evaluating model performance across different sports.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any, Optional, Union
from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score, roc_auc_score, confusion_matrix

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class PerformanceEvaluator:
    """
    Performance evaluator for the sports prediction system.
    Evaluates model performance across different sports and metrics.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the performance evaluator.
        
        Args:
            config_path: Path to the configuration directory
        """
        self.config_dir = config_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        
        # Create output directory
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output', 'evaluation')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_test_results(self, results_path: str) -> Dict[str, Any]:
        """
        Load test results from a file.
        
        Args:
            results_path: Path to the test results file
            
        Returns:
            Dictionary with test results
        """
        with open(results_path, 'r') as f:
            results = json.load(f)
        
        return results
    
    def evaluate_regression_performance(self, predictions: List[Dict[str, Any]], 
                                       actual_outcomes: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Evaluate regression performance metrics.
        
        Args:
            predictions: List of predictions
            actual_outcomes: List of actual outcomes
            
        Returns:
            Dictionary with regression performance metrics
        """
        # Extract values
        y_true = np.array([outcome['actual_value'] for outcome in actual_outcomes])
        y_pred = np.array([pred['predicted_value'] for pred in predictions])
        
        # Calculate metrics
        metrics = {}
        metrics['mse'] = mean_squared_error(y_true, y_pred)
        metrics['rmse'] = np.sqrt(metrics['mse'])
        metrics['mae'] = mean_absolute_error(y_true, y_pred)
        
        # Calculate mean absolute percentage error
        non_zero_indices = y_true != 0
        if np.any(non_zero_indices):
            mape = np.mean(np.abs((y_true[non_zero_indices] - y_pred[non_zero_indices]) / y_true[non_zero_indices])) * 100
            metrics['mape'] = mape
        else:
            metrics['mape'] = 0
        
        # Calculate R-squared
        if np.var(y_true) > 0:
            metrics['r2'] = 1 - (np.sum((y_true - y_pred) ** 2) / np.sum((y_true - np.mean(y_true)) ** 2))
        else:
            metrics['r2'] = 0
        
        return metrics
    
    def evaluate_classification_performance(self, predictions: List[Dict[str, Any]], 
                                          actual_outcomes: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Evaluate classification performance metrics.
        
        Args:
            predictions: List of predictions
            actual_outcomes: List of actual outcomes
            
        Returns:
            Dictionary with classification performance metrics
        """
        # Extract values
        y_true = []
        y_pred_proba = []
        
        for pred, outcome in zip(predictions, actual_outcomes):
            line = pred.get('line', 0)
            actual_value = outcome.get('actual_value', 0)
            actual_over = 1 if actual_value > line else 0
            
            over_probability = pred.get('over_probability', 0.5)
            
            y_true.append(actual_over)
            y_pred_proba.append(over_probability)
        
        y_true = np.array(y_true)
        y_pred_proba = np.array(y_pred_proba)
        y_pred = (y_pred_proba > 0.5).astype(int)
        
        # Calculate metrics
        metrics = {}
        metrics['accuracy'] = accuracy_score(y_true, y_pred)
        
        # Calculate AUC if there are both positive and negative classes
        if len(np.unique(y_true)) > 1:
            metrics['auc'] = roc_auc_score(y_true, y_pred_proba)
        else:
            metrics['auc'] = 0.5  # Default for single class
        
        # Calculate confusion matrix
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        
        metrics['precision'] = tp / (tp + fp) if (tp + fp) > 0 else 0
        metrics['recall'] = tp / (tp + fn) if (tp + fn) > 0 else 0
        metrics['f1'] = 2 * metrics['precision'] * metrics['recall'] / (metrics['precision'] + metrics['recall']) if (metrics['precision'] + metrics['recall']) > 0 else 0
        
        # Calculate over/under specific metrics
        over_indices = y_true == 1
        under_indices = y_true == 0
        
        if np.any(over_indices):
            metrics['over_accuracy'] = accuracy_score(y_true[over_indices], y_pred[over_indices])
        else:
            metrics['over_accuracy'] = 0
            
        if np.any(under_indices):
            metrics['under_accuracy'] = accuracy_score(y_true[under_indices], y_pred[under_indices])
        else:
            metrics['under_accuracy'] = 0
        
        return metrics
    
    def evaluate_confidence_calibration(self, predictions: List[Dict[str, Any]], 
                                      actual_outcomes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate confidence calibration.
        
        Args:
            predictions: List of predictions
            actual_outcomes: List of actual outcomes
            
        Returns:
            Dictionary with calibration metrics and curve data
        """
        # Extract values
        confidence_scores = []
        correct_predictions = []
        
        for pred, outcome in zip(predictions, actual_outcomes):
            line = pred.get('line', 0)
            actual_value = outcome.get('actual_value', 0)
            actual_over = 1 if actual_value > line else 0
            
            over_probability = pred.get('over_probability', 0.5)
            predicted_over = 1 if over_probability > 0.5 else 0
            
            confidence_score = pred.get('confidence_score', 50)
            correct = actual_over == predicted_over
            
            confidence_scores.append(confidence_score)
            correct_predictions.append(correct)
        
        confidence_scores = np.array(confidence_scores)
        correct_predictions = np.array(correct_predictions)
        
        # Calculate calibration curve
        bins = np.linspace(0, 100, 11)  # 0, 10, 20, ..., 100
        bin_indices = np.digitize(confidence_scores, bins)
        
        calibration_curve = []
        
        for i in range(1, len(bins)):
            bin_mask = bin_indices == i
            if np.any(bin_mask):
                bin_confidence = np.mean(confidence_scores[bin_mask])
                bin_accuracy = np.mean(correct_predictions[bin_mask])
                bin_count = np.sum(bin_mask)
                
                calibration_curve.append({
                    'confidence': bin_confidence,
                    'accuracy': bin_accuracy,
                    'count': int(bin_count)
                })
        
        # Calculate calibration metrics
        calibration_error = 0
        total_weight = 0
        
        for point in calibration_curve:
            confidence = point['confidence'] / 100  # Convert to 0-1 scale
            accuracy = point['accuracy']
            count = point['count']
            
            calibration_error += count * abs(confidence - accuracy)
            total_weight += count
        
        if total_weight > 0:
            calibration_error /= total_weight
        
        return {
            'calibration_error': calibration_error,
            'calibration_curve': calibration_curve
        }
    
    def evaluate_sport_performance(self, predictions: List[Dict[str, Any]], 
                                 actual_outcomes: List[Dict[str, Any]],
                                 sport: str) -> Dict[str, Any]:
        """
        Evaluate performance for a specific sport.
        
        Args:
            predictions: List of predictions
            actual_outcomes: List of actual outcomes
            sport: Sport name
            
        Returns:
            Dictionary with performance metrics
        """
        # Evaluate regression performance
        regression_metrics = self.evaluate_regression_performance(predictions, actual_outcomes)
        
        # Evaluate classification performance
        classification_metrics = self.evaluate_classification_performance(predictions, actual_outcomes)
        
        # Evaluate confidence calibration
        calibration_metrics = self.evaluate_confidence_calibration(predictions, actual_outcomes)
        
        # Combine metrics
        performance = {
            'sport': sport,
            'sample_size': len(predictions),
            'regression': regression_metrics,
            'classification': classification_metrics,
            'calibration': calibration_metrics
        }
        
        return performance
    
    def evaluate_all_sports(self, predictions: Dict[str, List[Dict[str, Any]]], 
                          actual_outcomes: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        """
        Evaluate performance for all sports.
        
        Args:
            predictions: Dictionary mapping sport names to prediction lists
            actual_outcomes: Dictionary mapping sport names to actual outcome lists
            
        Returns:
            Dictionary mapping sport names to performance metrics
        """
        performance = {}
        
        for sport in predictions:
            if sport in actual_outcomes:
                sport_predictions = predictions[sport]
                sport_outcomes = actual_outcomes[sport]
                
                # Match predictions with outcomes
                matched_predictions = []
                matched_outcomes = []
                
                for pred in sport_predictions:
                    for outcome in sport_outcomes:
                        if (pred.get('player') == outcome.get('player') and
                            pred.get('date') == outcome.get('date') and
                            pred.get('stat') == outcome.get('stat')):
                            matched_predictions.append(pred)
                            matched_outcomes.append(outcome)
                            break
                
                if matched_predictions:
                    sport_performance = self.evaluate_sport_performance(
                        matched_predictions, matched_outcomes, sport
                    )
                    performance[sport] = sport_performance
        
        return performance
    
    def compare_sports_performance(self, performance: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare performance across different sports.
        
        Args:
            performance: Dictionary mapping sport names to performance metrics
            
        Returns:
            Dictionary with cross-sport comparison metrics
        """
        comparison = {
            'regression': {},
            'classification': {},
            'sample_sizes': {}
        }
        
        # Extract metrics for each sport
        for sport, sport_performance in performance.items():
            # Sample size
            comparison['sample_sizes'][sport] = sport_performance.get('sample_size', 0)
            
            # Regression metrics
            for metric in ['mse', 'rmse', 'mae', 'mape', 'r2']:
                if metric not in comparison['regression']:
                    comparison['regression'][metric] = {}
                
                comparison['regression'][metric][sport] = sport_performance.get('regression', {}).get(metric, 0)
            
            # Classification metrics
            for metric in ['accuracy', 'auc', 'precision', 'recall', 'f1']:
                if metric not in comparison['classification']:
                    comparison['classification'][metric] = {}
                
                comparison['classification'][metric][sport] = sport_performance.get('classification', {}).get(metric, 0)
        
        # Calculate overall metrics
        comparison['overall'] = {
            'regression': {},
            'classification': {}
        }
        
        # Weighted average for regression metrics
        for metric in comparison['regression']:
            values = []
            weights = []
            
            for sport in comparison['regression'][metric]:
                value = comparison['regression'][metric][sport]
                weight = comparison['sample_sizes'][sport]
                
                values.append(value)
                weights.append(weight)
            
            if sum(weights) > 0:
                comparison['overall']['regression'][metric] = np.average(values, weights=weights)
            else:
                comparison['overall']['regression'][metric] = np.mean(values) if values else 0
        
        # Weighted average for classification metrics
        for metric in comparison['classification']:
            values = []
            weights = []
            
            for sport in comparison['classification'][metric]:
                value = comparison['classification'][metric][sport]
                weight = comparison['sample_sizes'][sport]
                
                values.append(value)
                weights.append(weight)
            
            if sum(weights) > 0:
                comparison['overall']['classification'][metric] = np.average(values, weights=weights)
            else:
                comparison['overall']['classification'][metric] = np.mean(values) if values else 0
        
        return comparison
    
    def visualize_performance(self, performance: Dict[str, Dict[str, Any]], output_dir: str = None) -> str:
        """
        Generate visualizations of performance metrics.
        
        Args:
            performance: Dictionary mapping sport names to performance metrics
            output_dir: Directory to save visualizations
            
        Returns:
            Path to the output directory
        """
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, 'visualizations')
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # Regression metrics comparison
        self._plot_regression_comparison(performance, output_dir)
        
        # Classification metrics comparison
        self._plot_classification_comparison(performance, output_dir)
        
        # Calibration curves
        self._plot_calibration_curves(performance, output_dir)
        
        # Sport-specific performance
        for sport, sport_performance in performance.items():
            self._plot_sport_performance(sport, sport_performance, output_dir)
        
        return output_dir
    
    def _plot_regression_comparison(self, performance: Dict[str, Dict[str, Any]], output_dir: str):
        """
        Plot regression metrics comparison across sports.
        
        Args:
            performance: Dictionary mapping sport names to performance metrics
            output_dir: Directory to save visualizations
        """
     <response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>