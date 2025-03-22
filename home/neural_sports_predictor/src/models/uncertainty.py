"""
Uncertainty estimation module for the neural network-based sports predictor.
This module provides methods for estimating prediction uncertainty.
"""

import tensorflow as tf
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union

class UncertaintyEstimator:
    """
    Uncertainty estimation for sports prediction models.
    Implements Monte Carlo Dropout and other methods for uncertainty quantification.
    """
    
    def __init__(self, model, config: Dict[str, Any]):
        """
        Initialize the uncertainty estimator.
        
        Args:
            model: Trained TensorFlow model with dropout layers
            config: Configuration dictionary with uncertainty parameters
        """
        self.model = model
        self.config = config
        self.num_samples = config.get('mc_dropout_samples', 100)
        self.dropout_rate = config.get('dropout_rate', 0.2)
        
    def monte_carlo_dropout(self, inputs: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Perform Monte Carlo Dropout for uncertainty estimation.
        
        Args:
            inputs: Model input data
            
        Returns:
            Dictionary with mean predictions and uncertainty estimates
        """
        # Enable dropout at inference time
        regression_samples = []
        classification_samples = []
        
        # Create a function that includes dropout at inference time
        inference_model = self._create_dropout_inference_model()
        
        # Perform multiple forward passes
        for _ in range(self.num_samples):
            regression_pred, classification_pred = inference_model(inputs, training=True)
            regression_samples.append(regression_pred)
            classification_samples.append(classification_pred)
        
        # Convert to numpy arrays
        regression_samples = np.array(regression_samples)
        classification_samples = np.array(classification_samples)
        
        # Calculate mean and standard deviation for regression
        regression_mean = np.mean(regression_samples, axis=0)
        regression_std = np.std(regression_samples, axis=0)
        
        # Calculate mean and standard deviation for classification
        classification_mean = np.mean(classification_samples, axis=0)
        classification_std = np.std(classification_samples, axis=0)
        
        # Calculate confidence intervals for regression
        regression_lower = regression_mean - 1.96 * regression_std
        regression_upper = regression_mean + 1.96 * regression_std
        
        # Calculate entropy for classification uncertainty
        classification_entropy = -1 * (
            classification_mean * np.log(classification_mean + 1e-10) + 
            (1 - classification_mean) * np.log(1 - classification_mean + 1e-10)
        )
        
        return {
            'regression_mean': regression_mean,
            'regression_std': regression_std,
            'regression_lower': regression_lower,
            'regression_upper': regression_upper,
            'classification_mean': classification_mean,
            'classification_std': classification_std,
            'classification_entropy': classification_entropy
        }
    
    def _create_dropout_inference_model(self):
        """
        Create a model that keeps dropout active during inference.
        
        Returns:
            Model with dropout enabled for inference
        """
        # For TensorFlow 2.x, we can use the model directly with training=True
        # This function is included for clarity and potential customization
        return self.model
    
    def quantile_regression(self, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Perform quantile regression for uncertainty estimation.
        Note: This requires a model specifically trained for quantile regression.
        
        Args:
            inputs: Model input data
            
        Returns:
            Dictionary with quantile predictions
        """
        # This is a placeholder for quantile regression
        # In a real implementation, this would use a model trained with quantile loss
        
        # For now, we'll use Monte Carlo Dropout as a substitute
        mc_results = self.monte_carlo_dropout(inputs)
        
        # Simulate quantile regression results
        return {
            'median': mc_results['regression_mean'],
            'lower_quantile': mc_results['regression_lower'],
            'upper_quantile': mc_results['regression_upper']
        }
    
    def ensemble_uncertainty(self, models: List[Any], inputs: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Estimate uncertainty using an ensemble of models.
        
        Args:
            models: List of trained models
            inputs: Model input data
            
        Returns:
            Dictionary with ensemble predictions and uncertainty estimates
        """
        regression_samples = []
        classification_samples = []
        
        # Get predictions from each model
        for model in models:
            regression_pred, classification_pred = model(inputs, training=False)
            regression_samples.append(regression_pred)
            classification_samples.append(classification_pred)
        
        # Convert to numpy arrays
        regression_samples = np.array(regression_samples)
        classification_samples = np.array(classification_samples)
        
        # Calculate mean and standard deviation for regression
        regression_mean = np.mean(regression_samples, axis=0)
        regression_std = np.std(regression_samples, axis=0)
        
        # Calculate mean and standard deviation for classification
        classification_mean = np.mean(classification_samples, axis=0)
        classification_std = np.std(classification_samples, axis=0)
        
        return {
            'regression_mean': regression_mean,
            'regression_std': regression_std,
            'classification_mean': classification_mean,
            'classification_std': classification_std
        }
    
    def calibrate_uncertainty(self, predictions: Dict[str, np.ndarray], 
                             calibration_data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Calibrate uncertainty estimates using historical data.
        
        Args:
            predictions: Model predictions with uncertainty
            calibration_data: Historical data for calibration
            
        Returns:
            Calibrated uncertainty estimates
        """
        # This is a placeholder for uncertainty calibration
        # In a real implementation, this would adjust uncertainty estimates based on historical performance
        
        # For now, we'll return the original predictions
        return predictions
    
    def confidence_score(self, uncertainty: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Convert uncertainty estimates to a confidence score (0-100%).
        
        Args:
            uncertainty: Uncertainty estimates
            
        Returns:
            Confidence scores
        """
        # Calculate confidence score based on regression standard deviation
        if 'regression_std' in uncertainty:
            # Normalize standard deviation to a confidence score
            # Lower std = higher confidence
            max_std = self.config.get('max_expected_std', 10.0)
            confidence = 100 * (1 - np.minimum(uncertainty['regression_std'] / max_std, 1.0))
            return confidence
        
        # Fallback if regression_std is not available
        if 'classification_std' in uncertainty:
            # For classification, confidence is inversely related to standard deviation
            confidence = 100 * (1 - 2 * uncertainty['classification_std'])
            return np.maximum(confidence, 0)  # Ensure non-negative
        
        # Default confidence if no uncertainty measures are available
        return np.ones(uncertainty[list(uncertainty.keys())[0]].shape) * 50  # 50% confidence
    
    def categorize_confidence(self, confidence_scores: np.ndarray) -> List[str]:
        """
        Categorize confidence scores into descriptive labels.
        
        Args:
            confidence_scores: Numerical confidence scores
            
        Returns:
            List of confidence category labels
        """
        categories = []
        
        for score in confidence_scores:
            if score >= 90:
                categories.append('Very High')
            elif score >= 75:
                categories.append('High')
            elif score >= 50:
                categories.append('Moderate')
            elif score >= 25:
                categories.append('Low')
            else:
                categories.append('Very Low')
        
        return categories
