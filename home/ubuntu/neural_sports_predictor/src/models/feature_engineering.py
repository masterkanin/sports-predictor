"""
Feature engineering module for the neural network-based sports predictor.
This module handles the creation of derived features to enhance prediction accuracy.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional, Union
from datetime import datetime, timedelta

class FeatureEngineer:
    """
    Feature engineering for sports prediction data.
    Creates derived features to enhance model performance.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the feature engineer.
        
        Args:
            config: Configuration dictionary with feature engineering parameters
        """
        self.config = config
        self.rolling_windows = config.get('rolling_window_sizes', [3, 5, 10])
        
    def engineer_player_features(self, player_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Engineer features from player statistics.
        
        Args:
            player_data: List of player game statistics
            
        Returns:
            DataFrame with engineered features
        """
        # Convert to DataFrame
        df = pd.DataFrame(player_data)
        
        # Extract stats from nested dictionaries if needed
        if 'stats' in df.columns and len(df) > 0 and isinstance(df['stats'].iloc[0], dict):
            stats_df = pd.json_normalize(df['stats'])
            df = pd.concat([df.drop('stats', axis=1), stats_df], axis=1)
        
        # Sort by player and date
        if 'player_id' in df.columns and 'game_date' in df.columns:
            df['game_date'] = pd.to_datetime(df['game_date'])
            df = df.sort_values(['player_id', 'game_date'])
        
        # Create engineered features
        df = self._create_rolling_averages(df)
        df = self._create_trend_features(df)
        df = self._create_home_away_features(df)
        df = self._create_rest_features(df)
        df = self._create_matchup_features(df)
        
        # Fill missing values
        df = df.fillna(0)
        
        return df
    
    def _create_rolling_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create rolling average features for numeric columns.
        
        Args:
            df: DataFrame with player statistics
            
        Returns:
            DataFrame with added rolling average features
        """
        # Identify numeric columns for rolling averages
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # Exclude certain columns
        exclude_cols = ['player_id', 'team_id', 'opponent_id', 'game_id']
        numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        # Create rolling averages for each window size
        for window in self.rolling_windows:
            for col in numeric_cols:
                if 'player_id' in df.columns:
                    # Group by player_id and calculate rolling average
                    df[f'{col}_rolling_{window}'] = df.groupby('player_id')[col].transform(
                        lambda x: x.shift(1).rolling(window=window, min_periods=1).mean()
                    )
                else:
                    # Calculate rolling average without grouping
                    df[f'{col}_rolling_{window}'] = df[col].shift(1).rolling(window=window, min_periods=1).mean()
        
        return df
    
    def _create_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create trend features to capture recent form.
        
        Args:
            df: DataFrame with player statistics
            
        Returns:
            DataFrame with added trend features
        """
        # Identify numeric columns for trend features
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # Exclude certain columns and already created rolling features
        exclude_cols = ['player_id', 'team_id', 'opponent_id', 'game_id']
        exclude_cols += [col for col in numeric_cols if 'rolling_' in col]
        numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        # Create trend features (slope of recent performance)
        for col in numeric_cols:
            if 'player_id' in df.columns:
                # Calculate the difference between most recent and average of last 5 games
                df[f'{col}_trend'] = df.groupby('player_id')[col].transform(
                    lambda x: x.shift(1) - x.shift(2).rolling(window=5, min_periods=1).mean()
                )
                
                # Calculate standard deviation to measure consistency
                df[f'{col}_std_5'] = df.groupby('player_id')[col].transform(
                    lambda x: x.shift(1).rolling(window=5, min_periods=2).std()
                )
            else:
                # Calculate without grouping
                df[f'{col}_trend'] = df[col].shift(1) - df[col].shift(2).rolling(window=5, min_periods=1).mean()
                df[f'{col}_std_5'] = df[col].shift(1).rolling(window=5, min_periods=2).std()
        
        return df
    
    def _create_home_away_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features based on home/away performance.
        
        Args:
            df: DataFrame with player statistics
            
        Returns:
            DataFrame with added home/away features
        """
        if 'home_away' in df.columns:
            # Create binary indicator for home games
            df['is_home'] = (df['home_away'] == 'home').astype(int)
            
            # Identify numeric columns for home/away splits
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            exclude_cols = ['player_id', 'team_id', 'opponent_id', 'game_id', 'is_home']
            exclude_cols += [col for col in numeric_cols if 'rolling_' in col or 'trend' in col or 'std_' in col]
            numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
            
            # Calculate home/away performance differences
            if 'player_id' in df.columns:
                for col in numeric_cols:
                    # Home performance
                    home_avg = df[df['home_away'] == 'home'].groupby('player_id')[col].transform(
                        lambda x: x.shift(1).rolling(window=10, min_periods=1).mean()
                    )
                    
                    # Away performance
                    away_avg = df[df['home_away'] == 'away'].groupby('player_id')[col].transform(
                        lambda x: x.shift(1).rolling(window=10, min_periods=1).mean()
                    )
                    
                    # Fill missing values
                    df[f'{col}_home_avg'] = df['player_id'].map(
                        df.groupby('player_id')[col].apply(
                            lambda x: x[df['home_away'] == 'home'].shift(1).rolling(window=10, min_periods=1).mean().fillna(0)
                        )
                    )
                    
                    df[f'{col}_away_avg'] = df['player_id'].map(
                        df.groupby('player_id')[col].apply(
                            lambda x: x[df['home_away'] == 'away'].shift(1).rolling(window=10, min_periods=1).mean().fillna(0)
                        )
                    )
                    
                    # Home/away differential
                    df[f'{col}_home_away_diff'] = df[f'{col}_home_avg'] - df[f'{col}_away_avg']
        
        return df
    
    def _create_rest_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features based on rest days and back-to-back games.
        
        Args:
            df: DataFrame with player statistics
            
        Returns:
            DataFrame with added rest features
        """
        if 'game_date' in df.columns and 'player_id' in df.columns:
            # Calculate days since last game
            df['days_rest'] = df.groupby('player_id')['game_date'].diff().dt.days
            
            # Fill NaN values (first game for each player)
            df['days_rest'] = df['days_rest'].fillna(3)  # Assume average rest for first game
            
            # Create indicator for back-to-back games
            df['is_back_to_back'] = (df['days_rest'] <= 1).astype(int)
            
            # Create indicator for long rest
            df['is_long_rest'] = (df['days_rest'] >= 4).astype(int)
        
        return df
    
    def _create_matchup_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features based on opponent matchups.
        
        Args:
            df: DataFrame with player statistics
            
        Returns:
            DataFrame with added matchup features
        """
        if 'opponent' in df.columns and 'player_id' in df.columns:
            # Calculate historical performance against specific opponents
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            exclude_cols = ['player_id', 'team_id', 'opponent_id', 'game_id', 'is_home', 'days_rest', 
                           'is_back_to_back', 'is_long_rest']
            exclude_cols += [col for col in numeric_cols if 'rolling_' in col or 'trend' in col or 
                            'std_' in col or 'home_avg' in col or 'away_avg' in col]
            numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
            
            # For each player-opponent combination, calculate average performance
            for col in numeric_cols[:3]:  # Limit to a few key stats to avoid explosion of features
                df[f'{col}_vs_opp_avg'] = df.groupby(['player_id', 'opponent'])[col].transform(
                    lambda x: x.shift(1).expanding().mean()
                )
        
        return df
    
    def engineer_team_features(self, team_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Engineer features from team statistics.
        
        Args:
            team_data: List of team game statistics
            
        Returns:
            DataFrame with engineered team features
        """
        # Convert to DataFrame
        df = pd.DataFrame(team_data)
        
        # Extract stats from nested dictionaries if needed
        if 'stats' in df.columns and len(df) > 0 and isinstance(df['stats'].iloc[0], dict):
            stats_df = pd.json_normalize(df['stats'])
            df = pd.concat([df.drop('stats', axis=1), stats_df], axis=1)
        
        # Sort by team and date
        if 'team_id' in df.columns and 'game_date' in df.columns:
            df['game_date'] = pd.to_datetime(df['game_date'])
            df = df.sort_values(['team_id', 'game_date'])
        
        # Create team strength metrics
        df = self._create_team_strength_metrics(df)
        
        # Create team trend features
        df = self._create_team_trend_features(df)
        
        # Fill missing values
        df = df.fillna(0)
        
        return df
    
    def _create_team_strength_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create team strength metrics based on historical performance.
        
        Args:
            df: DataFrame with team statistics
            
        Returns:
            DataFrame with added team strength metrics
        """
        if 'team_id' in df.columns:
            # Identify key team stats
            offensive_stats = [col for col in df.columns if any(term in col.lower() for term in 
                                                              ['score', 'point', 'goal', 'run', 'yard', 'offensive'])]
            defensive_stats = [col for col in df.columns if any(term in col.lower() for term in 
                                                              ['allowed', 'defensive', 'against'])]
            
            # Create offensive rating (average of normalized offensive stats)
            if offensive_stats:
                # Normalize each stat
                for stat in offensive_stats:
                    if df[stat].std() > 0:
                        df[f'{stat}_norm'] = (df[stat] - df[stat].mean()) / df[stat].std()
                    else:
                        df[f'{stat}_norm'] = 0
                
                # Calculate offensive rating
                norm_cols = [f'{stat}_norm' for stat in offensive_stats if f'{stat}_norm' in df.columns]
                if norm_cols:
                    df['offensive_rating'] = df[norm_cols].mean(axis=1)
                    
                    # Calculate rolling offensive rating
                    df['offensive_rating_rolling_5'] = df.groupby('team_id')['offensive_rating'].transform(
                        lambda x: x.shift(1).rolling(window=5, min_periods=1).mean()
                    )
            
            # Create defensive rating (average of normalized defensive stats)
            if defensive_stats:
                # Normalize each stat (invert so higher is better defense)
                for stat in defensive_stats:
                    if df[stat].std() > 0:
                        df[f'{stat}_norm'] = -1 * (df[stat] - df[stat].mean()) / df[stat].std()
                    else:
                        df[f'{stat}_norm'] = 0
                
                # Calculate defensive rating
                norm_cols = [f'{stat}_norm' for stat in defensive_stats if f'{stat}_norm' in df.columns]
                if norm_cols:
                    df['defensive_rating'] = df[norm_cols].mean(axis=1)
                    
                    # Calculate rolling defensive rating
                    df['defensive_rating_rolling_5'] = df.groupby('team_id')['defensive_rating'].transform(
                        lambda x: x.shift(1).rolling(window=5, min_periods=1).mean()
                    )
            
            # Create overall team rating
            if 'offensive_rating' in df.columns and 'defensive_rating' in df.columns:
                df['team_rating'] = (df['offensive_rating'] + df['defensive_rating']) / 2
                
                # Calculate rolling team rating
                df['team_rating_rolling_5'] = df.groupby('team_id')['team_rating'].transform(
                    lambda x: x.shift(1).rolling(window=5, min_periods=1).mean()
                )
        
        return df
    
    def _create_team_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create team trend features to capture recent form.
        
        Args:
            df: DataFrame with team statistics
            
        Returns:
            DataFrame with added team trend features
        """
        # Identify key metrics for trend analysis
        key_metrics = ['offensive_rating', 'defensive_rating', 'team_rating']
        key_metrics += [col for col in df.columns if 'win' in col.lower()]
        
        # Create trend features
        for col in key_metrics:
            if col in df.columns and 'team_id' in df.columns:
                # Calculate trend (difference between recent and longer-term average)
                df[f'{col}_trend'] = df.groupby('team_id')[col].transform(
                    lambda x: x.shift(1).rolling(window=3, min_periods=1).mean() - 
                             x.shift(1).rolling(window=10, min_periods=1).mean()
                )
        
        # Create win streak feature
        if 'win_loss' in df.columns and 'team_id' in df.columns:
            # Convert win/loss to binary
            df['win_binary'] = df['win_loss'].apply(lambda x: 1 if x in ['W', 'WIN', 'Win'] else 0)
            
            # Calculate current win streak (consecutive wins)
            df['win_streak'] = df.groupby('team_id')['win_binary'].transform(
                lambda x: x.groupby((x != x.shift(1)).cumsum()).cumsum()
            )
            
            # Reset streak to 0 for losses
 <response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>