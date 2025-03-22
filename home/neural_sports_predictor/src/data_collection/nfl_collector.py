"""
NFL data collector module for fetching NFL-specific statistics and data.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .base_collector import BaseDataCollector

class NFLDataCollector(BaseDataCollector):
    """
    Data collector for NFL statistics and information.
    Implements the abstract methods defined in BaseDataCollector.
    """
    
    def __init__(self, config_path: str = None, api_key: str = None):
        """
        Initialize the NFL data collector.
        
        Args:
            config_path: Path to the configuration directory
            api_key: API key for the sports data provider (optional)
        """
        super().__init__('nfl', config_path)
        
        # Set API key (from parameter, environment variable, or config file)
        self.api_key = api_key or os.environ.get('SPORTS_DATA_API_KEY', 'demo-key')
        
        # Get NFL-specific endpoints
        self.endpoints = self.sport_config.get('data_sources', {})
        
        # Determine current NFL season
        current_year = datetime.now().year
        current_month = datetime.now().month
        # NFL season typically starts in September and ends in February of the next year
        if current_month >= 3 and current_month <= 8:
            self.current_season = str(current_year)
        else:
            self.current_season = str(current_year if current_month >= 9 else current_year - 1)
            
        # Determine current week (simplified logic - would need more precise implementation)
        self.current_week = "1"  # Default to week 1
            
        self.logger.info(f"NFL data collector initialized for season {self.current_season}")
    
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
    
    def collect_player_stats(self, date: str = None, week: str = None, season: str = None) -> List[Dict]:
        """
        Collect NFL player statistics for a specific week.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (not used directly for NFL)
            week: NFL week number (defaults to current week)
            season: Season identifier (defaults to current season)
            
        Returns:
            List of player statistics
        """
        # NFL stats are typically collected by week, not by date
        if week is None:
            week = self.current_week
            
        if season is None:
            season = self.current_season
            
        self.logger.info(f"Collecting NFL player stats for season {season}, week {week}")
        
        endpoint = self.endpoints.get('player_stats', '')
        if not endpoint:
            self.logger.error("Player stats endpoint not found in configuration")
            return []
            
        url = self._format_endpoint(endpoint, season=season, week=week)
        data = self._make_api_request(url)
        
        if not data:
            self.logger.warning(f"No player stats data retrieved for season {season}, week {week}")
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
                'season': season,
                'week': week,
                'game_date': player_game.get('GameDate')[:10] if player_game.get('GameDate') else None,
                'stats': {
                    # Passing stats
                    'passing_attempts': player_game.get('PassingAttempts'),
                    'passing_completions': player_game.get('PassingCompletions'),
                    'passing_yards': player_game.get('PassingYards'),
                    'passing_touchdowns': player_game.get('PassingTouchdowns'),
                    'passing_interceptions': player_game.get('PassingInterceptions'),
                    
                    # Rushing stats
                    'rushing_attempts': player_game.get('RushingAttempts'),
                    'rushing_yards': player_game.get('RushingYards'),
                    'rushing_touchdowns': player_game.get('RushingTouchdowns'),
                    
                    # Receiving stats
                    'receptions': player_game.get('Receptions'),
                    'receiving_yards': player_game.get('ReceivingYards'),
                    'receiving_touchdowns': player_game.get('ReceivingTouchdowns'),
                    'targets': player_game.get('Targets'),
                    
                    # Defense stats
                    'tackles': player_game.get('Tackles'),
                    'sacks': player_game.get('Sacks'),
                    'interceptions': player_game.get('Interceptions'),
                    'fumbles_forced': player_game.get('FumblesForced'),
                    'fumbles_recovered': player_game.get('FumblesRecovered')
                },
                'fantasy_points': player_game.get('FantasyPoints')
            }
            
            processed_data.append(processed_player)
            
        self.logger.info(f"Collected stats for {len(processed_data)} NFL players")
        return processed_data
    
    def collect_team_stats(self, date: str = None, week: str = None, season: str = None) -> List[Dict]:
        """
        Collect NFL team statistics for a specific week.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (not used directly for NFL)
            week: NFL week number (defaults to current week)
            season: Season identifier (defaults to current season)
            
        Returns:
            List of team statistics
        """
        if week is None:
            week = self.current_week
            
        if season is None:
            season = self.current_season
            
        self.logger.info(f"Collecting NFL team stats for season {season}, week {week}")
        
        endpoint = self.endpoints.get('team_stats', '')
        if not endpoint:
            self.logger.error("Team stats endpoint not found in configuration")
            return []
            
        url = self._format_endpoint(endpoint, season=season, week=week)
        data = self._make_api_request(url)
        
        if not data:
            self.logger.warning(f"No team stats data retrieved for season {season}, week {week}")
            return []
            
        # Process and normalize the data
        processed_data = []
        for team_game in data:
            processed_team = {
                'team_id': team_game.get('TeamID'),
                'team': team_game.get('Team'),
                'opponent': team_game.get('Opponent'),
                'home_away': 'home' if team_game.get('HomeOrAway') == 'HOME' else 'away',
                'season': season,
                'week': week,
                'game_date': team_game.get('GameDate')[:10] if team_game.get('GameDate') else None,
                'stats': {
                    # Offense stats
                    'score': team_game.get('Score'),
                    'total_yards': team_game.get('TotalYards'),
                    'passing_yards': team_game.get('PassingYards'),
                    'rushing_yards': team_game.get('RushingYards'),
                    'first_downs': team_game.get('FirstDowns'),
                    'third_down_conversions': team_game.get('ThirdDownConversions'),
                    'third_down_attempts': team_game.get('ThirdDownAttempts'),
                    'fourth_down_conversions': team_game.get('FourthDownConversions'),
                    'fourth_down_attempts': team_game.get('FourthDownAttempts'),
                    'possession_time': team_game.get('PossessionTime'),
                    
                    # Defense stats
                    'sacks': team_game.get('Sacks'),
                    'interceptions': team_game.get('Interceptions'),
                    'fumbles_recovered': team_game.get('FumblesRecovered')
                },
                'win_loss': team_game.get('WinOrLoss'),
                'point_spread': team_game.get('PointSpread'),
                'over_under': team_game.get('OverUnder')
            }
            
            # Calculate efficiency metrics
            if processed_team['stats'].get('third_down_attempts') and processed_team['stats'].get('third_down_attempts') > 0:
                processed_team['stats']['third_down_efficiency'] = (
                    processed_team['stats']['third_down_conversions'] / processed_team['stats']['third_down_attempts']
                )
                
            processed_data.append(processed_team)
            
        self.logger.info(f"Collected stats for {len(processed_data)} NFL teams")
        return processed_data
    
    def collect_schedules(self, season: str = None) -> List[Dict]:
        """
        Collect NFL game schedules for a specific season.
        
        Args:
            season: Season identifier (defaults to current season)
            
        Returns:
            List of scheduled games
        """
        if season is None:
            season = self.current_season
            
        self.logger.info(f"Collecting NFL schedules for season {season}")
        
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
                'season_type': game.get('SeasonType'),
                'week': game.get('Week'),
                'status': game.get('Status'),
                'date': game.get('Date')[:10] if game.get('Date') else None,  # Extract YYYY-MM-DD
                'away_team': game.get('AwayTeam'),
                'home_team': game.get('HomeTeam'),
                'stadium': game.get('StadiumID'),
                'channel': game.get('Channel'),
                'point_spread': game.get('PointSpread'),
                'over_under': game.get('OverUnder'),
                'forecast': game.get('ForecastDescription'),
                'forecast_temp': game.get('ForecastTempLow')
            }
            
            processed_data.append(processed_game)
            
        self.logger.info(f"Collected {len(processed_data)} NFL scheduled games")
        return processed_data
    
    def collect_injuries(self, season: str = None) -> List[Dict]:
        """
        Collect current NFL injury reports.
        
        Args:
            season: Season identifier (defaults to current season)
            
        Returns:
            List of player injuries
        """
        if season is None:
            season = self.current_season
            
        self.logger.info(f"Collecting NFL injury reports for season {season}")
        
        endpoint = self.endpoints.get('injuries', '')
        if not endpoint:
            self.logger.error("Injuries endpoint not found in configuration")
            return []
            
        url = self._format_endpoint(endpoint, season=season)
        data = self._make_api_request(url)
        
        if not data:
            self.logger.warning(f"No injury data retrieved for season {season}")
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
                'practice_status': injury.get('PracticeStatus'),
                'game_status': injury.get('GameStatus'),
                'last_update': injury.get('LastUpdate')[:10] if injury.get('LastUpdate') else None
            }
            
            processed_data.append(processed_injury)
            
        self.logger.info(f"Collected {len(processed_data)} NFL player injuries")
        return processed_data
    
    def collect_odds(self, date: str = None, week: str = None, season: str = None) -> List[Dict]:
        """
        Collect NFL betting odds for a specific week.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (not used directly for NFL)
            week: NFL week number (defaults to current week)
            season: Season identifier (defaults to current season)
            
        Returns:
            List of betting odds
        """
        if week is None:
            week = self.current_week
            
        if season is None:
            season = self.current_season
            
        self.logger.info(f"Collecting NFL betting odds for season {season}, week {week}")
        
        endpoint = self.endpoints.get('odds', '')
        if not endpoint:
            self.logger.error("Odds endpoint not found in configuration")
            return []
            
        url = self._format_endpoint(endpoint, season=season, week=week)
        data = self._make_api_request(url)
        
        if not data:
            self.logger.warning(f"No odds data retrieved for season {season}, week {week}")
            return []
            
        # Process and normalize the data
        processed_data = []
        for game_odds in data:
            processed_odds = {
                'game_id': game_odds.get('GameID'),
                'season': season,
                'week': week,
                'away_team': game_odds.get('AwayTeam'),
                'home_team': game_odds.get('HomeTeam'),
                'point_spread': game_odds.get('PointSpread'),
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
                        'over_payou<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>