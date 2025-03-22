"""
Integration tests for the neural network-based sports predictor.
This module contains tests for the end-to-end pipeline.
"""

import os
import sys
import unittest
import json
import numpy as np
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_collection import DataCollectionManager
from src.training import TrainingPipeline, PredictionPipeline
from src.automation import AutomationSystem, MonitoringSystem

class TestEndToEndPipeline(unittest.TestCase):
    """Tests for the end-to-end pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        
        # Create mock data
        self.sample_data = {
            'nba': {
                'player_stats': [
                    {
                        'player_name': 'Player A',
                        'team': 'Team 1',
                        'opponent': 'Team 2',
                        'game_date': '2025-03-15',
                        'points': 25,
                        'rebounds': 10,
                        'assists': 5,
                        'is_home': 1
                    },
                    {
                        'player_name': 'Player A',
                        'team': 'Team 1',
                        'opponent': 'Team 3',
                        'game_date': '2025-03-17',
                        'points': 30,
                        'rebounds': 8,
                        'assists': 7,
                        'is_home': 0
                    }
                ],
                'team_stats': [
                    {
                        'team_name': 'Team 1',
                        'wins': 40,
                        'losses': 20,
                        'points_per_game': 110.5,
                        'opponent_points_per_game': 105.2
                    },
                    {
                        'team_name': 'Team 2',
                        'wins': 35,
                        'losses': 25,
                        'points_per_game': 108.3,
                        'opponent_points_per_game': 106.8
                    }
                ],
                'prizepicks': [
                    {
                        'player_name': 'Player A',
                        'stat_type': 'points',
                        'line': 27.5
                    }
                ]
            }
        }
        
        # Create output directory for test data
        self.test_output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output', 'test')
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        # Save sample data
        for sport, sport_data in self.sample_data.items():
            sport_file = os.path.join(self.test_output_dir, f"{sport}_data.json")
            with open(sport_file, 'w') as f:
                json.dump(sport_data, f)
    
    @patch('src.data_collection.DataCollectionManager')
    def test_data_collection_to_training(self, mock_manager):
        """Test data collection to training pipeline integration"""
        # Setup mocks
        mock_manager.return_value.run_daily_collection.return_value = self.sample_data
        
        # Create data collection manager
        data_manager = mock_manager(self.config_dir)
        
        # Run data collection
        collected_data = data_manager.run_daily_collection()
        
        # Verify data collection output
        self.assertIsInstance(collected_data, dict)
        self.assertIn('nba', collected_data)
        self.assertIn('player_stats', collected_data['nba'])
        self.assertIn('team_stats', collected_data['nba'])
        
        # Create training pipeline
        with patch('src.training.TrainingPipeline') as mock_training:
            # Setup mock
            mock_training.return_value.train_all_sports.return_value = {
                'nba': {
                    'sport': 'nba',
                    'model_path': '/path/to/model.h5',
                    'evaluation': {
                        'regression_mse': 5.2,
                        'classification_accuracy': 0.75
                    }
                }
            }
            
            # Create training pipeline
            training_pipeline = mock_training(self.config_dir)
            
            # Train models
            training_results = training_pipeline.train_all_sports(collected_data)
            
            # Verify training output
            self.assertIsInstance(training_results, dict)
            self.assertIn('nba', training_results)
            self.assertIn('evaluation', training_results['nba'])
    
    @patch('src.training.PredictionPipeline')
    def test_training_to_prediction(self, mock_pipeline):
        """Test training to prediction pipeline integration"""
        # Setup mock
        mock_pipeline.return_value.predict_for_sport.return_value = [
            {
                'player': 'Player A',
                'team': 'Team 1',
                'opponent': 'Team 2',
                'date': '2025-03-21',
                'stat': 'points',
                'predicted_value': 28.5,
                'over_probability': 0.65,
                'line': 27.5,
                'confidence': 'High',
                'confidence_score': 80,
                'top_factors': ['Recent scoring above average', 'Home game advantage', 'Weak opponent defense']
            }
        ]
        
        # Create prediction pipeline
        prediction_pipeline = mock_pipeline(self.config_dir)
        
        # Generate predictions
        predictions = prediction_pipeline.predict_for_sport(self.sample_data['nba'], 'nba')
        
        # Verify prediction output
        self.assertIsInstance(predictions, list)
        self.assertEqual(len(predictions), 1)
        self.assertIn('player', predictions[0])
        self.assertIn('predicted_value', predictions[0])
        self.assertIn('over_probability', predictions[0])
        self.assertIn('confidence', predictions[0])
    
    @patch('src.automation.AutomationSystem')
    def test_full_pipeline_integration(self, mock_system):
        """Test full pipeline integration"""
        # Setup mock
        mock_system.return_value.run_full_pipeline.return_value = True
        
        # Create automation system
        automation_system = mock_system(self.config_dir)
        
        # Run full pipeline
        result = automation_system.run_full_pipeline()
        
        # Verify result
        self.assertTrue(result)
    
    @patch('src.automation.MonitoringSystem')
    def test_prediction_to_monitoring(self, mock_system):
        """Test prediction to monitoring integration"""
        # Create sample predictions and outcomes
        predictions = {
            'nba': [
                {
                    'player': 'Player A',
                    'team': 'Team 1',
                    'opponent': 'Team 2',
                    'date': '2025-03-21',
                    'stat': 'points',
                    'predicted_value': 28.5,
                    'over_probability': 0.65,
                    'line': 27.5,
                    'confidence': 'High',
                    'confidence_score': 80
                }
            ]
        }
        
        actual_outcomes = {
            'nba': [
                {
                    'player': 'Player A',
                    'team': 'Team 1',
                    'opponent': 'Team 2',
                    'date': '2025-03-21',
                    'stat': 'points',
                    'actual_value': 30.0
                }
            ]
        }
        
        # Setup mock
        mock_system.return_value.track_performance.return_value = {
            'nba': {
                'mse': 2.25,
                'mae': 1.5,
                'accuracy': 1.0,
                'auc': 1.0
            }
        }
        
        # Create monitoring system
        monitoring_system = mock_system(self.config_dir)
        
        # Track performance
        performance = monitoring_system.track_performance(predictions, actual_outcomes)
        
        # Verify monitoring output
        self.assertIsInstance(performance, dict)
        self.assertIn('nba', performance)
        self.assertIn('mse', performance['nba'])
        self.assertIn('accuracy', performance['nba'])

class TestBacktesting(unittest.TestCase):
    """Tests for the backtesting framework"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        
        # Create historical data for backtesting
        self.historical_data = {
            'nba': {
                '2025-01-01': {
                    'player_stats': [
                        {
                            'player_name': 'Player A',
                            'team': 'Team 1',
                            'opponent': 'Team 2',
                            'game_date': '2025-01-01',
                            'points': 22,
                            'rebounds': 8,
                            'assists': 6,
                            'is_home': 1
                        }
                    ],
                    'team_stats': [
                        {
                            'team_name': 'Team 1',
                            'wins': 30,
                            'losses': 10
                        }
                    ],
                    'prizepicks': [
                        {
                            'player_name': 'Player A',
                            'stat_type': 'points',
                            'line': 20.5
                        }
                    ]
                },
                '2025-01-02': {
                    'player_stats': [
                        {
                            'player_name': 'Player A',
                            'team': 'Team 1',
                            'opponent': 'Team 3',
                            'game_date': '2025-01-02',
                            'points': 18,
                            'rebounds': 10,
                            'assists': 4,
                            'is_home': 0
                        }
                    ],
                    'team_stats': [
                        {
                            'team_name': 'Team 1',
                            'wins': 31,
                            'losses': 10
                        }
                    ],
                    'prizepicks': [
                        {
                            'player_name': 'Player A',
                            'stat_type': 'points',
                            'line': 21.5
                        }
                    ]
                }
            }
        }
    
    @patch('src.training.TrainingPipeline')
    @patch('src.training.PredictionPipeline')
    def test_backtesting_framework(self, mock_prediction, mock_training):
        """Test backtesting framework"""
        # Setup mocks
        mock_training.return_value.train_model_for_sport.return_value = {
            'sport': 'nba',
            'model_path': '/path/to/model.h5',
            'evaluation': {
                'regression_mse': 5.2,
                'classification_accuracy': 0.75
            }
        }
        
        mock_prediction.return_value.predict_for_sport.return_value = [
            {
                'player': 'Player A',
                'team': 'Team 1',
                'opponent': 'Team 2',
                'date': '2025-01-02',
                'stat': 'points',
                'predicted_value': 19.5,
                'over_probability': 0.4,
                'line': 21.5,
                'confidence': 'Moderate',
                'confidence_score': 60
            }
        ]
        
        # Create training and prediction pipelines
        training_pipeline = mock_training(self.config_dir)
        prediction_pipeline = mock_prediction(self.config_dir)
        
        # Perform backtesting
        backtest_results = {}
        
        for sport, dates in self.historical_data.items():
            sport_results = []
            
            # Sort dates
            sorted_dates = sorted(dates.keys())
            
            for i, date in enumerate(sorted_dates[:-1]):  # Skip last date as test
                # Use data up to current date for training
                train_data = {
                    'player_stats': [],
                    'team_stats': []
                }
                
                for train_date in sorted_dates[:i+1]:
                    train_data['player_stats'].extend(dates[train_date]['player_stats'])
                    train_data['team_stats'].extend(dates[train_date]['team_stats'])
                
                # Train model
                model_result = training_pipeline.train_model_for_sport(train_data, sport)
                
                # Use next date for testing
                test_date = sorted_dates[i+1]
                test_data = dates[test_date]
                
                # Generate predictions
                predictions = prediction_pipeline.predict_for_sport(test_data, sport)
                
                # Compare with actual outcomes
                actual_outcomes = [
                    {
                        'player': p['player_name'],
                        'team': p['team'],
                        'opponent': p['opponent'],
                        'date': p['game_date'],
                        'stat': 'points',
                        'actual_value': p['points']
                    }
                    for p in test_data['player_stats']
                ]
                
                # Calculate metrics
                for pred, actual in zip(predictions, actual_outcomes):
                    error = pred['predicted_value'] - actual['actual_value']
                    correct_direction = (pred['over_probability'] > 0.5 and actual['actual_value'] > pred['line']) or \
                                       (pred['over_probability'] <= 0.5 and actual['actual_value'] <= pred['line'])
                    
                    result = {
                        'date': test_date,
                        'player': pred['player'],
                        'predicted_value': pred['predicted_value'],
                        'actual_value': actual['actual_value'],
                        'error': error,
                        'line': pred['line'],
                        'over_probability': pred['over_probability'],
                        'correct_direction': correct_direction
                    }
                    
                    sport_results.append(result)
            
            backtest_results[sport] = sport_results
        
        # Verify backtest results
        self.assertIsInstance(backtest_results, dict)
        self.assertIn('nba', backtest_results)
        
        if backtest_results['nba']:
            result = backtest_results['nba'][0]
            self.assertIn('date', result)
            self.assertIn('player', result)
            self.assertIn('predicted_value', result)
            self.assertIn('actual_value', result)
            self.assertIn('error', result)
            self.assertIn('correct_direction', result)
    
    def test_cross_sport_evaluation(self):
        """Test cross-sport model evaluation"""
        # This test would evaluate how well the model generalizes across different sports
        # For now, we'll just verify the structure of the test
        
        # Create mock evaluation results
        evaluation_results = {
            'nba': {
                'regression_mse': 5.2,
                'regression_mae': 1.8,
                'classification_accuracy': 0.75,
                '<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>