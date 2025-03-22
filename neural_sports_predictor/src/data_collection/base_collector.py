"""
Base data collector module that defines the interface for all sport-specific collectors.
"""

import os
import json
import logging
import requests
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

class BaseDataCollector(ABC):
    """
    Abstract base class for all sport data collectors.
    Provides common functionality and defines the interface that all collectors must implement.
    """
    
    def __init__(self, sport_name: str, config_path: str = None):
        """
        Initialize the data collector with sport-specific configuration.
        
        Args:
            sport_name: Name of the sport (e.g., 'NBA', 'NFL')
            config_path: Path to the configuration directory
        """
        self.sport_name = sport_name.lower()
        self.config_dir = config_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                     'config')
        
        # Load sport configuration
        sport_config_path = os.path.join(self.config_dir, 'sports', f'{self.sport_name}.json')
        with open(sport_config_path, 'r') as f:
            self.sport_config = json.load(f)
            
        # Load data collection configuration
        pipeline_config_path = os.path.join(self.config_dir, 'pipeline', 'data_collection.json')
        with open(pipeline_config_path, 'r') as f:
            self.pipeline_config = json.load(f)
            
        # Setup logging
        self._setup_logging()
        
        # Initialize session for API requests
        self.session = requests.Session()
        
        # API configuration
        self.api_delay = self.pipeline_config.get('data_collection', {}).get('api_request_delay', 1)
        self.max_retries = self.pipeline_config.get('data_collection', {}).get('max_retries', 3)
        self.timeout = self.pipeline_config.get('data_collection', {}).get('timeout', 30)
        
        self.logger.info(f"Initialized {self.sport_name.upper()} data collector")
    
    def _setup_logging(self):
        """Set up logging configuration"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_config = self.pipeline_config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file_path', os.path.join(log_dir, 'data_collection.log'))
        
        # Create logger
        self.logger = logging.getLogger(f"{self.sport_name}_collector")
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
    
    def _make_api_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """
        Make an API request with retry logic and error handling.
        
        Args:
            url: API endpoint URL
            params: Query parameters for the request
            
        Returns:
            Response data as dictionary or None if request failed
        """
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Making API request to {url}")
                response = self.session.get(url, params=params, timeout=self.timeout)
                
                # Respect API rate limits
                time.sleep(self.api_delay)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    self.logger.warning(f"API request failed with status {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"API request error: {str(e)}")
            
            # Wait before retrying
            retry_delay = (2 ** attempt) * self.api_delay
            self.logger.info(f"Retrying in {retry_delay} seconds (attempt {attempt + 1}/{self.max_retries})")
            time.sleep(retry_delay)
        
        self.logger.error(f"Failed to retrieve data after {self.max_retries} attempts")
        return None
    
    def get_date_range(self, days: int = None) -> List[str]:
        """
        Generate a list of dates for data collection.
        
        Args:
            days: Number of days to look back (defaults to config value)
            
        Returns:
            List of date strings in format 'YYYY-MM-DD'
        """
        if days is None:
            days = self.pipeline_config.get('data_collection', {}).get('historical_days', 365)
            
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
            
        return date_list
    
    @abstractmethod
    def collect_player_stats(self, date: str = None) -> List[Dict]:
        """
        Collect player statistics for a specific date.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to yesterday)
            
        Returns:
            List of player statistics
        """
        pass
    
    @abstractmethod
    def collect_team_stats(self, date: str = None) -> List[Dict]:
        """
        Collect team statistics for a specific date.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to yesterday)
            
        Returns:
            List of team statistics
        """
        pass
    
    @abstractmethod
    def collect_schedules(self, season: str = None) -> List[Dict]:
        """
        Collect game schedules for a specific season.
        
        Args:
            season: Season identifier (defaults to current season)
            
        Returns:
            List of scheduled games
        """
        pass
    
    @abstractmethod
    def collect_injuries(self) -> List[Dict]:
        """
        Collect current injury reports.
        
        Returns:
            List of player injuries
        """
        pass
    
    @abstractmethod
    def collect_odds(self, date: str = None) -> List[Dict]:
        """
        Collect betting odds for a specific date.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to today)
            
        Returns:
            List of betting odds
        """
        pass
    
    def collect_weather(self, date: str = None) -> Optional[List[Dict]]:
        """
        Collect weather data for outdoor sports.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to today)
            
        Returns:
            List of weather data or None if sport is indoor
        """
        # Only collect weather for outdoor sports
        if not self.sport_config.get('is_indoor', False) and self.sport_config.get('weather_relevant', False):
            # Implementation will be provided by subclasses
            return self._collect_weather_impl(date)
        
        self.logger.debug(f"Weather data not relevant for {self.sport_name}")
        return None
    
    def _collect_weather_impl(self, date: str = None) -> List[Dict]:
        """
        Implementation for collecting weather data (to be overridden by outdoor sports).
        
        Args:
            date: Date string in format 'YYYY-MM-DD'
            
        Returns:
            List of weather data
        """
        return []
    
    def collect_all_data(self, date: str = None) -> Dict[str, List[Dict]]:
        """
        Collect all available data for a specific date.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to yesterday)
            
        Returns:
            Dictionary containing all collected data
        """
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
        self.logger.info(f"Collecting all data for {self.sport_name} on {date}")
        
        data = {
            'player_stats': self.collect_player_stats(date),
            'team_stats': self.collect_team_stats(date),
            'injuries': self.collect_injuries(),
            'odds': self.collect_odds(date)
        }
        
        # Add weather data for outdoor sports
        weather_data = self.collect_weather(date)
        if weather_data is not None:
            data['weather'] = weather_data
            
        return data
    
    def save_data(self, data: Dict[str, List[Dict]], date: str = None) -> Dict[str, str]:
        """
        Save collected data to storage.
        
        Args:
            data: Dictionary containing collected data
            date: Date string in format 'YYYY-MM-DD'
            
        Returns:
            Dictionary with paths to saved files
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                               'data', self.sport_name)
        os.makedirs(data_dir, exist_ok=True)
        
        saved_files = {}
        
        # Save each data type to a separate file
        for data_type, items in data.items():
            if not items:
                self.logger.warning(f"No {data_type} data to save for {self.sport_name} on {date}")
                continue
                
            filename = f"{data_type}_{date}.json"
            file_path = os.path.join(data_dir, filename)
            
            with open(file_path, 'w') as f:
                json.dump(items, f, indent=2)
                
            saved_files[data_type] = file_path
            self.logger.info(f"Saved {len(items)} {data_type} records to {file_path}")
            
        return saved_files
