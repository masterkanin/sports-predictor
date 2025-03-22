"""
Base neural network architecture module for the sports prediction system.
This module defines the core architecture components that will be used across all sports.
"""

import tensorflow as tf
from tensorflow.keras import layers, Model, regularizers
from tensorflow.keras.optimizers import Adam
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union

class SportsPredictorModel:
    """
    Neural network architecture for sports prediction with dual-task learning.
    Handles both regression (exact stat prediction) and classification (over/under probability).
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the sports predictor model.
        
        Args:
            config: Configuration dictionary with model parameters
        """
        self.config = config
        self.sport_embeddings = {}
        self.player_embeddings = {}
        self.team_embeddings = {}
        self.model = None
        
        # Extract key configuration parameters
        self.embedding_dim = config.get('embedding_dim', 32)
        self.lstm_units = config.get('lstm_units', 64)
        self.dropout_rate = config.get('dropout_rate', 0.2)
        self.l2_reg = config.get('l2_reg', 0.001)
        self.sequence_length = config.get('sequence_length', 10)
        
        # Set up sport-specific configurations
        self.sports_config = config.get('sports_config', {})
        
    def build_model(self, input_shapes: Dict[str, Any]) -> Model:
        """
        Build the neural network model architecture.
        
        Args:
            input_shapes: Dictionary of input shapes for different components
            
        Returns:
            Compiled Keras model
        """
        # Define inputs
        inputs = self._create_inputs(input_shapes)
        
        # Process different types of inputs
        processed_inputs = []
        
        # Process static features
        if 'static' in inputs:
            static_features = self._process_static_features(inputs['static'])
            processed_inputs.append(static_features)
        
        # Process sequential features
        if 'sequence' in inputs:
            sequence_features = self._process_sequence_features(inputs['sequence'])
            processed_inputs.append(sequence_features)
        
        # Process embeddings
        embedding_features = self._process_embeddings(inputs)
        if embedding_features is not None:
            processed_inputs.append(embedding_features)
        
        # Combine all processed inputs
        if len(processed_inputs) > 1:
            combined_features = layers.Concatenate()(processed_inputs)
        else:
            combined_features = processed_inputs[0]
        
        # Shared layers
        shared_representation = self._build_shared_layers(combined_features)
        
        # Output heads
        regression_output = self._build_regression_head(shared_representation)
        classification_output = self._build_classification_head(shared_representation)
        
        # Create model
        model = Model(
            inputs=[v for v in inputs.values()],
            outputs=[regression_output, classification_output]
        )
        
        # Compile model with appropriate loss functions and metrics
        model.compile(
            optimizer=Adam(learning_rate=self.config.get('learning_rate', 0.001)),
            loss={
                'regression_output': 'mean_squared_error',
                'classification_output': 'binary_crossentropy'
            },
            loss_weights={
                'regression_output': self.config.get('regression_loss_weight', 0.5),
                'classification_output': self.config.get('classification_loss_weight', 0.5)
            },
            metrics={
                'regression_output': ['mae', 'mse'],
                'classification_output': ['accuracy', 'AUC']
            }
        )
        
        self.model = model
        return model
    
    def _create_inputs(self, input_shapes: Dict[str, Any]) -> Dict[str, tf.Tensor]:
        """
        Create input layers for the model.
        
        Args:
            input_shapes: Dictionary of input shapes for different components
            
        Returns:
            Dictionary of input tensors
        """
        inputs = {}
        
        # Static features input
        if 'static' in input_shapes:
            inputs['static'] = layers.Input(shape=input_shapes['static'], name='static_input')
        
        # Sequential features input
        if 'sequence' in input_shapes:
            inputs['sequence'] = layers.Input(shape=input_shapes['sequence'], name='sequence_input')
        
        # Player ID input for embeddings
        if 'player_id' in input_shapes:
            inputs['player_id'] = layers.Input(shape=(1,), name='player_id_input', dtype='int32')
        
        # Team ID input for embeddings
        if 'team_id' in input_shapes:
            inputs['team_id'] = layers.Input(shape=(1,), name='team_id_input', dtype='int32')
        
        # Opponent ID input for embeddings
        if 'opponent_id' in input_shapes:
            inputs['opponent_id'] = layers.Input(shape=(1,), name='opponent_id_input', dtype='int32')
        
        # Sport ID input for embeddings
        if 'sport_id' in input_shapes:
            inputs['sport_id'] = layers.Input(shape=(1,), name='sport_id_input', dtype='int32')
        
        # PrizePicks line input
        if 'line' in input_shapes:
            inputs['line'] = layers.Input(shape=(1,), name='line_input')
        
        return inputs
    
    def _process_static_features(self, static_input: tf.Tensor) -> tf.Tensor:
        """
        Process static features through feedforward layers.
        
        Args:
            static_input: Input tensor for static features
            
        Returns:
            Processed static features
        """
        x = static_input
        
        # Apply batch normalization to standardize inputs
        x = layers.BatchNormalization()(x)
        
        # Feedforward layers with regularization
        for units in self.config.get('static_layer_units', [128, 64]):
            x = layers.Dense(
                units,
                activation='relu',
                kernel_regularizer=regularizers.l2(self.l2_reg)
            )(x)
            x = layers.BatchNormalization()(x)
            x = layers.Dropout(self.dropout_rate)(x)
        
        return x
    
    def _process_sequence_features(self, sequence_input: tf.Tensor) -> tf.Tensor:
        """
        Process sequential features through LSTM or Transformer layers.
        
        Args:
            sequence_input: Input tensor for sequential features
            
        Returns:
            Processed sequence features
        """
        x = sequence_input
        
        # Apply batch normalization to standardize inputs
        x = layers.BatchNormalization()(x)
        
        # Choose between LSTM and Transformer based on configuration
        if self.config.get('sequence_model_type', 'lstm').lower() == 'transformer':
            x = self._build_transformer_encoder(x)
        else:
            # Default to LSTM
            x = self._build_lstm_layers(x)
        
        return x
    
    def _build_lstm_layers(self, sequence_input: tf.Tensor) -> tf.Tensor:
        """
        Build LSTM layers for sequence processing.
        
        Args:
            sequence_input: Input tensor for sequential features
            
        Returns:
            Processed sequence features
        """
        x = sequence_input
        
        # Bidirectional LSTM layers
        for i, units in enumerate(self.config.get('lstm_layer_units', [self.lstm_units])):
            return_sequences = i < len(self.config.get('lstm_layer_units', [self.lstm_units])) - 1
            x = layers.Bidirectional(
                layers.LSTM(
                    units,
                    return_sequences=return_sequences,
                    dropout=self.dropout_rate,
                    recurrent_dropout=0,  # Set to 0 for better GPU performance
                    kernel_regularizer=regularizers.l2(self.l2_reg)
                )
            )(x)
            
            if return_sequences:
                x = layers.BatchNormalization()(x)
        
        return x
    
    def _build_transformer_encoder(self, sequence_input: tf.Tensor) -> tf.Tensor:
        """
        Build Transformer encoder for sequence processing.
        
        Args:
            sequence_input: Input tensor for sequential features
            
        Returns:
            Processed sequence features
        """
        x = sequence_input
        
        # Get transformer parameters from config
        num_heads = self.config.get('transformer_num_heads', 4)
        ff_dim = self.config.get('transformer_ff_dim', 128)
        num_transformer_blocks = self.config.get('num_transformer_blocks', 2)
        
        # Apply positional encoding
        x = self._add_positional_encoding(x)
        
        # Apply transformer blocks
        for _ in range(num_transformer_blocks):
            x = self._transformer_encoder_block(x, num_heads, ff_dim)
        
        # Global average pooling to get a fixed-size representation
        x = layers.GlobalAveragePooling1D()(x)
        
        return x
    
    def _add_positional_encoding(self, x: tf.Tensor) -> tf.Tensor:
        """
        Add positional encoding to the input for transformer.
        
        Args:
            x: Input tensor
            
        Returns:
            Input with positional encoding added
        """
        seq_length = tf.shape(x)[1]
        feature_size = tf.shape(x)[2]
        
        # Create positional encoding
        positions = tf.range(start=0, limit=seq_length, delta=1, dtype=tf.float32)
        positions = tf.expand_dims(positions, axis=1)
        
        # Calculate the positional encoding
        div_term = tf.exp(
            tf.range(start=0, limit=feature_size, delta=2, dtype=tf.float32) *
            (-tf.math.log(10000.0) / feature_size)
        )
        
        # Create the positional encoding matrix
        pos_encoding = tf.zeros((seq_length, feature_size))
        
        # Set the values
        indices = tf.range(start=0, limit=feature_size, delta=2)
        updates_sin = tf.sin(positions * div_term)
        pos_encoding = tf.tensor_scatter_nd_update(
            pos_encoding,
            tf.stack([tf.repeat(tf.range(seq_length), tf.size(indices)), tf.tile(indices, [seq_length])], axis=1),
            tf.reshape(updates_sin, [-1])
        )
        
        indices = tf.range(start=1, limit=feature_size, delta=2)
        updates_cos = tf.cos(positions * div_term)
        pos_encoding = tf.tensor_scatter_nd_update(
            pos_encoding,
            tf.stack([tf.repeat(tf.range(seq_length), tf.size(indices)), tf.tile(indices, [seq_length])], axis=1),
            tf.reshape(updates_cos, [-1])
        )
        
        # Add the positional encoding to the input
        pos_encoding = tf.expand_dims(pos_encoding, axis=0)
        x = x + pos_encoding
        
        return x
    
    def _transformer_encoder_block(self, x: tf.Tensor, num_heads: int, ff_dim: int) -> tf.Tensor:
        """
        Build a transformer encoder block.
        
        Args:
            x: Input tensor
            num_heads: Number of attention heads
            ff_dim: Feed-forward dimension
            
        Returns:
            Transformer encoder block output
        """
        # Multi-head self-attention
        attention_output = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=x.shape[-1] // num_heads
        )(x, x)
        attention_output = layers.Dropout(self.dropout_rate)(attention_output)
        
        # Add & Norm (residual connection and layer normalization)
        x1 = layers.LayerNormalization(epsilon=1e-6)(x + attention_output)
        
        # Feed-forward network
        ffn_output = layers.Dense(ff_dim, activation='relu')(x1)
        ffn_output = layers.Dense(x.shape[-1])(ffn_output)
        ffn_output = layers.Dropout(self.dropout_rate)(ffn_output)
        
        # Add & Norm (residual connection and layer normalization)
        x2 = layers.LayerNormalization(epsilon=1e-6)(x1 + ffn_output)
        
        return x2
    
    def _process_embeddings(self, inputs: Dict[str, tf.Tensor]) -> Optional[tf.Tensor]:
        """
        Process entity embeddings (player, team, opponent, sport).
        
        Args:
            inputs: Dictionary of input tensors
            
        Returns:
            Processed embedding features or None if no embeddings
        """
        embedding_outputs = []
        
        # Player embeddings
        if 'player_id' in inputs:
            player_embedding_layer = layers.Embedding(
                input_dim=self.config.get('num_players', 5000),
                output_dim=self.embedding_dim,
                embeddings_regularizer=regularizers.l2(self.l2_reg),
                name='player_embedding'
            )
            player_embedding = player_embedding_layer(inputs['player_id'])
            player_embedding = layers.Flatten()(player_embedding)
            embedding_outputs.append(player_embedding)
            
            # Store the embedding layer for later use
            self.player_embeddings['player'] = player_embedding_layer
        
        # Team embeddings
        if 'team_id' in inputs:
            team_embedding_layer = layers.Embedding(
                input_dim=self.config.get('num_teams', 100),
                output_dim=self.embedding_dim,
                embeddings_regularizer=regularizers.l2(self.l2_reg),
                name='team_embedding'
            )
            team_embedding = team_embedding_layer(inputs['team_id'])
            team_embedding = layers.Flatten()(team_embedding)
            embedding_outputs.append(team_embedding)
            
            # Store the embedding layer for later use
            self.team_embeddings['team'] = team_embedding_layer
        
        # Opponent embeddings
        if 'opponent_id' in inputs:
            opponent_embedding_layer = layers.Embedding(
                input_dim=self.config.get('num_teams', 100),
                output_dim=self.embedding_dim,
                embeddings_regularizer=regularizers.l2(self.l2_reg),
                name='opponent_embedding'
            )
            opponent_embedding = opponent_embedding_layer(inputs['opponent_id'])
            opponent_embedding = layers.Flatten()(opponent_embedding)
            embedding_outputs.append(opponent_embedding)
            
            # Store the embedding layer for later use
            self.team_embeddings['opponent'] = opponent_embedding_layer
        
        # Sport embeddings
        if 'sport_id' in inputs:
            sport_embedding_layer = layers.Embedding(
                input_dim=self.config.get('num_sports', 10),
                output_dim=self.embedding_dim,
                embeddings_regularizer=regularizers.l2(self.l2_reg),
                name='sport_embedding'
            )
            sport_embedding = sport_embedding_layer(inputs['sport_id'])
            sport_embedding = layers.Flatten()(sport_embedding)
            embedding_outputs.append(sport_embedding)
            
            # Store the embedding layer for later use
            self.sport_embeddings['sport'] = sport_embedding_layer
        
        # Combine all embeddings if any exist
        if embedding_outputs:
            combined_embeddings = layers.Concatenate()(embedding_outputs)
            return combined_embeddings
        
        return None
    
    def _build_shared_layers(self, combined_features: tf.Tensor) -> tf.Tensor:
        """
        Build shared layers for both regression and classification tasks.
        
        Args:
            co<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>