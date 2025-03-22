"""
MLB data collector module for fetching MLB-specific statistics and data.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .base_collector import BaseDataCollector

class MLBDataCollector(BaseDataCollector):
    """
    Data collector for MLB statistics and information.
    Implements the abstract methods defined in BaseDataCollector.
    """
    
    def __init__(self, config_path: str = None, api_key: str = None):
        """
        Initialize the MLB data collector.
        
        Args:
            config_path: Path to the configuration directory
            api_key: API key for the sports data provider (optional)
        """
        super().__init__('mlb', config_path)
        
        # Set API key (from parameter, environment variable, or config file)
        self.api_key = api_key or os.environ.get('SPORTS_DATA_API_KEY', 'demo-key')
        
        # Get MLB-specific endpoints
        self.endpoints = self.sport_config.get('data_sources', {})
        
        # Determine current MLB season
        current_year = datetime.now().year
        current_month = datetime.now().month
        # MLB season typically runs from April to October
        if current_month >= 11 or current_month <= 2:
            self.current_season = str(current_year - 1)
        else:
            self.current_season = str(current_year)
            
        self.logger.info(f"MLB data collector initialized for season {self.current_season}")
    
    def _format_endpoint(self, endpoint_template: str, **kwargs) -> str:
        """
        Format an endpoint URL with the given parameters.
        
        Args:
            endpoint_template: URL template from the configuration
            **kwargs: Parameters to substitute in the template
            
        Returns:
            Formatted URL
        """
        # Add API key to parameters
        params = {'key': self.api_key}
        
        # Format the URL template
        url = endpoint_template
        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            if placeholder in url:
                url = url.replace(placeholder, str(value))
                
        return url
    
    def collect_player_stats(self, date: str = None) -> List[Dict]:
        """
        Collect MLB player statistics for a specific date.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to yesterday)
            
        Returns:
            List of player statistics
        """
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
        self.logger.info(f"Collecting MLB player stats for {date}")
        
        endpoint = self.endpoints.get('player_stats', '')
        if not endpoint:
            self.logger.error("Player stats endpoint not found in configuration")
            return []
            
        url = self._format_endpoint(endpoint, date=date)
        data = self._make_api_request(url)
        
        if not data:
            self.logger.warning(f"No player stats data retrieved for {date}")
            return []
            
        # Process and normalize the data
        processed_data = []
        for player_game in data:
            # Extract relevant fields and normalize
            processed_player = {
                'player_id': player_game.get('PlayerID'),
                'player_name': player_game.get('Name'),
                'team': player_game.get('Team'),
                'position': player_game.get('Position'),
                'opponent': player_game.get('Opponent'),
                'home_away': 'home' if player_game.get('HomeOrAway') == 'HOME' else 'away',
                'game_date': date,
                'stats': {
                    # Batting stats
                    'at_bats': player_game.get('AtBats'),
                    'runs': player_game.get('Runs'),
                    'hits': player_game.get('Hits'),
                    'singles': player_game.get('Singles'),
                    'doubles': player_game.get('Doubles'),
                    'triples': player_game.get('Triples'),
                    'home_runs': player_game.get('HomeRuns'),
                    'runs_batted_in': player_game.get('RunsBattedIn'),
                    'batting_average': player_game.get('BattingAverage'),
                    'stolen_bases': player_game.get('StolenBases'),
                    'caught_stealing': player_game.get('CaughtStealing'),
                    'walks': player_game.get('Walks'),
                    'strikeouts': player_game.get('Strikeouts'),
                    
                    # Pitching stats
                    'innings_pitched': player_game.get('InningsPitched'),
                    'pitcher_strikeouts': player_game.get('PitcherStrikeouts'),
                    'pitcher_walks': player_game.get('PitcherWalks'),
                    'hits_allowed': player_game.get('HitsAllowed'),
                    'earned_runs': player_game.get('EarnedRuns'),
                    'earned_run_average': player_game.get('EarnedRunAverage'),
                    'pitches_thrown': player_game.get('PitchesThrown'),
                    'win': player_game.get('Win'),
                    'loss': player_game.get('Loss'),
                    'save': player_game.get('Save')
                },
                'fantasy_points': player_game.get('FantasyPoints')
            }
            
            # Calculate combined stats
            if all(key in processed_player['stats'] for key in ['hits', 'runs', 'runs_batted_in']):
                processed_player['stats']['hits_runs_rbi'] = (
                    processed_player['stats']['hits'] + 
                    processed_player['stats']['runs'] + 
                    processed_player['stats']['runs_batted_in']
                )
            
            processed_data.append(processed_player)
            
        self.logger.info(f"Collected stats for {len(processed_data)} MLB players")
        return processed_data
    
    def collect_team_stats(self, date: str = None) -> List[Dict]:
        """
        Collect MLB team statistics for a specific date.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to yesterday)
            
        Returns:
            List of team statistics
        """
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
        self.logger.info(f"Collecting MLB team stats for {date}")
        
        endpoint = self.endpoints.get('team_stats', '')
        if not endpoint:
            self.logger.error("Team stats endpoint not found in configuration")
            return []
            
        url = self._format_endpoint(endpoint, date=date)
        data = self._make_api_request(url)
        
        if not data:
            self.logger.warning(f"No team stats data retrieved for {date}")
            return []
            
        # Process and normalize the data
        processed_data = []
        for team_game in data:
            processed_team = {
                'team_id': team_game.get('TeamID'),
                'team': team_game.get('Team'),
                'opponent': team_game.get('Opponent'),
                'home_away': 'home' if team_game.get('HomeOrAway') == 'HOME' else 'away',
                'game_date': date,
                'stats': {
                    'runs': team_game.get('Runs'),
                    'hits': team_game.get('Hits'),
                    'at_bats': team_game.get('AtBats'),
                    'batting_average': team_game.get('BattingAverage'),
                    'on_base_percentage': team_game.get('OnBasePercentage'),
                    'slugging_percentage': team_game.get('SluggingPercentage'),
                    'errors': team_game.get('Errors'),
                    'home_runs': team_game.get('HomeRuns'),
                    'stolen_bases': team_game.get('StolenBases'),
                    'earned_runs': team_game.get('EarnedRuns'),
                    'team_era': team_game.get('TeamERA')
                },
                'win_loss': team_game.get('WinOrLoss'),
                'innings': team_game.get('Innings'),
                'run_line': team_game.get('RunLine'),
                'over_under': team_game.get('OverUnder')
            }
            
            processed_data.append(processed_team)
            
        self.logger.info(f"Collected stats for {len(processed_data)} MLB teams")
        return processed_data
    
    def collect_schedules(self, season: str = None) -> List[Dict]:
        """
        Collect MLB game schedules for a specific season.
        
        Args:
            season: Season identifier (defaults to current season)
            
        Returns:
            List of scheduled games
        """
        if season is None:
            season = self.current_season
            
        self.logger.info(f"Collecting MLB schedules for season {season}")
        
        endpoint = self.endpoints.get('schedules', '')
        if not endpoint:
            self.logger.error("Schedules endpoint not found in configuration")
            return []
            
        url = self._format_endpoint(endpoint, season=season)
        data = self._make_api_request(url)
        
        if not data:
            self.logger.warning(f"No schedule data retrieved for season {season}")
            return []
            
        # Process and normalize the data
        processed_data = []
        for game in data:
            processed_game = {
                'game_id': game.get('GameID'),
                'season': season,
                'status': game.get('Status'),
                'date': game.get('Day')[:10] if game.get('Day') else None,  # Extract YYYY-MM-DD
                'away_team': game.get('AwayTeam'),
                'home_team': game.get('HomeTeam'),
                'stadium': game.get('Stadium'),
                'channel': game.get('Channel'),
                'innings': game.get('Innings'),
                'day_night': game.get('DayNight'),
                'series': game.get('SeriesInfo')
            }
            
            processed_data.append(processed_game)
            
        self.logger.info(f"Collected {len(processed_data)} MLB scheduled games")
        return processed_data
    
    def collect_injuries(self) -> List[Dict]:
        """
        Collect current MLB injury reports.
        
        Returns:
            List of player injuries
        """
        self.logger.info("Collecting MLB injury reports")
        
        endpoint = self.endpoints.get('injuries', '')
        if not endpoint:
            self.logger.error("Injuries endpoint not found in configuration")
            return []
            
        url = self._format_endpoint(endpoint)
        data = self._make_api_request(url)
        
        if not data:
            self.logger.warning("No injury data retrieved")
            return []
            
        # Process and normalize the data
        processed_data = []
        for injury in data:
            processed_injury = {
                'player_id': injury.get('PlayerID'),
                'player_name': injury.get('Name'),
                'team': injury.get('Team'),
                'position': injury.get('Position'),
                'injury': injury.get('Injury'),
                'status': injury.get('Status'),
                'start_date': injury.get('StartDate')[:10] if injury.get('StartDate') else None,
                'expected_return': injury.get('ExpectedReturn')
            }
            
            processed_data.append(processed_injury)
            
        self.logger.info(f"Collected {len(processed_data)} MLB player injuries")
        return processed_data
    
    def collect_odds(self, date: str = None) -> List[Dict]:
        """
        Collect MLB betting odds for a specific date.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to today)
            
        Returns:
            List of betting odds
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        self.logger.info(f"Collecting MLB betting odds for {date}")
        
        endpoint = self.endpoints.get('odds', '')
        if not endpoint:
            self.logger.error("Odds endpoint not found in configuration")
            return []
            
        url = self._format_endpoint(endpoint, date=date)
        data = self._make_api_request(url)
        
        if not data:
            self.logger.warning(f"No odds data retrieved for {date}")
            return []
            
        # Process and normalize the data
        processed_data = []
        for game_odds in data:
            processed_odds = {
                'game_id': game_odds.get('GameID'),
                'date': date,
                'away_team': game_odds.get('AwayTeam'),
                'home_team': game_odds.get('HomeTeam'),
                'run_line': game_odds.get('RunLine'),
                'over_under': game_odds.get('OverUnder'),
                'away_money_line': game_odds.get('AwayMoneyLine'),
                'home_money_line': game_odds.get('HomeMoneyLine'),
                'updated_date': game_odds.get('LastUpdated')
            }
            
            # Add player props if available
            if 'PlayerPropOdds' in game_odds and game_odds['PlayerPropOdds']:
                player_props = []
                for prop in game_odds['PlayerPropOdds']:
                    player_prop = {
                        'player_id': prop.get('PlayerID'),
                        'player_name': prop.get('PlayerName'),
                        'team': prop.get('Team'),
                        'stat_type': prop.get('StatType'),
                        'line': prop.get('Line'),
                        'over_payout': prop.get('OverPayout'),
                        'under_payout': prop.get('UnderPayout')
                    }
                    player_props.append(player_prop)
                
                processed_odds['player_props'] = player_props
            
            processed_data.append(processed_odds)
            
        self.logger.info(f"Collected odds for {len(processed_data)} MLB games")
        return processed_data
    
    def _collect_weather_impl(self, date: str = None) -> List[Dict]:
        """
        Collect weather data for MLB games.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to today)
            
        Returns:
            List of weather data
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        self.logger.info(f"Collecting MLB weather data for {date}")
        
        endpoint = self.endpoints.get('weather', '')
        if not endpoint:
            self.logger.error("Weather endpoint not found in configuration")
            return []
            
        url = self._format_endpoint(endpoint, date=date)
        data = self._make_api_request(url)
        
        if not data:
            self.logger.warning(f"No weather data retrieved for {date}")
            return []
            
        # Process and normalize the data
        processed_data = []
        for game_weather in data:
            processed_weather = {
                'game_id': game_weather.get('GameID'),
                'date': date,
                'away_team': game_weather.get('AwayTeam'),
                'home_team': game_weather.get('HomeTeam'),
                'stadium': game_weather.get('Stadium'),
                'temperature': game_weather.get('Temperature'),
                'humidity': game_weather.get('Humidity'),
                'wind_speed': game_weather.get('WindSpeed'),
                'wind_direction': game_weather.get('WindDirection'),
                'precipitation': game_w<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>