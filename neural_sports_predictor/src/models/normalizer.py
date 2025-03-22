"""
Multi-sport input normalization module for the neural network-based sports predictor.
This module handles the normalization of different sport-specific statistics into a common format.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional, Union
import json
import os

class MultiSportNormalizer:
    """
    Normalizer for multi-sport input data.
    Handles the transformation of sport-specific statistics into a common format.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the multi-sport normalizer.
        
        Args:
            config_path: Path to the configuration directory
        """
        self.config_dir = config_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                     'config')
        
        # Load sport configurations
        self.sport_configs = {}
        self._load_sport_configs()
        
        # Initialize stat mappings
        self.stat_mappings = self._create_stat_mappings()
        
        # Initialize normalization parameters
        self.normalization_params = {}
        
    def _load_sport_configs(self) -> None:
        """
        Load configuration files for all sports.
        """
        sports_dir = os.path.join(self.config_dir, 'sports')
        
        for filename in os.listdir(sports_dir):
            if filename.endswith('.json'):
                sport_name = filename.split('.')[0]
                with open(os.path.join(sports_dir, filename), 'r') as f:
                    self.sport_configs[sport_name] = json.load(f)
    
    def _create_stat_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        Create mappings between sport-specific stats and common normalized stats.
        
        Returns:
            Dictionary mapping sport-specific stats to common normalized stats
        """
        # Define common normalized stat categories
        common_stats = [
            'scoring',           # Points, goals, runs, etc.
            'assists',           # Assists across sports
            'rebounds',          # Rebounds, catches, etc.
            'defensive_plays',   # Steals, interceptions, blocks, etc.
            'efficiency',        # Shooting %, completion %, etc.
            'playing_time',      # Minutes, innings, etc.
            'turnovers',         # Turnovers, fumbles, etc.
            'fouls'              # Fouls, penalties, etc.
        ]
        
        # Create mappings for each sport
        mappings = {}
        
        # NBA mappings
        mappings['nba'] = {
            'points': 'scoring',
            'rebounds': 'rebounds',
            'assists': 'assists',
            'steals': 'defensive_plays',
            'blocks': 'defensive_plays',
            'three_pointers_made': 'scoring',
            'field_goal_percentage': 'efficiency',
            'minutes': 'playing_time',
            'turnovers': 'turnovers',
            'personal_fouls': 'fouls'
        }
        
        # NFL mappings
        mappings['nfl'] = {
            'passing_yards': 'scoring',
            'passing_touchdowns': 'scoring',
            'rushing_yards': 'scoring',
            'rushing_touchdowns': 'scoring',
            'receiving_yards': 'scoring',
            'receptions': 'rebounds',
            'receiving_touchdowns': 'scoring',
            'tackles': 'defensive_plays',
            'sacks': 'defensive_plays',
            'interceptions': 'defensive_plays',
            'passing_completions': 'efficiency',
            'passing_attempts': 'efficiency',
            'rushing_attempts': 'efficiency',
            'targets': 'efficiency',
            'fumbles': 'turnovers'
        }
        
        # MLB mappings
        mappings['mlb'] = {
            'runs': 'scoring',
            'hits': 'scoring',
            'home_runs': 'scoring',
            'runs_batted_in': 'assists',
            'stolen_bases': 'defensive_plays',
            'batting_average': 'efficiency',
            'at_bats': 'playing_time',
            'innings_pitched': 'playing_time',
            'pitcher_strikeouts': 'defensive_plays',
            'earned_run_average': 'efficiency',
            'walks': 'turnovers',
            'strikeouts': 'turnovers'
        }
        
        # NHL mappings
        mappings['nhl'] = {
            'goals': 'scoring',
            'assists': 'assists',
            'points': 'scoring',
            'shots': 'efficiency',
            'blocked_shots': 'defensive_plays',
            'hits': 'defensive_plays',
            'time_on_ice': 'playing_time',
            'penalty_minutes': 'fouls',
            'face_offs_won': 'efficiency',
            'plus_minus': 'efficiency'
        }
        
        # Soccer mappings
        mappings['soccer'] = {
            'goals': 'scoring',
            'assists': 'assists',
            'shots': 'efficiency',
            'shots_on_target': 'efficiency',
            'passes': 'assists',
            'key_passes': 'assists',
            'tackles': 'defensive_plays',
            'interceptions': 'defensive_plays',
            'minutes_played': 'playing_time',
            'fouls_committed': 'fouls',
            'yellow_cards': 'fouls',
            'red_cards': 'fouls'
        }
        
        return mappings
    
    def fit(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        Fit the normalizer on training data to compute normalization parameters.
        
        Args:
            data: Dictionary mapping sport names to lists of player statistics
        """
        # Calculate normalization parameters for each sport and stat
        for sport, sport_data in data.items():
            if sport not in self.normalization_params:
                self.normalization_params[sport] = {}
                
            # Convert to DataFrame for easier processing
            df = pd.DataFrame(sport_data)
            
            # Extract stats from nested dictionaries
            if 'stats' in df.columns and len(df) > 0 and isinstance(df['stats'].iloc[0], dict):
                stats_df = pd.json_normalize(df['stats'])
                
                # Calculate mean and std for each stat
                for stat in stats_df.columns:
                    if stats_df[stat].dtype in [np.float64, np.int64]:
                        self.normalization_params[sport][stat] = {
                            'mean': float(stats_df[stat].mean()),
                            'std': float(stats_df[stat].std()) if stats_df[stat].std() > 0 else 1.0
                        }
    
    def transform(self, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, np.ndarray]:
        """
        Transform sport-specific data into normalized common format.
        
        Args:
            data: Dictionary mapping sport names to lists of player statistics
            
        Returns:
            Dictionary with normalized features for each common stat category
        """
        # Initialize normalized data structure
        normalized_data = {
            'scoring': [],
            'assists': [],
            'rebounds': [],
            'defensive_plays': [],
            'efficiency': [],
            'playing_time': [],
            'turnovers': [],
            'fouls': []
        }
        
        # Process each sport's data
        for sport, sport_data in data.items():
            sport_mapping = self.stat_mappings.get(sport, {})
            sport_params = self.normalization_params.get(sport, {})
            
            for player_data in sport_data:
                # Extract stats from nested dictionary
                if 'stats' in player_data and isinstance(player_data['stats'], dict):
                    stats = player_data['stats']
                    
                    # Initialize normalized stats for this player
                    player_normalized = {category: [] for category in normalized_data.keys()}
                    
                    # Normalize each stat and map to common categories
                    for stat, value in stats.items():
                        if stat in sport_mapping and isinstance(value, (int, float)):
                            common_category = sport_mapping[stat]
                            
                            # Normalize using mean and std if available
                            if stat in sport_params:
                                mean = sport_params[stat]['mean']
                                std = sport_params[stat]['std']
                                normalized_value = (value - mean) / std
                            else:
                                # Fallback to min-max scaling if no parameters
                                normalized_value = value / 100.0  # Simple scaling
                            
                            player_normalized[common_category].append(normalized_value)
                    
                    # Average multiple stats in the same category
                    for category, values in player_normalized.items():
                        if values:
                            normalized_data[category].append(np.mean(values))
                        else:
                            normalized_data[category].append(0.0)  # Default value if no stats
        
        # Convert lists to numpy arrays
        for category in normalized_data:
            normalized_data[category] = np.array(normalized_data[category])
            
        return normalized_data
    
    def fit_transform(self, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, np.ndarray]:
        """
        Fit the normalizer and transform the data.
        
        Args:
            data: Dictionary mapping sport names to lists of player statistics
            
        Returns:
            Dictionary with normalized features for each common stat category
        """
        self.fit(data)
        return self.transform(data)
    
    def inverse_transform(self, normalized_data: Dict[str, np.ndarray], sport: str) -> Dict[str, np.ndarray]:
        """
        Convert normalized data back to sport-specific scale.
        
        Args:
            normalized_data: Dictionary with normalized features
            sport: Sport name to convert back to
            
        Returns:
            Dictionary with denormalized sport-specific stats
        """
        sport_mapping = self.stat_mappings.get(sport, {})
        sport_params = self.normalization_params.get(sport, {})
        
        # Create reverse mapping (common category -> sport-specific stats)
        reverse_mapping = {}
        for stat, category in sport_mapping.items():
            if category not in reverse_mapping:
                reverse_mapping[category] = []
            reverse_mapping[category].append(stat)
        
        # Initialize denormalized data
        denormalized_data = {}
        
        # Denormalize each common category to sport-specific stats
        for category, values in normalized_data.items():
            if category in reverse_mapping:
                for stat in reverse_mapping[category]:
                    if stat in sport_params:
                        mean = sport_params[stat]['mean']
                        std = sport_params[stat]['std']
                        denormalized_data[stat] = values * std + mean
                    else:
                        # Fallback if no parameters
                        denormalized_data[stat] = values * 100.0
        
        return denormalized_data
    
    def save(self, filepath: str) -> None:
        """
        Save the normalizer parameters to a file.
        
        Args:
            filepath: Path to save the parameters
        """
        params = {
            'stat_mappings': self.stat_mappings,
            'normalization_params': self.normalization_params
        }
        
        with open(filepath, 'w') as f:
            json.dump(params, f, indent=2)
    
    def load(self, filepath: str) -> None:
        """
        Load normalizer parameters from a file.
        
        Args:
            filepath: Path to load the parameters from
        """
        with open(filepath, 'r') as f:
            params = json.load(f)
            
        self.stat_mappings = params.get('stat_mappings', {})
        self.normalization_params = params.get('normalization_params', {})
