"""
NBA data collector module for fetching NBA-specific statistics and data.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .base_collector import BaseDataCollector

class NBADataCollector(BaseDataCollector):
    """
    Data collector for NBA statistics and information.
    Implements the abstract methods defined in BaseDataCollector.
    """
    
    def __init__(self, config_path: str = None, api_key: str = None):
        """
        Initialize the NBA data collector.
        
        Args:
            config_path: Path to the configuration directory
            api_key: API key for the sports data provider (optional)
        """
        super().__init__('nba', config_path)
        
        # Set API key (from parameter, environment variable, or config file)
        self.api_key = api_key or os.environ.get('SPORTS_DATA_API_KEY', 'demo-key')
        
        # Get NBA-specific endpoints
        self.endpoints = self.sport_config.get('data_sources', {})
        
        # Determine current NBA season
        current_year = datetime.now().year
        current_month = datetime.now().month
        # NBA season spans two years and typically starts in October
        if current_month >= 10:
            self.current_season = f"{current_year}-{current_year + 1}"
        else:
            self.current_season = f"{current_year - 1}-{current_year}"
            
        self.logger.info(f"NBA data collector initialized for season {self.current_season}")
    
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
        Collect NBA player statistics for a specific date.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to yesterday)
            
        Returns:
            List of player statistics
        """
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
        self.logger.info(f"Collecting NBA player stats for {date}")
        
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
                'minutes': player_game.get('Minutes'),
                'stats': {
                    'points': player_game.get('Points'),
                    'rebounds': player_game.get('Rebounds'),
                    'assists': player_game.get('Assists'),
                    'steals': player_game.get('Steals'),
                    'blocks': player_game.get('BlockedShots'),
                    'three_pointers_made': player_game.get('ThreePointersMade'),
                    'field_goals_made': player_game.get('FieldGoalsMade'),
                    'field_goals_attempted': player_game.get('FieldGoalsAttempted'),
                    'free_throws_made': player_game.get('FreeThrowsMade'),
                    'free_throws_attempted': player_game.get('FreeThrowsAttempted'),
                    'turnovers': player_game.get('Turnovers'),
                    'personal_fouls': player_game.get('PersonalFouls')
                },
                'fantasy_points': player_game.get('FantasyPoints'),
                'plus_minus': player_game.get('PlusMinus')
            }
            
            # Calculate combined stats
            processed_player['stats']['points_rebounds_assists'] = (
                processed_player['stats']['points'] + 
                processed_player['stats']['rebounds'] + 
                processed_player['stats']['assists']
            )
            
            processed_data.append(processed_player)
            
        self.logger.info(f"Collected stats for {len(processed_data)} NBA players")
        return processed_data
    
    def collect_team_stats(self, date: str = None) -> List[Dict]:
        """
        Collect NBA team statistics for a specific date.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to yesterday)
            
        Returns:
            List of team statistics
        """
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
        self.logger.info(f"Collecting NBA team stats for {date}")
        
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
                    'points': team_game.get('Points'),
                    'rebounds': team_game.get('Rebounds'),
                    'assists': team_game.get('Assists'),
                    'steals': team_game.get('Steals'),
                    'blocks': team_game.get('BlockedShots'),
                    'turnovers': team_game.get('Turnovers'),
                    'field_goal_percentage': team_game.get('FieldGoalPercentage'),
                    'three_point_percentage': team_game.get('ThreePointPercentage'),
                    'free_throw_percentage': team_game.get('FreeThrowPercentage'),
                    'possessions': team_game.get('Possessions')
                },
                'win_loss': team_game.get('WinOrLoss'),
                'point_spread': team_game.get('PointSpread'),
                'over_under': team_game.get('OverUnder')
            }
            
            # Calculate pace and efficiency metrics
            if processed_team['stats'].get('possessions'):
                processed_team['stats']['pace'] = processed_team['stats']['possessions'] * 48 / 40  # Normalize to 48 minutes
                processed_team['stats']['offensive_rating'] = processed_team['stats']['points'] * 100 / processed_team['stats']['possessions']
                
            processed_data.append(processed_team)
            
        self.logger.info(f"Collected stats for {len(processed_data)} NBA teams")
        return processed_data
    
    def collect_schedules(self, season: str = None) -> List[Dict]:
        """
        Collect NBA game schedules for a specific season.
        
        Args:
            season: Season identifier (defaults to current season)
            
        Returns:
            List of scheduled games
        """
        if season is None:
            season = self.current_season
            
        self.logger.info(f"Collecting NBA schedules for season {season}")
        
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
                'arena': game.get('Arena'),
                'start_time': game.get('DateTime'),
                'channel': game.get('Channel')
            }
            
            processed_data.append(processed_game)
            
        self.logger.info(f"Collected {len(processed_data)} NBA scheduled games")
        return processed_data
    
    def collect_injuries(self) -> List[Dict]:
        """
        Collect current NBA injury reports.
        
        Returns:
            List of player injuries
        """
        self.logger.info("Collecting NBA injury reports")
        
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
                'status': injury.get('InjuryStatus'),
                'start_date': injury.get('StartDate')[:10] if injury.get('StartDate') else None,
                'expected_return': injury.get('ExpectedReturn')
            }
            
            processed_data.append(processed_injury)
            
        self.logger.info(f"Collected {len(processed_data)} NBA player injuries")
        return processed_data
    
    def collect_odds(self, date: str = None) -> List[Dict]:
        """
        Collect NBA betting odds for a specific date.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to today)
            
        Returns:
            List of betting odds
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        self.logger.info(f"Collecting NBA betting odds for {date}")
        
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
                        'over_payout': prop.get('OverPayout'),
                        'under_payout': prop.get('UnderPayout')
                    }
                    player_props.append(player_prop)
                
                processed_odds['player_props'] = player_props
            
            processed_data.append(processed_odds)
            
        self.logger.info(f"Collected odds for {len(processed_data)} NBA games")
        return processed_data
    
    def collect_prizepicks_lines(self, date: str = None) -> List[Dict]:
        """
        Collect PrizePicks lines for NBA players.
        This is a custom method specific to NBA collector.
        
        Args:
            date: Date string in format 'YYYY-MM-DD' (defaults to today)
            
        Returns:
            List of PrizePicks lines
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        self.logger.info(f"Collecting NBA PrizePicks lines for {date}")
        
        # This would typically use a different API or web scraping
        # For demonstration, we'll implement a placeholder that would be replaced with actual API calls
        
        # Example implementation using web scraping (to be implemented)
        prizepicks_data = []
        
        # Log that this is a placeholder
        self.logger.warning("PrizePicks data collection not fully implemented - requires web scraping or API access")
        
        return prizepicks_data
    
    def collect_news_and_sentiment(self, days: int = 3) -> List[Dict]:
        """
        Collect recent news and social media sentiment about NBA players.
        This is a custom method specific to NBA collector.
        
        Args:
            days: Number of days to look back for news
            
        Returns:
            List of news and sentiment data
        """
        self.logger.info(f"Collecting NBA news and sentiment for the past {days} days")
        
        # This would typically use news APIs and social media APIs
        # For demonstration, we'll implement a placeholder that would be replaced with actual API calls
        
        # Example implementation using news API and sentiment analysis (to be implemented)
        news_data = []
        
        # Log that this is a placeholder
        self.logger.warning("News and sentiment collection not fully implemented - requires news API and NLP processing")
        
        return news_data
