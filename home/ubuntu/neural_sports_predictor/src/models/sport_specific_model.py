"""
Sport-specific model implementation for the neural network-based sports predictor.
This module extends the base model with sport-specific preprocessing and feature engineering.
"""

import tensorflow as tf
from tensorflow.keras import layers, Model
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union

from .base_model import SportsPredictorModel

class SportSpecificModel:
    """
    Sport-specific implementation of the neural network model.
    Handles sport-specific preprocessing, feature engineering, and model configuration.
    """
    
    def __init__(self, sport_name: str, config: Dict[str, Any]):
        """
        Initialize the sport-specific model.
        
        Args:
            sport_name: Name of the sport (e.g., 'nba', 'nfl')
            config: Configuration dictionary with model parameters
        """
        self.sport_name = sport_name.lower()
        self.config = config
        
        # Get sport-specific configuration
        self.sport_config = config.get('sports_config', {}).get(self.sport_name, {})
        
        # Create base model
        self.base_model = SportsPredictorModel(config)
        
        # Set up feature engineering parameters
        self.feature_engineering_config = self.sport_config.get('feature_engineering', {})
        
        # Set up stat-specific parameters
        self.stats_config = self.sport_config.get('stats', {})
        
    def preprocess_data(self, data: Dict[str, Any]) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
        """
        Preprocess raw data for the specific sport.
        
        Args:
            data: Raw data dictionary with player stats, team stats, etc.
            
        Returns:
            Tuple of (inputs, targets) for model training/prediction
        """
        # Extract player data
        player_data = data.get('player_stats', [])
        
        # Extract team data
        team_data = data.get('team_stats', [])
        
        # Extract other relevant data
        injuries = data.get('injuries', [])
        odds = data.get('odds', [])
        schedules = data.get('schedules', [])
        weather = data.get('weather', []) if not self.sport_config.get('is_indoor', False) else []
        
        # Process and engineer features
        static_features, sequence_features, entity_ids, targets = self._engineer_features(
            player_data, team_data, injuries, odds, schedules, weather
        )
        
        # Prepare inputs dictionary
        inputs = {}
        
        if static_features is not None:
            inputs['static'] = static_features
            
        if sequence_features is not None:
            inputs['sequence'] = sequence_features
            
        # Add entity IDs for embeddings
        for key, value in entity_ids.items():
            inputs[key] = value
            
        return inputs, targets
    
    def _engineer_features(
        self, 
        player_data: List[Dict[str, Any]], 
        team_data: List[Dict[str, Any]],
        injuries: List[Dict[str, Any]],
        odds: List[Dict[str, Any]],
        schedules: List[Dict[str, Any]],
        weather: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, np.ndarray], Dict[str, np.ndarray]]:
        """
        Engineer features for the specific sport.
        
        Args:
            player_data: List of player statistics
            team_data: List of team statistics
            injuries: List of injury reports
            odds: List of betting odds
            schedules: List of game schedules
            weather: List of weather data (for outdoor sports)
            
        Returns:
            Tuple of (static_features, sequence_features, entity_ids, targets)
        """
        # This is a placeholder implementation
        # In a real implementation, this would process the data and create features
        
        # Example static features (would be calculated from the input data)
        static_features = np.random.random((len(player_data), 20))
        
        # Example sequence features (would be calculated from historical data)
        sequence_length = self.config.get('sequence_length', 10)
        sequence_features = np.random.random((len(player_data), sequence_length, 15))
        
        # Example entity IDs
        entity_ids = {
            'player_id': np.array([[i % 1000] for i in range(len(player_data))]),
            'team_id': np.array([[i % 30] for i in range(len(player_data))]),
            'opponent_id': np.array([[i % 30] for i in range(len(player_data))]),
            'sport_id': np.array([[self._get_sport_id()] for _ in range(len(player_data))])
        }
        
        # Example targets
        targets = {
            'regression_output': np.random.random((len(player_data), 1)) * 30,  # Example stat values
            'classification_output': np.random.randint(0, 2, (len(player_data), 1))  # Binary over/under
        }
        
        return static_features, sequence_features, entity_ids, targets
    
    def _get_sport_id(self) -> int:
        """
        Get the numeric ID for the current sport.
        
        Returns:
            Sport ID as integer
        """
        sport_mapping = {
            'nba': 0,
            'nfl': 1,
            'mlb': 2,
            'nhl': 3,
            'soccer': 4
        }
        
        return sport_mapping.get(self.sport_name, 0)
    
    def build_model(self) -> Model:
        """
        Build the model with sport-specific input shapes.
        
        Returns:
            Compiled Keras model
        """
        # Define input shapes based on sport-specific requirements
        input_shapes = self._get_input_shapes()
        
        # Build the model using the base model
        model = self.base_model.build_model(input_shapes)
        
        return model
    
    def _get_input_shapes(self) -> Dict[str, Any]:
        """
        Get input shapes for the specific sport.
        
        Returns:
            Dictionary of input shapes
        """
        # Static features shape (number of features depends on the sport)
        static_shape = (self.sport_config.get('num_static_features', 20),)
        
        # Sequence features shape
        sequence_length = self.config.get('sequence_length', 10)
        sequence_features = self.sport_config.get('num_sequence_features', 15)
        sequence_shape = (sequence_length, sequence_features)
        
        # Define input shapes
        input_shapes = {
            'static': static_shape,
            'sequence': sequence_shape,
            'player_id': (1,),
            'team_id': (1,),
            'opponent_id': (1,),
            'sport_id': (1,),
            'line': (1,)
        }
        
        return input_shapes
    
    def train(self, train_data: Dict[str, Any], validation_data: Optional[Dict[str, Any]] = None, 
              epochs: int = 100, batch_size: int = 64) -> Dict[str, Any]:
        """
        Train the model on sport-specific data.
        
        Args:
            train_data: Training data dictionary
            validation_data: Validation data dictionary
            epochs: Number of training epochs
            batch_size: Batch size for training
            
        Returns:
            Training history
        """
        # Preprocess training data
        train_inputs, train_targets = self.preprocess_data(train_data)
        
        # Preprocess validation data if provided
        val_inputs, val_targets = None, None
        if validation_data is not None:
            val_inputs, val_targets = self.preprocess_data(validation_data)
        
        # Build the model if not already built
        if self.base_model.model is None:
            self.build_model()
        
        # Train the model
        history = self.base_model.model.fit(
            train_inputs,
            train_targets,
            validation_data=(val_inputs, val_targets) if val_inputs is not None else None,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=self._get_callbacks()
        )
        
        return history.history
    
    def _get_callbacks(self) -> List[tf.keras.callbacks.Callback]:
        """
        Get training callbacks for the model.
        
        Returns:
            List of Keras callbacks
        """
        callbacks = []
        
        # Early stopping
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=self.config.get('early_stopping_patience', 10),
            restore_best_weights=True
        )
        callbacks.append(early_stopping)
        
        # Model checkpoint
        checkpoint = tf.keras.callbacks.ModelCheckpoint(
            filepath=f'models/{self.sport_name}_model_best.h5',
            monitor='val_loss',
            save_best_only=True
        )
        callbacks.append(checkpoint)
        
        # Learning rate scheduler
        lr_scheduler = tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6
        )
        callbacks.append(lr_scheduler)
        
        # TensorBoard logging
        tensorboard = tf.keras.callbacks.TensorBoard(
            log_dir=f'logs/{self.sport_name}_{datetime.now().strftime("%Y%m%d-%H%M%S")}',
            histogram_freq=1
        )
        callbacks.append(tensorboard)
        
        return callbacks
    
    def predict(self, data: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """
        Make predictions using the trained model.
        
        Args:
            data: Data dictionary with features
            
        Returns:
            Dictionary with regression and classification predictions
        """
        # Preprocess data
        inputs, _ = self.preprocess_data(data)
        
        # Ensure model is built
        if self.base_model.model is None:
            raise ValueError("Model has not been built or trained yet.")
        
        # Make predictions
        regression_pred, classification_pred = self.base_model.model.predict(inputs)
        
        # Return predictions
        return {
            'regression': regression_pred,
            'classification': classification_pred
        }
    
    def evaluate(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Evaluate the model on test data.
        
        Args:
            data: Test data dictionary
            
        Returns:
            Dictionary with evaluation metrics
        """
        # Preprocess data
        inputs, targets = self.preprocess_data(data)
        
        # Ensure model is built
        if self.base_model.model is None:
            raise ValueError("Model has not been built or trained yet.")
        
        # Evaluate model
        results = self.base_model.model.evaluate(inputs, targets, return_dict=True)
        
        return results
    
    def save_model(self, filepath: str) -> None:
        """
        Save the model to disk.
        
        Args:
            filepath: Path to save the model
        """
        self.base_model.save_model(filepath)
        
    def load_model(self, filepath: str) -> None:
        """
        Load the model from disk.
        
        Args:
            filepath: Path to load the model from
        """
        self.base_model.load_model(filepath)
