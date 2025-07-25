import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session

from .sports_api import sports_api
from .database import get_db
from .models import MatchCache, MatchMetrics, Match

logger = logging.getLogger(__name__)

@dataclass
class MatchData:
    """Structured match data for efficient processing"""
    external_id: str
    home_team: str
    away_team: str
    league: str
    status: str
    elapsed_time: int
    home_score: int
    away_score: int
    start_time: datetime
    
    # Metrics
    home_possession: float = 50.0
    away_possession: float = 50.0
    home_shots: int = 0
    away_shots: int = 0
    home_shots_on_target: int = 0
    away_shots_on_target: int = 0
    home_corners: int = 0
    away_corners: int = 0
    home_fouls: int = 0
    away_fouls: int = 0
    home_yellow_cards: int = 0
    away_yellow_cards: int = 0
    home_red_cards: int = 0
    away_red_cards: int = 0
    home_xg: float = 0.0
    away_xg: float = 0.0
    home_pressure: float = 0.0
    away_pressure: float = 0.0
    home_momentum: float = 0.0
    away_momentum: float = 0.0
    
    # Context
    referee: Optional[str] = None
    venue: Optional[str] = None
    weather: Optional[Dict] = None
    
    # Raw data for reference
    raw_data: Optional[Dict] = None
    stats_data: Optional[List] = None
    events_data: Optional[List] = None
    lineups_data: Optional[List] = None

