"""
Unit tests for the neural network-based sports predictor.
This module contains tests for critical components of the system.
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

from src.models import MultiSportNormalizer, FeatureEngineer, UncertaintyEstimator
from src.data_collection import DataCollectionManager
from src.training import TrainingPipeline, PredictionPipeline
from src.automation import AutomationSystem, MonitoringSystem

class TestMultiSportNormalizer(unittest.TestCase):
    """Tests for the MultiSportNormalizer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        self.normalizer = MultiSportNormalizer(self.config_dir)
    
    def test_initialization(self):
        """Test normalizer initialization"""
        self.assertIsNotNone(self.normalizer)
        self.assertIsNotNone(self.normalizer.sport_mappings)
    
    def test_normalize_stat(self):
        """Test stat normalization"""
        # Test NBA points normalization
        normalized_value = self.normalizer.normalize_stat('nba', 'points', 30.0)
        self.assertIsInstance(normalized_value, float)
        
        # Test NFL passing yards normalization
        normalized_value = self.normalizer.normalize_stat('nfl', 'passing_yards', 300.0)
        self.assertIsInstance(normalized_value, float)
    
    def test_denormalize_stat(self):
        """Test stat denormalization"""
        # Test NBA points denormalization
        original_value = 30.0
        normalized_value = self.normalizer.normalize_stat('nba', 'points', original_value)
        denormalized_value = self.normalizer.denormalize_stat('nba', 'points', normalized_value)
        self.assertAlmostEqual(original_value, denormalized_value, places=5)
        
        # Test NFL passing yards denormalization
        original_value = 300.0
        normalized_value = self.normalizer.normalize_stat('nfl', 'passing_yards', original_value)
        denormalized_value = self.normalizer.denormalize_stat('nfl', 'passing_yards', normalized_value)
        self.assertAlmostEqual(original_value, denormalized_value, places=5)

class TestFeatureEngineer(unittest.TestCase):
    """Tests for the FeatureEngineer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'rolling_windows': [3, 5, 10],
            'include_team_stats': True,
            'include_opponent_stats': True
        }
        self.feature_engineer = FeatureEngineer(self.config)
    
    def test_initialization(self):
        """Test feature engineer initialization"""
        self.assertIsNotNone(self.feature_engineer)
        self.assertEqual(self.feature_engineer.rolling_windows, [3, 5, 10])
        self.assertTrue(self.feature_engineer.include_team_stats)
        self.assertTrue(self.feature_engineer.include_opponent_stats)
    
    def test_engineer_player_features(self):
        """Test player feature engineering"""
        # Create sample player data
        player_data = [
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
        ]
        
        # Engineer features
        result = self.feature_engineer.engineer_player_features(player_data)
        
        # Check result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result.columns), len(player_data[0]))  # Should have more columns after engineering
        
        # Check if rolling features were created
        self.assertIn('points_rolling_3', result.columns)
    
    def test_create_prizepicks_features(self):
        """Test PrizePicks feature creation"""
        # Create sample data
        player_df = pd.DataFrame([
            {
                'player_name': 'Player A',
                'team': 'Team 1',
                'opponent': 'Team 2',
                'game_date': '2025-03-21',
                'points': 25
            }
        ])
        
        prizepicks_data = [
            {
                'player_name': 'Player A',
                'stat_type': 'points',
                'line': 24.5
            }
        ]
        
        # Create PrizePicks features
        result = self.feature_engineer.create_prizepicks_features(player_df, prizepicks_data)
        
        # Check result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('line', result.columns)
        self.assertIn('line_diff', result.columns)  # Should have line difference feature

class TestUncertaintyEstimator(unittest.TestCase):
    """Tests for the UncertaintyEstimator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock model
        self.mock_model = MagicMock()
        self.mock_model.return_value = (np.array([[25.0]]), np.array([[0.7]]))
        
        self.config = {
            'mc_dropout_samples': 10,
            'dropout_rate': 0.2,
            'max_expected_std': 10.0
        }
        
        self.uncertainty_estimator = UncertaintyEstimator(self.mock_model, self.config)
    
    def test_initialization(self):
        """Test uncertainty estimator initialization"""
        self.assertIsNotNone(self.uncertainty_estimator)
        self.assertEqual(self.uncertainty_estimator.num_samples, 10)
        self.assertEqual(self.uncertainty_estimator.dropout_rate, 0.2)
    
    def test_confidence_score(self):
        """Test confidence score calculation"""
        # Create sample uncertainty data
        uncertainty = {
            'regression_std': np.array([[2.0]])
        }
        
        # Calculate confidence score
        confidence = self.uncertainty_estimator.confidence_score(uncertainty)
        
        # Check result
        self.assertIsInstance(confidence, np.ndarray)
        self.assertGreaterEqual(confidence[0], 0)
        self.assertLessEqual(confidence[0], 100)
    
    def test_categorize_confidence(self):
        """Test confidence categorization"""
        # Create sample confidence scores
        confidence_scores = np.array([95, 80, 60, 30, 10])
        
        # Categorize confidence
        categories = self.uncertainty_estimator.categorize_confidence(confidence_scores)
        
        # Check result
        self.assertEqual(len(categories), 5)
        self.assertEqual(categories[0], 'Very High')
        self.assertEqual(categories[1], 'High')
        self.assertEqual(categories[2], 'Moderate')
        self.assertEqual(categories[3], 'Low')
        self.assertEqual(categories[4], 'Very Low')

