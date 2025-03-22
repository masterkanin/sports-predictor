"""
Training pipeline module for the neural network-based sports predictor.
This module handles data preparation, model training, and evaluation.
"""

import os
import json
import numpy as np
import pandas as pd
import tensorflow as tf
from typing import Dict, List, Tuple, Any, Optional, Union
from datetime import datetime
import logging
from sklearn.model_selection import train_test_split

from ..models import SportsPredictorModel, SportSpecificModel, MultiSportNormalizer, FeatureEngineer, UncertaintyEstimator

class TrainingPipeline:
    """
    Pipeline for training the sports prediction model.
    Handles data preparation, model training, and evaluation.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the training pipeline.
        
        Args:
            config_path: Path to the configuration directory
        """
        self.config_dir = config_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                     'config')
        
        # Load training configuration
        pipeline_config_path = os.path.join(self.config_dir, 'pipeline', 'training.json')
        with open(pipeline_config_path, 'r') as f:
            self.config = json.load(f)
            
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.normalizer = MultiSportNormalizer(self.config_dir)
        self.feature_engineer = FeatureEngineer(self.config.get('feature_engineering', {}))
        
        # Initialize sport-specific models
        self.models = {}
        
        self.logger.info("Training pipeline initialized")
    
    def _setup_logging(self):
        """Set up logging configuration"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file_path', os.path.join(log_dir, 'training.log'))
        
        # Create logger
        self.logger = logging.getLogger('training_pipeline')
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
    
    def prepare_data(self, data: Dict[str, Any], sport: str) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        """
        Prepare data for training, validation, and testing.
        
        Args:
            data: Raw data dictionary with player stats, team stats, etc.
            sport: Sport name (e.g., 'nba', 'nfl')
            
        Returns:
            Tuple of (train_data, val_data, test_data)
        """
        self.logger.info(f"Preparing data for {sport}")
        
        # Extract player and team data
        player_data = data.get('player_stats', [])
        team_data = data.get('team_stats', [])
        
        # Engineer features
        player_df = self.feature_engineer.engineer_player_features(player_data)
        team_df = self.feature_engineer.engineer_team_features(team_data)
        
        # Combine player and team features
        combined_df = self.feature_engineer.combine_player_team_features(player_df, team_df)
        
        # Add PrizePicks features if available
        if 'prizepicks' in data:
            combined_df = self.feature_engineer.create_prizepicks_features(combined_df, data['prizepicks'])
        
        # Convert back to dictionary format
        processed_data = combined_df.to_dict('records')
        
        # Split data into train, validation, and test sets
        train_data, temp_data = train_test_split(
            processed_data, 
            test_size=self.config.get('validation_test_size', 0.3),
            random_state=42
        )
        
        val_data, test_data = train_test_split(
            temp_data, 
            test_size=0.5,  # 50% of the temp_data (15% of total)
            random_state=42
        )
        
        self.logger.info(f"Data split: {len(train_data)} training, {len(val_data)} validation, {len(test_data)} test samples")
        
        return {
            'player_stats': train_data,
            'team_stats': team_data
        }, {
            'player_stats': val_data,
            'team_stats': team_data
        }, {
            'player_stats': test_data,
            'team_stats': team_data
        }
    
    def train_model_for_sport(self, data: Dict[str, Any], sport: str) -> Dict[str, Any]:
        """
        Train a model for a specific sport.
        
        Args:
            data: Raw data dictionary with player stats, team stats, etc.
            sport: Sport name (e.g., 'nba', 'nfl')
            
        Returns:
            Dictionary with training results and metrics
        """
        self.logger.info(f"Training model for {sport}")
        
        # Prepare data
        train_data, val_data, test_data = self.prepare_data(data, sport)
        
        # Create sport-specific model
        model_config = self.config.get('model', {})
        model_config['sports_config'] = {sport: self.config.get('sports_config', {}).get(sport, {})}
        
        sport_model = SportSpecificModel(sport, model_config)
        
        # Train the model
        training_config = self.config.get('training', {})
        history = sport_model.train(
            train_data,
            val_data,
            epochs=training_config.get('epochs', 100),
            batch_size=training_config.get('batch_size', 64)
        )
        
        # Evaluate the model
        evaluation = sport_model.evaluate(test_data)
        
        # Save the model
        model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, f"{sport}_model.h5")
        sport_model.save_model(model_path)
        
        # Store the model for later use
        self.models[sport] = sport_model
        
        # Return results
        results = {
            'sport': sport,
            'history': history,
            'evaluation': evaluation,
            'model_path': model_path
        }
        
        self.logger.info(f"Model training completed for {sport}")
        return results
    
    def train_all_sports(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Train models for all sports.
        
        Args:
            data: Dictionary mapping sport names to data dictionaries
            
        Returns:
            Dictionary mapping sport names to training results
        """
        self.logger.info("Training models for all sports")
        
        results = {}
        
        for sport, sport_data in data.items():
            try:
                sport_results = self.train_model_for_sport(sport_data, sport)
                results[sport] = sport_results
            except Exception as e:
                self.logger.error(f"Error training model for {sport}: {str(e)}")
                results[sport] = {'error': str(e)}
        
        return results
    
    def optimize_hyperparameters(self, data: Dict[str, Any], sport: str) -> Dict[str, Any]:
        """
        Optimize hyperparameters for a specific sport model.
        
        Args:
            data: Raw data dictionary with player stats, team stats, etc.
            sport: Sport name (e.g., 'nba', 'nfl')
            
        Returns:
            Dictionary with optimal hyperparameters
        """
        self.logger.info(f"Optimizing hyperparameters for {sport}")
        
        # This is a placeholder for hyperparameter optimization
        # In a real implementation, this would use a library like Optuna or Ray Tune
        
        # For now, we'll return a default set of hyperparameters
        optimal_params = {
            'learning_rate': 0.001,
            'dropout_rate': 0.2,
            'lstm_units': 64,
            'embedding_dim': 32,
            'batch_size': 64
        }
        
        self.logger.info(f"Hyperparameter optimization completed for {sport}")
        return optimal_params
    
    def create_ensemble(self, data: Dict[str, Any], sport: str, num_models: int = 5) -> List[Any]:
        """
        Create an ensemble of models for a specific sport.
        
        Args:
            data: Raw data dictionary with player stats, team stats, etc.
            sport: Sport name (e.g., 'nba', 'nfl')
            num_models: Number of models in the ensemble
            
        Returns:
            List of trained models
        """
        self.logger.info(f"Creating ensemble of {num_models} models for {sport}")
        
        # Prepare data
        train_data, val_data, test_data = self.prepare_data(data, sport)
        
        # Create and train multiple models
        models = []
        
        for i in range(num_models):
            # Create model with slightly different configuration
            model_config = self.config.get('model', {}).copy()
            model_config['sports_config'] = {sport: self.config.get('sports_config', {}).get(sport, {})}
            
            # Vary some parameters for diversity
            model_config['dropout_rate'] = model_config.get('dropout_rate', 0.2) + (i * 0.05)
            model_config['seed'] = 42 + i
            
            # Create and train model
            sport_model = SportSpecificModel(sport, model_config)
            
            training_config = self.config.get('training', {})
            sport_model.train(
                train_data,
                val_data,
                epochs=training_config.get('epochs', 100),
                batch_size=training_config.get('batch_size', 64)
            )
            
            # Save the model
            model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')
            os.makedirs(model_dir, exist_ok=True)
            model_path = os.path.join(model_dir, f"{sport}_ensemble_model_{i}.h5")
            sport_model.save_model(model_path)
            
            models.append(sport_model)
        
        self.logger.info(f"Ensemble creation completed for {sport}")
        return models
    
    def evaluate_model(self, model: Any, test_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Evaluate a trained model on test data.
        
        Args:
            model: Trained model
            test_data: Test data dictionary
            
        Returns:
            Dictionary with evaluation metrics
        """
        # Evaluate the model
        evaluation = model.evaluate(test_data)
        
        return evaluation
    
    def cross_validate(self, data: Dict[str, Any], sport: str, n_folds: int = 5) -> Dict[str, List[float]]:
        """
        Perform cross-validation for a specific sport model.
        
        Args:
            data: Raw data dictionary with player stats, team stats, etc.
            sport: Sport name (e.g., 'nba', 'nfl')
            n_folds: Number of cross-validation folds
            
        Returns:
            Dictionary with cross-validation metrics
        """
        self.logger.info(f"Performing {n_folds}-fold cross-validation for {sport}")
        
        # Extract player data
        player_data = data.get('player_stats', [])
        
        # Engineer features
        player_df = self.feature_engineer.engineer_player_features(player_data)
        
        # Convert back to dictionary format
        processed_data = player_df.to_dict('records')
        
        # Initialize metrics
        metrics = {
            'regression_mse': [],
            'regression_mae': [],
            'classification_accuracy': [],
            'classification_auc': []
        }
        
        # Perform cross-validation
        fold_size = len(processed_data) // n_folds
        
        for i in range(n_folds):
            # Create train/test split for this fold
            test_start = i * fold_size
            test_end = (i + 1) * fold_size if i < n_folds - 1 else len(processed_data)
            
            test_fold = processed_data[test_start:test_end]
            train_fold = processed_data[:test_start] + processed_data[test_end:]
            
            # Create and train model
            model_config = self.config.get('model', {})
            model_config['sports_config'] = {sport: self.config.get('sports_config', {}).get(sport, {})}
            
            sport_model = SportSpecificModel(sport, model_config)
            
            # Train the model
            training_config = self.config.get('training', {})
            sport_model.train(
                {'player_stats': train_fold},
                None,  # No validation data for CV
                epochs=training_config.get('cv_epochs', 50),
                batch_size=training_config.get('batch_size', 64)
            )
            
            # Evaluate the model
            evaluation = sport_model.evaluate({'player_stats': test_fold})
            
            # Store metrics
            metrics['regression_mse'].append(evaluation.get('regression_output_mse', 0))
            metrics['regression_mae'].append(evaluation.get('regression_output_mae', 0))
            metrics['classification_accuracy'].append(evaluation.get('classification_output_accuracy', 0))
            metrics['classification_auc'].append(evaluation.get('classification_output_auc', 0))
        
        # Calculate mean and std for each metric
        for metric in metrics:
            metrics[f'{metric}_mean'] = np.mean(metrics[metric])
            metrics[f'{metric}_std'] = np.std(metrics[metric])
        
        self.logger.info(f"Cross-validation completed for {sport}")
        return metrics
