"""
Module for initializing the data collection package.
"""

from .base_collector import BaseDataCollector
from .nba_collector import NBADataCollector
from .nfl_collector import NFLDataCollector
from .mlb_collector import MLBDataCollector
from .nhl_collector import NHLDataCollector
from .soccer_collector import SoccerDataCollector
from .data_manager import DataCollectionManager

__all__ = [
    'BaseDataCollector',
    'NBADataCollector',
    'NFLDataCollector',
    'MLBDataCollector',
    'NHLDataCollector',
    'SoccerDataCollector',
    'DataCollectionManager'
]
