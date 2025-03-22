"""
Soccer data collector module for fetching soccer-specific statistics and data.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .base_collector import BaseDataCollector

class SoccerDataCollector(BaseDataCollector):
    """
    Data collector for soccer statistics and information.
    Implements the abstract methods defined in BaseDataCollector.
    """
    
    def __init__(self, config_path: str = None, api_key: str = None):
        """
        Initialize the soccer data collector.
        
        Args:
            config_path: Path to the configuration directory
            api_key: API key for the sports data provider (optional)
        """
        super().__init__('soccer', config_path)
        
        # Set API key (from parameter, environment variable, or config file)
        self.api_key = api_key or os.environ.get('SPORTS_DATA_API_KEY', 'demo-key')
        
        # Get soccer-specific endpoints
        self.endpoints = self.sport_config.get('data_sources', {})
        
        # Soccer has multiple competitions/leagues with different seasons
        # For simplicity, we'll use the current year as the season
        self.current_season = str(datetime.now().year)
            
        self.logger.info(f"Soccer data collector initialized for season {self.current_season}")
    
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
        Collect soccer player statistics for a specific date.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to yesterday)
            
        Returns:
            List of player statistics
        """
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
        self.logger.info(f"Collecting soccer player stats for {date}")
        
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
                'competition': player_game.get('Competition'),
                'stats': {
                    'goals': player_game.get('Goals'),
                    'assists': player_game.get('Assists'),
                    'shots': player_game.get('Shots'),
                    'shots_on_target': player_game.get('ShotsOnTarget'),
                    'passes': player_game.get('Passes'),
                    'key_passes': player_game.get('KeyPasses'),
                    'pass_accuracy': player_game.get('PassAccuracy'),
                    'dribbles': player_game.get('Dribbles'),
                    'tackles': player_game.get('Tackles'),
                    'interceptions': player_game.get('Interceptions'),
                    'fouls_committed': player_game.get('FoulsCommitted'),
                    'fouls_drawn': player_game.get('FoulsDrawn'),
                    'yellow_cards': player_game.get('YellowCards'),
                    'red_cards': player_game.get('RedCards'),
                    'minutes_played': player_game.get('MinutesPlayed')
                },
                'fantasy_points': player_game.get('FantasyPoints')
            }
            
            # Calculate combined stats
            processed_player['stats']['goal_contributions'] = (
                processed_player['stats']['goals'] + 
                processed_player['stats']['assists']
            )
            
            processed_data.append(processed_player)
            
        self.logger.info(f"Collected stats for {len(processed_data)} soccer players")
        return processed_data
    
    def collect_team_stats(self, date: str = None) -> List[Dict]:
        """
        Collect soccer team statistics for a specific date.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to yesterday)
            
        Returns:
            List of team statistics
        """
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
        self.logger.info(f"Collecting soccer team stats for {date}")
        
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
                'competition': team_game.get('Competition'),
                'stats': {
                    'goals': team_game.get('Goals'),
                    'shots': team_game.get('Shots'),
                    'shots_on_target': team_game.get('ShotsOnTarget'),
                    'possession': team_game.get('Possession'),
                    'passes': team_game.get('Passes'),
                    'pass_accuracy': team_game.get('PassAccuracy'),
                    'corners': team_game.get('Corners'),
                    'offsides': team_game.get('Offsides'),
                    'fouls': team_game.get('Fouls'),
                    'yellow_cards': team_game.get('YellowCards'),
                    'red_cards': team_game.get('RedCards')
                },
                'result': team_game.get('Result'),
                'score': team_game.get('Score'),
                'expected_goals': team_game.get('ExpectedGoals')
            }
            
            # Calculate shooting efficiency
            if processed_team['stats'].get('shots') and processed_team['stats'].get('shots') > 0:
                processed_team['stats']['shot_accuracy'] = (
                    processed_team['stats']['shots_on_target'] / processed_team['stats']['shots']
                )
                
            processed_data.append(processed_team)
            
        self.logger.info(f"Collected stats for {len(processed_data)} soccer teams")
        return processed_data
    
    def collect_schedules(self, season: str = None) -> List[Dict]:
        """
        Collect soccer game schedules for competitions.
        
        Args:
            season: Season identifier (defaults to current season)
            
        Returns:
            List of scheduled games
        """
        self.logger.info("Collecting soccer competitions and schedules")
        
        endpoint = self.endpoints.get('schedules', '')
        if not endpoint:
            self.logger.error("Competitions endpoint not found in configuration")
            return []
            
        url = self._format_endpoint(endpoint)
        data = self._make_api_request(url)
        
        if not data:
            self.logger.warning("No competition data retrieved")
            return []
            
        # Process and normalize the data
        processed_data = []
        for competition in data:
            # For each competition, we would typically make another API call to get the schedule
            # For demonstration, we'll just process the competition data
            processed_competition = {
                'competition_id': competition.get('CompetitionID'),
                'name': competition.get('Name'),
                'league': competition.get('League'),
                'season': competition.get('Season'),
                'season_type': competition.get('SeasonType'),
                'start_date': competition.get('StartDate')[:10] if competition.get('StartDate') else None,
                'end_date': competition.get('EndDate')[:10] if competition.get('EndDate') else None,
                'teams': competition.get('Teams', [])
            }
            
            processed_data.append(processed_competition)
            
        self.logger.info(f"Collected {len(processed_data)} soccer competitions")
        return processed_data
    
    def collect_injuries(self) -> List[Dict]:
        """
        Collect current soccer injury reports.
        
        Returns:
            List of player injuries
        """
        self.logger.info("Collecting soccer injury reports")
        
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
            
        self.logger.info(f"Collected {len(processed_data)} soccer player injuries")
        return processed_data
    
    def collect_odds(self, date: str = None) -> List[Dict]:
        """
        Collect soccer betting odds for a specific date.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to today)
            
        Returns:
            List of betting odds
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        self.logger.info(f"Collecting soccer betting odds for {date}")
        
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
                'competition': game_odds.get('Competition'),
                'away_team': game_odds.get('AwayTeam'),
                'home_team': game_odds.get('HomeTeam'),
                'draw_money_line': game_odds.get('DrawMoneyLine'),
                'away_money_line': game_odds.get('AwayMoneyLine'),
                'home_money_line': game_odds.get('HomeMoneyLine'),
                'over_under': game_odds.get('OverUnder'),
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
            
        self.logger.info(f"Collected odds for {len(processed_data)} soccer games")
        return processed_data
    
    def _collect_weather_impl(self, date: str = None) -> List[Dict]:
        """
        Collect weather data for soccer games.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to today)
            
        Returns:
            List of weather data
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        self.logger.info(f"Collecting soccer weather data for {date}")
        
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
                'competition': game_weather.get('Competition'),
                'away_team': game_weather.get('AwayTeam'),
                'home_team': game_weather.get('HomeTeam'),
                'stadium': game_weather.get('Stadium'),
                'temperature': game_weather.get('Temperature'),
                'humidity': game_weather.get('Humidity'),
                'wind_speed': game_weather.get('WindSpeed'),
                'wind_direction': game_weather.get('WindDirection'),
                'precipitation': game_weather.get('Precipitation'),
                'weather_description': game_weather.get('Description')
            }
            
            processed_data.append(processed_weather)
            
        self.logger.info(f"Collected weather data for {len(processed_data)} soccer games")
        return processed_dat<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>