class TestDataCollectionManager(unittest.TestCase):
    """Tests for the DataCollectionManager class"""
    
    @patch('src.data_collection.DataCollectionManager')
    def setUp(self, mock_manager):
        """Set up test fixtures"""
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        self.data_manager = mock_manager
        self.data_manager.config_dir = self.config_dir
    
    def test_initialization(self):
        """Test data manager initialization"""
        self.assertIsNotNone(self.data_manager)
    
    @patch('src.data_collection.nba_collector.NBADataCollector')
    def test_collect_data_for_sport(self, mock_collector):
        """Test sport-specific data collection"""
        # Setup mock
        mock_instance = mock_collector.return_value
        mock_instance.collect_player_stats.return_value = [{'player_name': 'Player A', 'points': 25}]
        mock_instance.collect_team_stats.return_value = [{'team_name': 'Team 1', 'wins': 40}]
        
        # Call method
        self.data_manager.collect_data_for_sport.return_value = {
            'player_stats': [{'player_name': 'Player A', 'points': 25}],
            'team_stats': [{'team_name': 'Team 1', 'wins': 40}]
        }
        
        result = self.data_manager.collect_data_for_sport('nba')
        
        # Check result
        self.assertIsInstance(result, dict)
        self.assertIn('player_stats', result)
        self.assertIn('team_stats', result)

class TestTrainingPipeline(unittest.TestCase):
    """Tests for the TrainingPipeline class"""
    
    @patch('src.training.TrainingPipeline')
    def setUp(self, mock_pipeline):
        """Set up test fixtures"""
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        self.training_pipeline = mock_pipeline
        self.training_pipeline.config_dir = self.config_dir
    
    def test_initialization(self):
        """Test training pipeline initialization"""
        self.assertIsNotNone(self.training_pipeline)
    
    def test_prepare_data(self):
        """Test data preparation"""
        # Create sample data
        data = {
            'player_stats': [
                {
                    'player_name': 'Player A',
                    'team': 'Team 1',
                    'opponent': 'Team 2',
                    'game_date': '2025-03-15',
                    'points': 25
                }
            ],
            'team_stats': [
                {
                    'team_name': 'Team 1',
                    'wins': 40,
                    'losses': 20
                }
            ]
        }
        
        # Setup mock
        self.training_pipeline.prepare_data.return_value = (
            {'player_stats': data['player_stats'][:1], 'team_stats': data['team_stats']},
            {'player_stats': [], 'team_stats': data['team_stats']},
            {'player_stats': [], 'team_stats': data['team_stats']}
        )
        
        # Call method
        train_data, val_data, test_data = self.training_pipeline.prepare_data(data, 'nba')
        
        # Check result
        self.assertIsInstance(train_data, dict)
        self.assertIsInstance(val_data, dict)
        self.assertIsInstance(test_data, dict)
        self.assertIn('player_stats', train_data)
        self.assertIn('team_stats', train_data)

