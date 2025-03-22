"""
Monitoring module for the neural network-based sports predictor.
This module handles performance monitoring, data drift detection, and model calibration.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional, Union
from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns

class MonitoringSystem:
    """
    Monitoring system for the sports prediction pipeline.
    Handles performance tracking, data drift detection, and model calibration.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the monitoring system.
        
        Args:
            config_path: Path to the configuration directory
        """
        self.config_dir = config_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                     'config')
        
        # Load monitoring configuration
        monitoring_config_path = os.path.join(self.config_dir, 'pipeline', 'monitoring.json')
        if os.path.exists(monitoring_config_path):
            with open(monitoring_config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "performance_metrics": ["mse", "mae", "accuracy", "auc"],
                "drift_detection_window": 30,
                "calibration_window": 14,
                "alert_thresholds": {
                    "mse_increase": 0.2,
                    "accuracy_decrease": 0.1,
                    "drift_score": 0.05
                },
                "logging": {
                    "level": "INFO",
                    "file_path": "logs/monitoring.log"
                }
            }
            
        # Setup logging
        self._setup_logging()
        
        # Initialize performance history
        self.performance_history = {}
        
        # Initialize data distribution history
        self.data_distribution_history = {}
        
        # Load historical data if available
        self._load_history()
        
        self.logger.info("Monitoring system initialized")
    
    def _setup_logging(self):
        """Set up logging configuration"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file_path', os.path.join(log_dir, 'monitoring.log'))
        
        # Create logger
        self.logger = logging.getLogger('monitoring_system')
        self.logger.setLevel(log_level)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        
        # Create formatter and add to handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger if not already added
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
    
    def _load_history(self):
        """Load historical performance and data distribution data"""
        history_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                  'output', 'monitoring')
        
        # Load performance history
        performance_path = os.path.join(history_dir, 'performance_history.json')
        if os.path.exists(performance_path):
            with open(performance_path, 'r') as f:
                self.performance_history = json.load(f)
        
        # Load data distribution history
        distribution_path = os.path.join(history_dir, 'distribution_history.json')
        if os.path.exists(distribution_path):
            with open(distribution_path, 'r') as f:
                self.data_distribution_history = json.load(f)
    
    def _save_history(self):
        """Save performance and data distribution history"""
        history_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                  'output', 'monitoring')
        os.makedirs(history_dir, exist_ok=True)
        
        # Save performance history
        performance_path = os.path.join(history_dir, 'performance_history.json')
        with open(performance_path, 'w') as f:
            json.dump(self.performance_history, f, indent=2)
        
        # Save data distribution history
        distribution_path = os.path.join(history_dir, 'distribution_history.json')
        with open(distribution_path, 'w') as f:
            json.dump(self.data_distribution_history, f, indent=2)
    
    def track_performance(self, predictions: Dict[str, List[Dict[str, Any]]], 
                         actual_outcomes: Dict[str, List[Dict[str, Any]]],
                         date: str = None) -> Dict[str, Dict[str, float]]:
        """
        Track prediction performance against actual outcomes.
        
        Args:
            predictions: Dictionary mapping sport names to prediction lists
            actual_outcomes: Dictionary mapping sport names to actual outcome lists
            date: Date string in format 'YYYY-MM-DD' (defaults to today)
            
        Returns:
            Dictionary with performance metrics for each sport
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        self.logger.info(f"Tracking performance for {date}")
        
        performance = {}
        
        for sport, sport_predictions in predictions.items():
            if sport not in actual_outcomes:
                self.logger.warning(f"No actual outcomes available for {sport}")
                continue
            
            sport_outcomes = actual_outcomes[sport]
            
            # Match predictions with outcomes
            matched_data = self._match_predictions_with_outcomes(sport_predictions, sport_outcomes)
            
            if not matched_data:
                self.logger.warning(f"No matched data for {sport}")
                continue
            
            # Calculate performance metrics
            sport_performance = self._calculate_performance_metrics(matched_data)
            performance[sport] = sport_performance
            
            # Update performance history
            if sport not in self.performance_history:
                self.performance_history[sport] = {}
            
            self.performance_history[sport][date] = sport_performance
            
            # Check for performance degradation
            self._check_performance_degradation(sport, date)
        
        # Save updated history
        self._save_history()
        
        return performance
    
    def _match_predictions_with_outcomes(self, predictions: List[Dict[str, Any]], 
                                        outcomes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Match predictions with actual outcomes.
        
        Args:
            predictions: List of predictions
            outcomes: List of actual outcomes
            
        Returns:
            List of matched data with predictions and outcomes
        """
        matched_data = []
        
        # Create lookup dictionary for outcomes
        outcome_lookup = {}
        for outcome in outcomes:
            key = f"{outcome.get('player', '')}-{outcome.get('stat', '')}-{outcome.get('date', '')}"
            outcome_lookup[key] = outcome
        
        # Match predictions with outcomes
        for pred in predictions:
            key = f"{pred.get('player', '')}-{pred.get('stat', '')}-{pred.get('date', '')}"
            if key in outcome_lookup:
                outcome = outcome_lookup[key]
                
                matched_item = {
                    'player': pred.get('player', ''),
                    'team': pred.get('team', ''),
                    'opponent': pred.get('opponent', ''),
                    'date': pred.get('date', ''),
                    'stat': pred.get('stat', ''),
                    'predicted_value': pred.get('predicted_value', 0),
                    'actual_value': outcome.get('actual_value', 0),
                    'line': pred.get('line', 0),
                    'over_probability': pred.get('over_probability', 0.5),
                    'actual_over': 1 if outcome.get('actual_value', 0) > pred.get('line', 0) else 0,
                    'confidence': pred.get('confidence', ''),
                    'confidence_score': pred.get('confidence_score', 50)
                }
                
                matched_data.append(matched_item)
        
        return matched_data
    
    def _calculate_performance_metrics(self, matched_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate performance metrics for matched prediction data.
        
        Args:
            matched_data: List of matched predictions and outcomes
            
        Returns:
            Dictionary with performance metrics
        """
        metrics = {}
        
        # Extract arrays for calculations
        y_true = np.array([item['actual_value'] for item in matched_data])
        y_pred = np.array([item['predicted_value'] for item in matched_data])
        
        # Binary classification arrays
        y_true_binary = np.array([item['actual_over'] for item in matched_data])
        y_pred_proba = np.array([item['over_probability'] for item in matched_data])
        y_pred_binary = (y_pred_proba > 0.5).astype(int)
        
        # Calculate regression metrics
        metrics['mse'] = mean_squared_error(y_true, y_pred)
        metrics['mae'] = mean_absolute_error(y_true, y_pred)
        metrics['rmse'] = np.sqrt(metrics['mse'])
        
        # Calculate classification metrics
        metrics['accuracy'] = accuracy_score(y_true_binary, y_pred_binary)
        metrics['auc'] = roc_auc_score(y_true_binary, y_pred_proba)
        
        # Calculate confidence-weighted metrics
        confidence_weights = np.array([item['confidence_score'] / 100 for item in matched_data])
        metrics['weighted_mse'] = np.average((y_true - y_pred) ** 2, weights=confidence_weights)
        
        # Calculate over/under specific metrics
        over_indices = y_true_binary == 1
        under_indices = y_true_binary == 0
        
        if np.any(over_indices):
            metrics['over_accuracy'] = accuracy_score(
                y_true_binary[over_indices], 
                y_pred_binary[over_indices]
            )
        else:
            metrics['over_accuracy'] = 0
            
        if np.any(under_indices):
            metrics['under_accuracy'] = accuracy_score(
                y_true_binary[under_indices], 
                y_pred_binary[under_indices]
            )
        else:
            metrics['under_accuracy'] = 0
        
        # Calculate calibration metrics
        confidence_bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
        calibration_scores = []
        
        for i in range(len(confidence_bins) - 1):
            lower = confidence_bins[i]
            upper = confidence_bins[i + 1]
            
            bin_indices = (y_pred_proba >= lower) & (y_pred_proba < upper)
            if np.any(bin_indices):
                avg_confidence = np.mean(y_pred_proba[bin_indices])
                avg_accuracy = np.mean(y_true_binary[bin_indices])
                calibration_scores.append(abs(avg_confidence - avg_accuracy))
        
        if calibration_scores:
            metrics['calibration_error'] = np.mean(calibration_scores)
        else:
            metrics['calibration_error'] = 0
        
        return metrics
    
    def _check_performance_degradation(self, sport: str, date: str):
        """
        Check for performance degradation compared to historical performance.
        
        Args:
            sport: Sport name
            date: Current date
        """
        if sport not in self.performance_history:
            return
        
        # Get current performance
        current_performance = self.performance_history[sport].get(date)
        if not current_performance:
            return
        
        # Get historical dates
        dates = list(self.performance_history[sport].keys())
        dates.remove(date)
        
        if not dates:
            return
        
        # Sort dates and get recent history
        dates.sort(reverse=True)
        recent_dates = dates[:7]  # Last week
        
        if not recent_dates:
            return
        
        # Calculate average recent performance
        recent_performance = {}
        for metric in current_performance:
            values = [self.performance_history[sport][d].get(metric, 0) for d in recent_dates]
            recent_performance[metric] = np.mean(values)
        
        # Check for degradation
        alert_thresholds = self.config.get('alert_thresholds', {})
        
        # MSE increase
        mse_threshold = alert_thresholds.get('mse_increase', 0.2)
        if (current_performance.get('mse', 0) > 
            recent_performance.get('mse', 0) * (1 + mse_threshold)):
            self.logger.warning(
                f"Performance degradation detected for {sport}: MSE increased by "
                f"{(current_performance['mse'] / recent_performance['mse'] - 1) * 100:.1f}%"
            )
        
        # Accuracy decrease
        acc_threshold = alert_thresholds.get('accuracy_decrease', 0.1)
        if (current_performance.get('accuracy', 1) < 
            recent_performance.get('accuracy', 1) * (1 - acc_threshold)):
            self.logger.warning(
                f"Performance degradation detected for {sport}: Accuracy decreased by "
                f"{(1 - current_performance['accuracy'] / recent_performance['accuracy']) * 100:.1f}%"
            )
    
    def detect_data_drift(self, new_data: Dict[str, List[Dict[str, Any]]], 
                         date: str = None) -> Dict[str, Dict[str, float]]:
        """
        Detect drift in input data distribution.
        
        Args:
            new_data: Dictionary mapping sport names to data lists
            date: Date string in format 'YYYY-MM-DD' (defaults to today)
            
        Returns:
            Dictionary with drift scores for each sport
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        self.logger.info(f"Detecting data drift for {date}")
        
        drift_scores = {}
        
        for sport, sport_data in new_data.items():
            # Calculate data distribution statistics
            distribution = self._calculate_data_distribution(sport_data)
            
            # Update distribution history
            if sport not in self.data_distribution_history:
                self.data_distribution_history[sport] = {}
            
            self.data_distribution_history[sport][date] = distribution
            
            # Calculate drift score compared to historical distribution
            drift_score = self._calculate_drift_score(sport, distribution)
            drift_scores[sport] = drift_score
            
            # Check for significant drift
            self._check_significant_drift(sport, drift_score)
        
        # Save updated history
        self._save_history()
        
        return drift_scores
    
    def _calculate_data_distribution(self, data: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """
        Calculate distribution statistics for input data.
        
        Args:
            data: List of data points
            
        Returns:
            Dictiona<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>