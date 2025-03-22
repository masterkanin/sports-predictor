"""
Main data collection module that orchestrates the collection process for all sports.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from .base_collector import BaseDataCollector
from .nba_collector import NBADataCollector
from .nfl_collector import NFLDataCollector
from .mlb_collector import MLBDataCollector
from .nhl_collector import NHLDataCollector
from .soccer_collector import SoccerDataCollector

class DataCollectionManager:
    """
    Manager class that orchestrates data collection across all sports.
    """
    
    def __init__(self, config_path: str = None, api_key: str = None):
        """
        Initialize the data collection manager.
        
        Args:
            config_path: Path to the configuration directory
            api_key: API key for the sports data provider (optional)
        """
        self.config_dir = config_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                     'config')
        
        # Load data collection configuration
        pipeline_config_path = os.path.join(self.config_dir, 'pipeline', 'data_collection.json')
        with open(pipeline_config_path, 'r') as f:
            self.pipeline_config = json.load(f)
            
        # Setup logging
        self._setup_logging()
        
        # Initialize collectors for each sport
        self.collectors = {
            'nba': NBADataCollector(config_path, api_key),
            'nfl': NFLDataCollector(config_path, api_key),
            'mlb': MLBDataCollector(config_path, api_key),
            'nhl': NHLDataCollector(config_path, api_key),
            'soccer': SoccerDataCollector(config_path, api_key)
        }
        
        self.logger.info("Data collection manager initialized")
    
    def _setup_logging(self):
        """Set up logging configuration"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_config = self.pipeline_config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file_path', os.path.join(log_dir, 'data_collection.log'))
        
        # Create logger
        self.logger = logging.getLogger('data_collection_manager')
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
    
    def collect_data_for_sport(self, sport: str, date: str = None) -> Dict[str, Dict[str, List[Dict]]]:
        """
        Collect all data for a specific sport.
        
        Args:
            sport: Sport name (e.g., 'nba', 'nfl')
            date: Date string in format 'YYYY-MM-DD' (defaults to yesterday)
            
        Returns:
            Dictionary containing all collected data for the sport
        """
        if sport.lower() not in self.collectors:
            self.logger.error(f"No collector available for sport: {sport}")
            return {}
            
        self.logger.info(f"Collecting data for {sport.upper()}")
        
        collector = self.collectors[sport.lower()]
        data = collector.collect_all_data(date)
        saved_files = collector.save_data(data, date)
        
        return {sport.lower(): {'data': data, 'files': saved_files}}
    
    def collect_data_for_all_sports(self, date: str = None) -> Dict[str, Dict[str, List[Dict]]]:
        """
        Collect data for all supported sports.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to yesterday)
            
        Returns:
            Dictionary containing all collected data for all sports
        """
        self.logger.info(f"Collecting data for all sports for date: {date or 'yesterday'}")
        
        all_data = {}
        
        for sport, collector in self.collectors.items():
            try:
                self.logger.info(f"Starting data collection for {sport.upper()}")
                data = collector.collect_all_data(date)
                saved_files = collector.save_data(data, date)
                all_data[sport] = {'data': data, 'files': saved_files}
                self.logger.info(f"Completed data collection for {sport.upper()}")
            except Exception as e:
                self.logger.error(f"Error collecting data for {sport}: {str(e)}")
                
        return all_data
    
    def collect_prizepicks_data(self, date: str = None) -> Dict[str, List[Dict]]:
        """
        Collect PrizePicks lines for all sports.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to today)
            
        Returns:
            Dictionary containing PrizePicks lines for all sports
        """
        self.logger.info(f"Collecting PrizePicks lines for all sports for date: {date or 'today'}")
        
        prizepicks_data = {}
        
        for sport, collector in self.collectors.items():
            try:
                if hasattr(collector, 'collect_prizepicks_lines'):
                    self.logger.info(f"Collecting PrizePicks lines for {sport.upper()}")
                    data = collector.collect_prizepicks_lines(date)
                    prizepicks_data[sport] = data
            except Exception as e:
                self.logger.error(f"Error collecting PrizePicks data for {sport}: {str(e)}")
                
        return prizepicks_data
    
    def collect_news_and_sentiment(self, days: int = 3) -> Dict[str, List[Dict]]:
        """
        Collect news and sentiment data for all sports.
        
        Args:
            days: Number of days to look back for news
            
        Returns:
            Dictionary containing news and sentiment data for all sports
        """
        self.logger.info(f"Collecting news and sentiment for all sports for the past {days} days")
        
        news_data = {}
        
        for sport, collector in self.collectors.items():
            try:
                if hasattr(collector, 'collect_news_and_sentiment'):
                    self.logger.info(f"Collecting news and sentiment for {sport.upper()}")
                    data = collector.collect_news_and_sentiment(days)
                    news_data[sport] = data
            except Exception as e:
                self.logger.error(f"Error collecting news and sentiment for {sport}: {str(e)}")
                
        return news_data
    
    def run_daily_collection(self) -> Dict[str, Dict[str, List[Dict]]]:
        """
        Run the daily data collection process for all sports.
        
        Returns:
            Dictionary containing all collected data for all sports
        """
        self.logger.info("Starting daily data collection process")
        
        # Collect regular data for all sports
        all_data = self.collect_data_for_all_sports()
        
        # Collect PrizePicks lines
        prizepicks_data = self.collect_prizepicks_data()
        
        # Collect news and sentiment
        news_data = self.collect_news_and_sentiment()
        
        # Add additional data to the results
        for sport in all_data:
            if sport in prizepicks_data:
                all_data[sport]['data']['prizepicks'] = prizepicks_data[sport]
            if sport in news_data:
                all_data[sport]['data']['news'] = news_data[sport]
        
        self.logger.info("Daily data collection process completed")
        return all_data
