import os
import httpx
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv

load_dotenv()

class SportsAPIService:
    def __init__(self):
        self.api_key = os.getenv("API_FOOTBALL_KEY")
        # Direct API-Football endpoint (no longer RapidAPI)
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-apisports-key": self.api_key
        }
        
    async def get_live_matches(self) -> List[Dict]:
        """Get currently live matches"""
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
                return data.get("response", [])
            except Exception as e:
                print(f"Error fetching live matches: {e}")
                return []
    
    async def get_todays_matches(self) -> List[Dict]:
        """Get today's matches"""
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
                return data.get("response", [])
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
    
    async def get_league_matches(self, league_id: int, season: int = 2024) -> List[Dict]:
        """Get matches for a specific league and season"""
        if not self.api_key:
            return []
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/fixtures",
                    headers=self.headers,
                    params={"league": league_id, "season": season}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", [])
            except Exception as e:
                print(f"Error fetching league matches: {e}")
                return []
    
    def format_match_data(self, match_data: Dict) -> Dict:
        """Format raw API data into our standard format"""
        fixture = match_data.get("fixture", {})
        teams = match_data.get("teams", {})
        goals = match_data.get("goals", {})
        league = match_data.get("league", {})
        
        return {
            "external_id": str(fixture.get("id")),
            "home_team": teams.get("home", {}).get("name", ""),
            "away_team": teams.get("away", {}).get("name", ""),
            "league": league.get("name", ""),
            "start_time": fixture.get("date"),
            "status": fixture.get("status", {}).get("short", ""),
            "home_score": goals.get("home") or 0,
            "away_score": goals.get("away") or 0,
            "venue": fixture.get("venue", {}).get("name", ""),
            "referee": fixture.get("referee", ""),
            "elapsed": fixture.get("status", {}).get("elapsed", 0)
        }

# Global instance
sports_api = SportsAPIService() 