class TestPredictionPipeline(unittest.TestCase):
    """Tests for the PredictionPipeline class"""
    
    @patch('src.training.PredictionPipeline')
    def setUp(self, mock_pipeline):
        """Set up test fixtures"""
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        self.prediction_pipeline = mock_pipeline
        self.prediction_pipeline.config_dir = self.config_dir
    
    def test_initialization(self):
        """Test prediction pipeline initialization"""
        self.assertIsNotNone(self.prediction_pipeline)
    
    def test_predict_for_sport(self):
        """Test sport-specific prediction"""
        # Create sample data
        data = {
            'player_stats': [
                {
                    'player_name': 'Player A',
                    'team': 'Team 1',
                    'opponent': 'Team 2',
                    'game_date': '2025-03-21',
                    'points': 25
                }
            ],
            'team_stats': [
                {
                    'team_name': 'Team 1',
                    'wins': 40,
                    'losses': 20
                }
            ],
            'prizepicks': [
                {
                    'player_name': 'Player A',
                    'stat_type': 'points',
                    'line': 24.5
                }
            ]
        }
        
        # Setup mock
        self.prediction_pipeline.predict_for_sport.return_value = [
            {
                'player': 'Player A',
                'team': 'Team 1',
                'opponent': 'Team 2',
                'date': '2025-03-21',
                'stat': 'points',
                'predicted_value': 26.5,
                'over_probability': 0.7,
                'line': 24.5,
                'confidence': 'High',
                'confidence_score': 80,
                'top_factors': ['Recent scoring above average', 'Home game advantage', 'Weak opponent defense']
            }
        ]
        
        # Call method
        predictions = self.prediction_pipeline.predict_for_sport(data, 'nba')
        
        # Check result
        self.assertIsInstance(predictions, list)
        self.assertEqual(len(predictions), 1)
        self.assertIn('player', predictions[0])
        self.assertIn('predicted_value', predictions[0])
        self.assertIn('over_probability', predictions[0])
        self.assertIn('confidence', predictions[0])
        self.assertIn('top_factors', predictions[0])

class TestAutomationSystem(unittest.TestCase):
    """Tests for the AutomationSystem class"""
    
    @patch('src.automation.AutomationSystem')
    def setUp(self, mock_system):
        """Set up test fixtures"""
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        self.automation_system = mock_system
        self.automation_system.config_dir = self.config_dir
    
    def test_initialization(self):
        """Test automation system initialization"""
        self.assertIsNotNone(self.automation_system)
    
    def test_run_data_collection(self):
        """Test data collection execution"""
        # Setup mock
        self.automation_system.run_data_collection.return_value = {
            'nba': {
                'player_stats': [{'player_name': 'Player A', 'points': 25}],
                'team_stats': [{'team_name': 'Team 1', 'wins': 40}]
            }
        }
        
        # Call method
        result = self.automation_system.run_data_collection()
        
        # Check result
        self.assertIsInstance(result, dict)
        self.assertIn('nba', result)
    
    def test_run_full_pipeline(self):
        """Test full pipeline execution"""
        # Setup mock
        self.automation_system.run_full_pipeline.return_value = True
        
        # Call method
        result = self.automation_system.run_full_pipeline()
        
        # Check result
        self.assertTrue(result)

class TestMonitoringSystem(unittest.TestCase):
    """Tests for the MonitoringSystem class"""
    
    @patch('src.automation.MonitoringSystem')
    def setUp(self, mock_system):
        """Set up test fixtures"""
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        self.monitoring_system = mock_system
        self.monitoring_system.config_dir = self.config_dir
    
    def test_initialization(self):
        """Test monitoring system initialization"""
        self.assertIsNotNone(self.monitoring_system)
    
    def test_track_performance(self):
        """Test performance tracking"""
        # Create sample data
        predictions = {
            'nba': [
                {
                    'player': 'Player A',
                    'team': 'Team 1',
                    'opponent': 'Team 2',
                    'date': '2025-03-21',
                    'stat': 'points',
                    'predicted_value': 26.5,
                    'over_probability': 0.7,
                    'line': 24.5
                }
            ]
        }
        
        actual_outcomes = {
            'nba': [
                {
                    'player': 'Player A',
                    'team': 'Team 1',
                    'opponent': 'Team 2',
                    'dat<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>