import os
import httpx
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv
from .core.config import settings

load_dotenv()

class SportsAPIService:
    def __init__(self):
        self.api_key = settings.API_FOOTBALL_KEY
        self.base_url = settings.SPORTS_API_BASE_URL
        self.headers = {
            "x-apisports-key": self.api_key
        }
        
    async def get_live_matches(self) -> List[Dict]:
        """Get currently live matches with detailed stats"""
        if not self.api_key:
            return []
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/fixtures",
                    headers=self.headers,
                    params={"live": "all"}
                )
                response.raise_for_status()
                data = response.json()
                matches = data.get("response", [])
                
                print(f"Found {len(matches)} live matches")
                
                # Return basic matches - enhancement will be handled by data service
                return matches
            except Exception as e:
                print(f"Error fetching live matches: {e}")
                return []
    
    async def get_todays_matches(self) -> List[Dict]:
        """Get today's matches with detailed stats"""
        if not self.api_key:
            return []
            
        today = datetime.now().strftime("%Y-%m-%d")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/fixtures",
                    headers=self.headers,
                    params={"date": today}
                )
                response.raise_for_status()
                data = response.json()
                matches = data.get("response", [])
                
                # Return basic matches - enhancement will be handled by data service
                return matches
            except Exception as e:
                print(f"Error fetching today's matches: {e}")
                return []

    async def get_match_statistics(self, fixture_id: int) -> Optional[Dict]:
        """Get detailed statistics for a specific match"""
        if not self.api_key:
            return None
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/fixtures/statistics",
                    headers=self.headers,
                    params={"fixture": fixture_id}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", [])
            except Exception as e:
                print(f"Error fetching match statistics: {e}")
                return None

    async def get_match_events(self, fixture_id: int) -> Optional[Dict]:
        """Get match events (goals, cards, substitutions)"""
        if not self.api_key:
            return None
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/fixtures/events",
                    headers=self.headers,
                    params={"fixture": fixture_id}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", [])
            except Exception as e:
                print(f"Error fetching match events: {e}")
                return None

    async def get_match_lineups(self, fixture_id: int) -> Optional[Dict]:
        """Get match lineups and formations"""
        if not self.api_key:
            return None
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/fixtures/lineups",
                    headers=self.headers,
                    params={"fixture": fixture_id}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", [])
            except Exception as e:
                print(f"Error fetching match lineups: {e}")
                return None

    async def _enhance_match_data(self, match: Dict, client: httpx.AsyncClient) -> Dict:
        """Enhance match data with detailed statistics"""
        fixture_id = match.get("fixture", {}).get("id")
        if not fixture_id:
            return match

        # Get detailed stats
        stats = await self._get_match_stats(fixture_id, client)
        events = await self._get_match_events(fixture_id, client)
        lineups = await self._get_match_lineups(fixture_id, client)

        # Enhance the match data
        enhanced_match = match.copy()
        enhanced_match["detailed_stats"] = stats or []
        enhanced_match["events"] = events or []
        enhanced_match["lineups"] = lineups or []
        enhanced_match["alert_metrics"] = self._extract_alert_metrics(match, stats, events)

        return enhanced_match

    async def _get_match_stats(self, fixture_id: int, client: httpx.AsyncClient) -> List:
        """Get match statistics"""
        try:
            response = await client.get(
                f"{self.base_url}/fixtures/statistics",
                headers=self.headers,
                params={"fixture": fixture_id}
            )
            response.raise_for_status()
            data = response.json()
            result = data.get("response", [])
            return result if isinstance(result, list) else []
        except Exception as e:
            print(f"Error fetching stats for fixture {fixture_id}: {e}")
            return []

    async def _get_match_events(self, fixture_id: int, client: httpx.AsyncClient) -> List:
        """Get match events"""
        try:
            response = await client.get(
                f"{self.base_url}/fixtures/events",
                headers=self.headers,
                params={"fixture": fixture_id}
            )
            response.raise_for_status()
            data = response.json()
            result = data.get("response", [])
            return result if isinstance(result, list) else []
        except Exception as e:
            print(f"Error fetching events for fixture {fixture_id}: {e}")
            return []

    async def _get_match_lineups(self, fixture_id: int, client: httpx.AsyncClient) -> List:
        """Get match lineups"""
        try:
            response = await client.get(
                f"{self.base_url}/fixtures/lineups",
                headers=self.headers,
                params={"fixture": fixture_id}
            )
            response.raise_for_status()
            data = response.json()
            result = data.get("response", [])
            return result if isinstance(result, list) else []
        except Exception as e:
            print(f"Error fetching lineups for fixture {fixture_id}: {e}")
            return []

    def _extract_alert_metrics(self, match: Dict, stats: Optional[List] = None, events: Optional[List] = None) -> Dict:
        """Extract key metrics for alert creation"""
        metrics = {
            "basic": {
                "home_score": match.get("goals", {}).get("home", 0),
                "away_score": match.get("goals", {}).get("away", 0),
                "score_difference": abs(match.get("goals", {}).get("home", 0) - match.get("goals", {}).get("away", 0)),
                "total_goals": match.get("goals", {}).get("home", 0) + match.get("goals", {}).get("away", 0),
                "match_status": match.get("fixture", {}).get("status", {}).get("short", "Unknown"),
                "elapsed_time": match.get("fixture", {}).get("status", {}).get("elapsed", 0),
                "referee": match.get("fixture", {}).get("referee", "Unknown"),
                "venue": match.get("fixture", {}).get("venue", {}).get("name", "Unknown"),
                "weather": match.get("fixture", {}).get("weather", {}),
            },
            "possession": {"home": 50, "away": 50},
            "shots": {"home": 0, "away": 0, "home_on_target": 0, "away_on_target": 0},
            "cards": {"home_yellow": 0, "away_yellow": 0, "home_red": 0, "away_red": 0},
            "corners": {"home": 0, "away": 0},
            "fouls": {"home": 0, "away": 0},
            "offsides": {"home": 0, "away": 0},
            "xg": {"home": 0.0, "away": 0.0},
            "pressure": {"home": 0, "away": 0},
            "momentum": {"home": 0, "away": 0},
            "final_third_possession": {"home": 0, "away": 0},
            "passes": {"home": 0, "away": 0, "home_accuracy": 0, "away_accuracy": 0},
            "tackles": {"home": 0, "away": 0},
            "clearances": {"home": 0, "away": 0},
            "saves": {"home": 0, "away": 0},
            "goal_kicks": {"home": 0, "away": 0},
            "throw_ins": {"home": 0, "away": 0},
            "injuries": {"home": 0, "away": 0},
            "substitutions": {"home": 0, "away": 0},
        }

        # Extract from detailed stats
        if stats and isinstance(stats, list):
            for team_stats in stats:
                team_id = team_stats.get("team", {}).get("id")
                is_home = team_id == match.get("teams", {}).get("home", {}).get("id")
                team_key = "home" if is_home else "away"
                
                statistics = team_stats.get("statistics", [])
                for stat in statistics:
                    stat_type = stat.get("type")
                    stat_value = stat.get("value")
                    
                    # Ensure stat_value is a string or number, not a dict
                    if isinstance(stat_value, dict):
                        stat_value = str(stat_value)
                    
                    if stat_type == "Ball Possession":
                        percentage = int(stat_value.replace("%", "")) if stat_value and isinstance(stat_value, str) else 50
                        metrics["possession"][team_key] = percentage
                    elif stat_type == "Total Shots":
                        metrics["shots"][team_key] = int(stat_value) if stat_value else 0
                    elif stat_type == "Shots on Goal":
                        metrics["shots"][f"{team_key}_on_target"] = int(stat_value) if stat_value else 0
                    elif stat_type == "Corner Kicks":
                        metrics["corners"][team_key] = int(stat_value) if stat_value else 0
                    elif stat_type == "Fouls":
                        metrics["fouls"][team_key] = int(stat_value) if stat_value else 0
                    elif stat_type == "Yellow Cards":
                        metrics["cards"][f"{team_key}_yellow"] = int(stat_value) if stat_value else 0
                    elif stat_type == "Red Cards":
                        metrics["cards"][f"{team_key}_red"] = int(stat_value) if stat_value else 0
                    elif stat_type == "Offsides":
                        metrics["offsides"][team_key] = int(stat_value) if stat_value else 0
                    elif stat_type == "Passes":
                        metrics["passes"][team_key] = int(stat_value) if stat_value else 0
                    elif stat_type == "Passes %":
                        percentage = int(stat_value.replace("%", "")) if stat_value and isinstance(stat_value, str) else 0
                        metrics["passes"][f"{team_key}_accuracy"] = percentage

        # Extract from events
        if events and isinstance(events, list):
            home_id = match.get("teams", {}).get("home", {}).get("id")
            away_id = match.get("teams", {}).get("away", {}).get("id")
            
            for event in events:
                team_id = event.get("team", {}).get("id")
                event_type = event.get("type")
                
                if team_id == home_id:
                    team_key = "home"
                elif team_id == away_id:
                    team_key = "away"
                else:
                    continue
                
                if event_type == "Goal":
                    # Goals are already in basic metrics
                    pass
                elif event_type == "Card":
                    card_type = event.get("detail", {}).get("type", "yellow")
                    if card_type == "red":
                        metrics["cards"][f"{team_key}_red"] += 1
                    else:
                        metrics["cards"][f"{team_key}_yellow"] += 1
                elif event_type == "Subst":
                    metrics["substitutions"][team_key] += 1

        return metrics

    def format_match_data(self, match: Dict) -> Dict:
        """Format match data for frontend consumption"""
        fixture = match.get("fixture", {})
        teams = match.get("teams", {})
        goals = match.get("goals", {})
        league = match.get("league", {})
        
        return {
            "id": fixture.get("id"),
            "external_id": str(fixture.get("id")),
            "home_team": teams.get("home", {}).get("name", "Unknown"),
            "away_team": teams.get("away", {}).get("name", "Unknown"),
            "home_team_id": teams.get("home", {}).get("id"),
            "away_team_id": teams.get("away", {}).get("id"),
            "league": league.get("name", "Unknown"),
            "league_id": league.get("id"),
            "start_time": fixture.get("date"),
            "status": fixture.get("status", {}).get("short", "Unknown"),
            "elapsed": fixture.get("status", {}).get("elapsed", 0),
            "home_score": goals.get("home", 0),
            "away_score": goals.get("away", 0),
            "venue": fixture.get("venue", {}).get("name", "Unknown"),
            "referee": fixture.get("referee", "Unknown"),
            "weather": fixture.get("weather", {}),
            "detailed_stats": match.get("detailed_stats", []),
            "events": match.get("events", []),
            "lineups": match.get("lineups", []),
            "alert_metrics": match.get("alert_metrics", {}),
        }

# Global instance
sports_api = SportsAPIService() 