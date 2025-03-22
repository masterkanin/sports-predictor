"""
Prediction pipeline module for the neural network-based sports predictor.
This module handles generating predictions for upcoming games and PrizePicks lines.
"""

import os
import json
import numpy as np
import pandas as pd
import tensorflow as tf
from typing import Dict, List, Tuple, Any, Optional, Union
from datetime import datetime, timedelta
import logging

from ..models import SportSpecificModel, MultiSportNormalizer, FeatureEngineer, UncertaintyEstimator

class PredictionPipeline:
    """
    Pipeline for generating predictions using the trained sports prediction model.
    Handles data preparation, prediction generation, and uncertainty estimation.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the prediction pipeline.
        
        Args:
            config_path: Path to the configuration directory
        """
        self.config_dir = config_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                     'config')
        
        # Load prediction configuration
        pipeline_config_path = os.path.join(self.config_dir, 'pipeline', 'prediction.json')
        with open(pipeline_config_path, 'r') as f:
            self.config = json.load(f)
            
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.normalizer = MultiSportNormalizer(self.config_dir)
        self.feature_engineer = FeatureEngineer(self.config.get('feature_engineering', {}))
        
        # Initialize sport-specific models
        self.models = {}
        self.ensembles = {}
        self.uncertainty_estimators = {}
        
        # Load trained models
        self._load_models()
        
        self.logger.info("Prediction pipeline initialized")
    
    def _setup_logging(self):
        """Set up logging configuration"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file_path', os.path.join(log_dir, 'prediction.log'))
        
        # Create logger
        self.logger = logging.getLogger('prediction_pipeline')
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
    
    def _load_models(self):
        """Load trained models for all sports"""
        model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')
        
        # Get list of supported sports
        sports_dir = os.path.join(self.config_dir, 'sports')
        sports = [f.split('.')[0] for f in os.listdir(sports_dir) if f.endswith('.json')]
        
        for sport in sports:
            try:
                # Load main model
                model_path = os.path.join(model_dir, f"{sport}_model.h5")
                if os.path.exists(model_path):
                    # Create sport-specific model
                    model_config = self.config.get('model', {})
                    model_config['sports_config'] = {sport: self.config.get('sports_config', {}).get(sport, {})}
                    
                    sport_model = SportSpecificModel(sport, model_config)
                    sport_model.load_model(model_path)
                    self.models[sport] = sport_model
                    
                    # Create uncertainty estimator
                    uncertainty_config = self.config.get('uncertainty', {})
                    self.uncertainty_estimators[sport] = UncertaintyEstimator(
                        sport_model.base_model.model, 
                        uncertainty_config
                    )
                    
                    self.logger.info(f"Loaded model for {sport}")
                
                # Check for ensemble models
                ensemble_models = []
                i = 0
                while True:
                    ensemble_path = os.path.join(model_dir, f"{sport}_ensemble_model_{i}.h5")
                    if os.path.exists(ensemble_path):
                        ensemble_model = SportSpecificModel(sport, model_config)
                        ensemble_model.load_model(ensemble_path)
                        ensemble_models.append(ensemble_model)
                        i += 1
                    else:
                        break
                
                if ensemble_models:
                    self.ensembles[sport] = ensemble_models
                    self.logger.info(f"Loaded ensemble of {len(ensemble_models)} models for {sport}")
                
            except Exception as e:
                self.logger.error(f"Error loading model for {sport}: {str(e)}")
    
    def prepare_prediction_data(self, data: Dict[str, Any], sport: str) -> Dict[str, Any]:
        """
        Prepare data for prediction.
        
        Args:
            data: Raw data dictionary with player stats, team stats, etc.
            sport: Sport name (e.g., 'nba', 'nfl')
            
        Returns:
            Processed data ready for prediction
        """
        self.logger.info(f"Preparing prediction data for {sport}")
        
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
        processed_data = {
            'player_stats': combined_df.to_dict('records'),
            'team_stats': team_df.to_dict('records')
        }
        
        return processed_data
    
    def predict_for_sport(self, data: Dict[str, Any], sport: str) -> List[Dict[str, Any]]:
        """
        Generate predictions for a specific sport.
        
        Args:
            data: Raw data dictionary with player stats, team stats, etc.
            sport: Sport name (e.g., 'nba', 'nfl')
            
        Returns:
            List of predictions with uncertainty estimates
        """
        self.logger.info(f"Generating predictions for {sport}")
        
        if sport not in self.models:
            self.logger.error(f"No model available for {sport}")
            return []
        
        # Prepare data
        processed_data = self.prepare_prediction_data(data, sport)
        
        # Get model
        model = self.models[sport]
        
        # Generate predictions
        predictions = model.predict(processed_data)
        
        # Get uncertainty estimates
        uncertainty_estimator = self.uncertainty_estimators.get(sport)
        if uncertainty_estimator:
            uncertainty = uncertainty_estimator.monte_carlo_dropout(processed_data)
            
            # Calculate confidence scores
            confidence_scores = uncertainty_estimator.confidence_score(uncertainty)
            confidence_categories = uncertainty_estimator.categorize_confidence(confidence_scores)
        else:
            # Default uncertainty if no estimator available
            uncertainty = {
                'regression_std': np.ones_like(predictions['regression']) * 0.1,
                'classification_std': np.ones_like(predictions['classification']) * 0.1
            }
            confidence_scores = np.ones_like(predictions['regression']) * 50
            confidence_categories = ['Moderate'] * len(predictions['regression'])
        
        # Use ensemble if available
        if sport in self.ensembles and self.ensembles[sport]:
            ensemble_predictions = []
            for ensemble_model in self.ensembles[sport]:
                ensemble_pred = ensemble_model.predict(processed_data)
                ensemble_predictions.append((ensemble_pred['regression'], ensemble_pred['classification']))
            
            # Average ensemble predictions
            ensemble_regression = np.mean([p[0] for p in ensemble_predictions], axis=0)
            ensemble_classification = np.mean([p[1] for p in ensemble_predictions], axis=0)
            
            # Blend with main model predictions (optional)
            blend_weight = self.config.get('ensemble_blend_weight', 0.5)
            predictions['regression'] = (1 - blend_weight) * predictions['regression'] + blend_weight * ensemble_regression
            predictions['classification'] = (1 - blend_weight) * predictions['classification'] + blend_weight * ensemble_classification
        
        # Format predictions
        formatted_predictions = []
        
        player_data = processed_data.get('player_stats', [])
        prizepicks_data = data.get('prizepicks', [])
        
        for i, player in enumerate(player_data):
            # Get PrizePicks line if available
            line = None
            for pp in prizepicks_data:
                if pp.get('player_name') == player.get('player_name') and pp.get('stat_type') == player.get('stat_type'):
                    line = pp.get('line')
                    break
            
            prediction = {
                'player': player.get('player_name', f"Player_{i}"),
                'team': player.get('team', ''),
                'opponent': player.get('opponent', ''),
                'date': player.get('game_date', datetime.now().strftime('%Y-%m-%d')),
                'stat': player.get('stat_type', 'points'),
                'predicted_value': float(predictions['regression'][i][0]),
                'over_probability': float(predictions['classification'][i][0]),
                'line': line,
                'confidence': confidence_categories[i],
                'confidence_score': float(confidence_scores[i]),
                'prediction_range': [
                    float(predictions['regression'][i][0] - uncertainty['regression_std'][i][0]),
                    float(predictions['regression'][i][0] + uncertainty['regression_std'][i][0])
                ]
            }
            
            # Add top factors if available
            if 'top_factors' in player:
                prediction['top_factors'] = player['top_factors']
            else:
                # Generate some placeholder factors based on features
                prediction['top_factors'] = self._generate_top_factors(player, prediction)
            
            formatted_predictions.append(prediction)
        
        self.logger.info(f"Generated {len(formatted_predictions)} predictions for {sport}")
        return formatted_predictions
    
    def _generate_top_factors(self, player: Dict[str, Any], prediction: Dict[str, Any]) -> List[str]:
        """
        Generate top factors that influenced the prediction.
        
        Args:
            player: Player data
            prediction: Prediction data
            
        Returns:
            List of top factors
        """
        factors = []
        
        # Check recent form
        if 'points_rolling_5' in player and player['points_rolling_5'] > prediction['predicted_value']:
            factors.append("Recent scoring below average")
        elif 'points_rolling_5' in player and player['points_rolling_5'] < prediction['predicted_value']:
            factors.append("Recent scoring above average")
        
        # Check home/away
        if 'is_home' in player and player['is_home'] == 1:
            factors.append("Home game advantage")
        elif 'is_home' in player and player['is_home'] == 0:
            factors.append("Away game factor")
        
        # Check rest days
        if 'days_rest' in player and player['days_rest'] <= 1:
            factors.append("Playing on short rest")
        elif 'days_rest' in player and player['days_rest'] >= 3:
            factors.append("Well-rested player")
        
        # Check opponent strength
        if 'opponent_team_defensive_rating_rolling_5' in player:
            if player['opponent_team_defensive_rating_rolling_5'] > 0:
                factors.append("Weak opponent defense")
            else:
                factors.append("Strong opponent defense")
        
        # Ensure we have at least 3 factors
        default_factors = [
            "Historical performance trend",
            "Matchup analysis",
            "Recent usage rate"
        ]
        
        while len(factors) < 3:
            if default_factors:
                factors.append(default_factors.pop(0))
            else:
                break
        
        return factors[:3]  # Return top 3 factors
    
    def predict_for_all_sports(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate predictions for all sports.
        
        Args:
            data: Dictionary mapping sport names to data dictionaries
            
        Returns:
            Dictionary mapping sport names to prediction lists
        """
        self.logger.info("Generating predictions for all sports")
        
        results = {}
        
        for sport, sport_data in data.items():
            try:
                sport_predictions = self.predict_for_sport(sport_data, sport)
                results[sport] = sport_predictions
            except Exception as e:
                self.logger.error(f"Error generating predictions for {sport}: {str(e)}")
                results[sport] = []
        
        return results
    
    def generate_daily_predictions(self, date: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate predictions for all sports for a specific date.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to today)
            
        Returns:
            Dictionary mapping sport names to prediction lists
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        self.logger.info(f"Generating daily predictions for {date}")
        
        # This would typically load the latest data for the specified date
        # For demonstration, we'll return a placeholder
        
        self.logger.warning("Daily prediction generation requires actual data collection")
        return {}
    
    def save_predictions(self, predictions: Dict[str, List[Dict[str, Any]]], date: str = None) -> str:
        """
        Save predictions to a file.
        
        Args:
            predictions: Dictionary mapping sport names to prediction lists
            date: Date string in format 'YYYY-MM-DD' (defaults to today)
            
        Returns:
            Path to the saved predictions file
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        self.logger.info(f"Saving predictions for {date}")
        
        # Create output directory
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output', 'predictions')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save predictions to JSON file
        output_path = os.path.join(output_dir<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>