class DataService:
    """Efficient data fetching, caching, and structuring service"""
    
    def __init__(self):
        self.cache_ttl = 300  # 5 minutes
        self.batch_size = 10  # Process matches in batches
        
    async def get_live_matches_efficient(self) -> List[MatchData]:
        """Get live matches with efficient caching and batching"""
        try:
            # Get basic live matches
            raw_matches = await sports_api.get_live_matches()
            if not raw_matches:
                return []
            
            # Process in batches for efficiency
            match_data_list = []
            for i in range(0, len(raw_matches), self.batch_size):
                batch = raw_matches[i:i + self.batch_size]
                batch_data = await self._process_match_batch(batch)
                match_data_list.extend(batch_data)
            
            return match_data_list
            
        except Exception as e:
            logger.error(f"Error fetching live matches: {e}")
            return []
    
    async def get_todays_matches_efficient(self) -> List[MatchData]:
        """Get today's matches with efficient caching and batching"""
        try:
            # Get basic today's matches
            raw_matches = await sports_api.get_todays_matches()
            if not raw_matches:
                return []
            
            # Process in batches for efficiency
            match_data_list = []
            for i in range(0, len(raw_matches), self.batch_size):
                batch = raw_matches[i:i + self.batch_size]
                batch_data = await self._process_match_batch(batch)
                match_data_list.extend(batch_data)
            
            return match_data_list
            
        except Exception as e:
            logger.error(f"Error fetching today's matches: {e}")
            return []
    
    async def _process_match_batch(self, matches: List[Dict]) -> List[MatchData]:
        """Process a batch of matches efficiently"""
        tasks = []
        for match in matches:
            task = self._process_single_match(match)
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out errors and return valid results
        valid_results = []
        for result in results:
            if isinstance(result, MatchData):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Error processing match: {result}")
        
        return valid_results
    
    async def _process_single_match(self, match: Dict) -> MatchData:
        """Process a single match with caching"""
        external_id = str(match.get("fixture", {}).get("id", ""))
        if not external_id:
            raise ValueError("No external ID found in match data")
        
        # Check cache first
        cached_data = await self._get_cached_match(external_id)
        if cached_data and not cached_data.is_expired:
            return self._create_match_data_from_cache(cached_data)
        
        # Fetch fresh data if cache miss or expired
        enhanced_data = await self._fetch_enhanced_match_data(match)
        
        # Cache the result
        await self._cache_match_data(external_id, enhanced_data)
        
        # Store metrics for alert processing
        await self._store_match_metrics(external_id, enhanced_data)
        
        return self._create_match_data_from_raw(enhanced_data)
    
    async def _get_cached_match(self, external_id: str) -> Optional[MatchCache]:
        """Get cached match data"""
        db = next(get_db())
        try:
            return db.query(MatchCache).filter(
                MatchCache.external_id == external_id
            ).first()
        finally:
            db.close()
    
    async def _cache_match_data(self, external_id: str, match_data: Dict):
        """Cache match data"""
        db = next(get_db())
        try:
            # Check if cache entry exists
            cache_entry = db.query(MatchCache).filter(
                MatchCache.external_id == external_id
            ).first()
            
            if cache_entry:
                # Update existing entry
                cache_entry.match_data = match_data
                cache_entry.stats_data = match_data.get("detailed_stats")
                cache_entry.events_data = match_data.get("events")
                cache_entry.lineups_data = match_data.get("lineups")
                cache_entry.alert_metrics = match_data.get("alert_metrics")
                cache_entry.last_updated = datetime.utcnow()
            else:
                # Create new entry
                cache_entry = MatchCache(
                    external_id=external_id,
                    match_data=match_data,
                    stats_data=match_data.get("detailed_stats"),
                    events_data=match_data.get("events"),
                    lineups_data=match_data.get("lineups"),
                    alert_metrics=match_data.get("alert_metrics"),
                    last_updated=datetime.utcnow(),
                    cache_ttl=self.cache_ttl
                )
                db.add(cache_entry)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error caching match data: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def _fetch_enhanced_match_data(self, match: Dict) -> Dict:
        """Fetch enhanced match data with all details"""
        fixture_id = match.get("fixture", {}).get("id")
        if not fixture_id:
            return match
        
        # Use the existing sports API but with better error handling
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                enhanced_match = await sports_api._enhance_match_data(match, client)
                return enhanced_match
        except Exception as e:
            logger.error(f"Error enhancing match data for {fixture_id}: {e}")
            return match
    
    async def _store_match_metrics(self, external_id: str, match_data: Dict):
        """Store structured metrics for efficient alert processing"""
        try:
            metrics = self._extract_metrics_from_match(match_data)
            if not metrics:
                return
            
            db = next(get_db())
            try:
                # Create new metrics entry
                metrics_entry = MatchMetrics(
                    match_id=external_id,
                    timestamp=datetime.utcnow(),
                    **metrics
                )
                db.add(metrics_entry)
                db.commit()
                
            except Exception as e:
                logger.error(f"Error storing match metrics: {e}")
                db.rollback()
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error extracting metrics: {e}")
    
    def _extract_metrics_from_match(self, match_data: Dict) -> Optional[Dict]:
        """Extract structured metrics from match data"""
        try:
            fixture = match_data.get("fixture", {})
            goals = match_data.get("goals", {})
            teams = match_data.get("teams", {})
            alert_metrics = match_data.get("alert_metrics", {})
            
            metrics = {
                "home_score": goals.get("home", 0),
                "away_score": goals.get("away", 0),
                "elapsed_time": fixture.get("status", {}).get("elapsed", 0),
                "status": fixture.get("status", {}).get("short", "Unknown"),
                "referee": fixture.get("referee", "Unknown"),
                "venue": fixture.get("venue", {}).get("name", "Unknown"),
                "weather": fixture.get("weather"),
            }
            
            # Extract from alert metrics if available
            if alert_metrics:
                basic = alert_metrics.get("basic", {})
                possession = alert_metrics.get("possession", {})
                shots = alert_metrics.get("shots", {})
                corners = alert_metrics.get("corners", {})
                fouls = alert_metrics.get("fouls", {})
                cards = alert_metrics.get("cards", {})
                xg = alert_metrics.get("xg", {})
                pressure = alert_metrics.get("pressure", {})
                momentum = alert_metrics.get("momentum", {})
                
                metrics.update({
                    "home_possession": possession.get("home", 50.0),
                    "away_possession": possession.get("away", 50.0),
                    "home_shots": shots.get("home", 0),
                    "away_shots": shots.get("away", 0),
                    "home_shots_on_target": shots.get("home_on_target", 0),
                    "away_shots_on_target": shots.get("away_on_target", 0),
                    "home_corners": corners.get("home", 0),
                    "away_corners": corners.get("away", 0),
                    "home_fouls": fouls.get("home", 0),
                    "away_fouls": fouls.get("away", 0),
                    "home_yellow_cards": cards.get("home_yellow", 0),
                    "away_yellow_cards": cards.get("away_yellow", 0),
                    "home_red_cards": cards.get("home_red", 0),
                    "away_red_cards": cards.get("away_red", 0),
                    "home_xg": xg.get("home", 0.0),
                    "away_xg": xg.get("away", 0.0),
                    "home_pressure": pressure.get("home", 0.0),
                    "away_pressure": pressure.get("away", 0.0),
                    "home_momentum": momentum.get("home", 0.0),
                    "away_momentum": momentum.get("away", 0.0),
                })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error extracting metrics: {e}")
            return None
    
    def _create_match_data_from_cache(self, cache_entry: MatchCache) -> MatchData:
        """Create MatchData from cached entry"""
        match_data = cache_entry.match_data
        return self._create_match_data_from_raw(match_data)
    
    def _create_match_data_from_raw(self, match_data: Dict) -> MatchData:
        """Create MatchData from raw match data"""
        fixture = match_data.get("fixture", {})
        goals = match_data.get("goals", {})
        teams = match_data.get("teams", {})
        alert_metrics = match_data.get("alert_metrics", {})
        
        # Extract basic info
        external_id = str(fixture.get("id", ""))
        home_team = teams.get("home", {}).get("name", "Unknown")
        away_team = teams.get("away", {}).get("name", "Unknown")
        league = match_data.get("league", {}).get("name", "Unknown")
        status = fixture.get("status", {}).get("short", "Unknown")
        elapsed_time = fixture.get("status", {}).get("elapsed", 0) or 0
        home_score = goals.get("home", 0) or 0
        away_score = goals.get("away", 0) or 0
        
        # Parse start time
        start_time_str = fixture.get("date")
        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00')) if start_time_str else datetime.utcnow()
        
        # Create MatchData object
        match_data_obj = MatchData(
            external_id=external_id,
            home_team=home_team,
            away_team=away_team,
            league=league,
            status=status,
            elapsed_time=elapsed_time or 0,
            home_score=home_score or 0,
            away_score=away_score or 0,
            start_time=start_time,
            raw_data=match_data,
            stats_data=match_data.get("detailed_stats"),
            events_data=match_data.get("events"),
            lineups_data=match_data.get("lineups")
        )
        
        # Extract metrics if available
        if alert_metrics:
            basic = alert_metrics.get("basic", {})
            possession = alert_metrics.get("possession", {})
            shots = alert_metrics.get("shots", {})
            corners = alert_metrics.get("corners", {})
            fouls = alert_metrics.get("fouls", {})
            cards = alert_metrics.get("cards", {})
            xg = alert_metrics.get("xg", {})
            pressure = alert_metrics.get("pressure", {})
            momentum = alert_metrics.get("momentum", {})
            
            match_data_obj.home_possession = possession.get("home", 50.0)
            match_data_obj.away_possession = possession.get("away", 50.0)
            match_data_obj.home_shots = shots.get("home", 0)
            match_data_obj.away_shots = shots.get("away", 0)
            match_data_obj.home_shots_on_target = shots.get("home_on_target", 0)
            match_data_obj.away_shots_on_target = shots.get("away_on_target", 0)
            match_data_obj.home_corners = corners.get("home", 0)
            match_data_obj.away_corners = corners.get("away", 0)
            match_data_obj.home_fouls = fouls.get("home", 0)
            match_data_obj.away_fouls = fouls.get("away", 0)
            match_data_obj.home_yellow_cards = cards.get("home_yellow", 0)
            match_data_obj.away_yellow_cards = cards.get("away_yellow", 0)
            match_data_obj.home_red_cards = cards.get("home_red", 0)
            match_data_obj.away_red_cards = cards.get("away_red", 0)
            match_data_obj.home_xg = xg.get("home", 0.0)
            match_data_obj.away_xg = xg.get("away", 0.0)
            match_data_obj.home_pressure = pressure.get("home", 0.0)
            match_data_obj.away_pressure = pressure.get("away", 0.0)
            match_data_obj.home_momentum = momentum.get("home", 0.0)
            match_data_obj.away_momentum = momentum.get("away", 0.0)
            match_data_obj.referee = basic.get("referee", "Unknown")
            match_data_obj.venue = basic.get("venue", "Unknown")
            match_data_obj.weather = basic.get("weather")
        
        return match_data_obj
    
    async def cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        db = next(get_db())
        try:
            expired_entries = db.query(MatchCache).filter(
                MatchCache.last_updated < datetime.utcnow() - timedelta(seconds=self.cache_ttl)
            ).all()
            
            for entry in expired_entries:
                db.delete(entry)
            
            db.commit()
            logger.info(f"Cleaned up {len(expired_entries)} expired cache entries")
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            db.rollback()
        finally:
            db.close()

# Global instance
data_service = DataService() 