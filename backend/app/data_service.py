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
    """Efficient data fetching, caching, and structuring service with intelligent API optimization"""
    
    def __init__(self):
        # Tiered caching strategy
        self.basic_cache_ttl = 300  # 5 minutes for basic match data
        self.detailed_cache_ttl = 180  # 3 minutes for detailed stats
        self.live_cache_ttl = 60  # 1 minute for live matches
        self.batch_size = 15  # Process matches in batches
        
        # API call optimization
        self.max_concurrent_requests = 5
        self.request_delay = 0.1  # 100ms between requests
        self.last_request_time = 0
        
        # Smart refresh intervals
        self.live_match_refresh_interval = 30  # 30 seconds for live matches
        self.finished_match_refresh_interval = 300  # 5 minutes for finished matches
        
    async def get_live_matches_efficient(self) -> List[MatchData]:
        """Get live matches with intelligent caching and minimal API calls"""
        try:
            # Get basic live matches
            raw_matches = await sports_api.get_live_matches()
            if not raw_matches:
                return []
            
            # Process in optimized batches
            match_data_list = []
            for i in range(0, len(raw_matches), self.batch_size):
                batch = raw_matches[i:i + self.batch_size]
                batch_data = await self._process_match_batch_optimized(batch, is_live=True)
                match_data_list.extend(batch_data)
            
            logger.info(f"📊 Processed {len(match_data_list)} live matches with optimized caching")
            return match_data_list
            
        except Exception as e:
            logger.error(f"Error fetching live matches: {e}")
            return []
    
    async def get_todays_matches_efficient(self) -> List[MatchData]:
        """Get today's matches with intelligent caching and minimal API calls"""
        try:
            # Get basic today's matches
            raw_matches = await sports_api.get_todays_matches()
            if not raw_matches:
                return []
            
            # Process in optimized batches
            match_data_list = []
            for i in range(0, len(raw_matches), self.batch_size):
                batch = raw_matches[i:i + self.batch_size]
                batch_data = await self._process_match_batch_optimized(batch, is_live=False)
                match_data_list.extend(batch_data)
            
            logger.info(f"📅 Processed {len(match_data_list)} today's matches with optimized caching")
            return match_data_list
            
        except Exception as e:
            logger.error(f"Error fetching today's matches: {e}")
            return []
    
    async def _process_match_batch_optimized(self, matches: List[Dict], is_live: bool = False) -> List[MatchData]:
        """Process a batch of matches with intelligent caching and API optimization"""
        tasks = []
        for match in matches:
            task = self._process_single_match_optimized(match, is_live)
            tasks.append(task)
        
        # Execute with concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        async def controlled_task(task):
            async with semaphore:
                await asyncio.sleep(self.request_delay)  # Rate limiting
                return await task
        
        controlled_tasks = [controlled_task(task) for task in tasks]
        results = await asyncio.gather(*controlled_tasks, return_exceptions=True)
        
        # Filter out errors and return valid results
        valid_results = []
        for result in results:
            if isinstance(result, MatchData):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Error processing match: {result}")
        
        return valid_results
    
    async def _process_single_match_optimized(self, match: Dict, is_live: bool = False) -> MatchData:
        """Process a single match with intelligent caching strategy"""
        external_id = str(match.get("fixture", {}).get("id", ""))
        if not external_id:
            raise ValueError("No external ID found in match data")
        
        # Determine cache TTL based on match status
        cache_ttl = self._get_cache_ttl_for_match(match, is_live)
        
        # Check cache first with appropriate TTL
        cached_data = await self._get_cached_match_with_ttl(external_id, cache_ttl)
        if cached_data:
            logger.debug(f"📋 Using cached data for match {external_id}")
            return self._create_match_data_from_cache(cached_data)
        
        # Fetch fresh data with appropriate detail level
        detail_level = self._get_detail_level_for_match(match, is_live)
        enhanced_data = await self._fetch_match_data_with_level(match, detail_level)
        
        # Cache the result with appropriate TTL
        await self._cache_match_data_with_ttl(external_id, enhanced_data, cache_ttl)
        
        # Store metrics for alert processing
        await self._store_match_metrics(external_id, enhanced_data)
        
        return self._create_match_data_from_raw(enhanced_data)
    
    def _get_cache_ttl_for_match(self, match: Dict, is_live: bool) -> int:
        """Determine appropriate cache TTL based on match status"""
        status = match.get("fixture", {}).get("status", {}).get("short", "").upper()
        
        if is_live or status in ["1H", "HT", "2H", "ET", "P", "BT"]:
            return self.live_cache_ttl  # 1 minute for live matches
        elif status in ["FT", "AET", "PEN"]:
            return self.basic_cache_ttl  # 5 minutes for finished matches
        elif status in ["NS", "TBD", "PST"]:
            return self.basic_cache_ttl * 2  # 10 minutes for scheduled matches
        else:
            return self.basic_cache_ttl
    
    def _get_detail_level_for_match(self, match: Dict, is_live: bool) -> str:
        """Determine appropriate detail level for API calls"""
        status = match.get("fixture", {}).get("status", {}).get("short", "").upper()
        
        if is_live or status in ["1H", "HT", "2H", "ET", "P", "BT"]:
            return "full"  # Full details for live matches
        elif status in ["FT", "AET", "PEN"]:
            return "detailed"  # Detailed stats for finished matches
        else:
            return "basic"  # Basic info for scheduled matches
    
    async def _get_cached_match_with_ttl(self, external_id: str, cache_ttl: int) -> Optional[MatchCache]:
        """Get cached match data with custom TTL"""
        db = next(get_db())
        try:
            cache_entry = db.query(MatchCache).filter(
                MatchCache.external_id == external_id
            ).first()
            
            if cache_entry:
                # Check if cache is still valid with custom TTL
                age_seconds = (datetime.utcnow() - cache_entry.last_updated).total_seconds()
                if age_seconds < cache_ttl:
                    return cache_entry
            
            return None
        finally:
            db.close()
    
    async def _cache_match_data_with_ttl(self, external_id: str, match_data: Dict, cache_ttl: int):
        """Cache match data with custom TTL"""
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
                cache_entry.cache_ttl = cache_ttl
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
                    cache_ttl=cache_ttl
                )
                db.add(cache_entry)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error caching match data: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def _fetch_match_data_with_level(self, match: Dict, detail_level: str) -> Dict:
        """Fetch match data with appropriate detail level to minimize API calls"""
        fixture_id = match.get("fixture", {}).get("id")
        if not fixture_id:
            return match
        
        try:
            if detail_level == "full":
                # Full details for live matches
                return await self._fetch_enhanced_match_data(match)
            elif detail_level == "detailed":
                # Detailed stats for finished matches
                return await self._fetch_detailed_match_data(match)
            else:
                # Basic info for scheduled matches
                return await self._fetch_basic_match_data(match)
                
        except Exception as e:
            logger.error(f"Error fetching match data for {fixture_id}: {e}")
            return match
    
    async def _fetch_basic_match_data(self, match: Dict) -> Dict:
        """Fetch basic match data (minimal API calls)"""
        # Just return the basic match data with default metrics
        enhanced_match = match.copy()
        enhanced_match["alert_metrics"] = self._extract_basic_metrics(match)
        return enhanced_match
    
    async def _fetch_detailed_match_data(self, match: Dict) -> Dict:
        """Fetch detailed match data (moderate API calls)"""
        fixture_id = match.get("fixture", {}).get("id")
        
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                # Get statistics and events (skip lineups for efficiency)
                stats = await self._get_match_stats_optimized(fixture_id, client)
                events = await self._get_match_events_optimized(fixture_id, client)
                
                enhanced_match = match.copy()
                enhanced_match["detailed_stats"] = stats or []
                enhanced_match["events"] = events or []
                enhanced_match["lineups"] = []  # Skip lineups for efficiency
                enhanced_match["alert_metrics"] = self._extract_alert_metrics(match, stats, events)
                
                return enhanced_match
        except Exception as e:
            logger.error(f"Error fetching detailed match data for {fixture_id}: {e}")
            return await self._fetch_basic_match_data(match)
    
    async def _fetch_enhanced_match_data(self, match: Dict) -> Dict:
        """Fetch enhanced match data (full API calls for live matches)"""
        # Use the existing sports API but with better error handling
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                enhanced_match = await sports_api._enhance_match_data(match, client)
                return enhanced_match
        except Exception as e:
            logger.error(f"Error enhancing match data for {match.get('fixture', {}).get('id')}: {e}")
            # Fall back to detailed match data if enhancement fails
            return await self._fetch_detailed_match_data(match)
    
    async def _get_match_stats_optimized(self, fixture_id: int, client) -> List:
        """Get match statistics with error handling"""
        try:
            response = await client.get(
                f"{sports_api.base_url}/fixtures/statistics",
                headers=sports_api.headers,
                params={"fixture": fixture_id},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", [])
        except Exception as e:
            logger.warning(f"Failed to fetch stats for fixture {fixture_id}: {e}")
            return []
    
    async def _get_match_events_optimized(self, fixture_id: int, client) -> List:
        """Get match events with error handling"""
        try:
            response = await client.get(
                f"{sports_api.base_url}/fixtures/events",
                headers=sports_api.headers,
                params={"fixture": fixture_id},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", [])
        except Exception as e:
            logger.warning(f"Failed to fetch events for fixture {fixture_id}: {e}")
            return []
    
    def _extract_basic_metrics(self, match: Dict) -> Dict:
        """Extract basic metrics without API calls"""
        return {
            "basic": {
                "home_score": match.get("goals", {}).get("home", 0) or 0,
                "away_score": match.get("goals", {}).get("away", 0) or 0,
                "score_difference": abs((match.get("goals", {}).get("home", 0) or 0) - (match.get("goals", {}).get("away", 0) or 0)),
                "total_goals": (match.get("goals", {}).get("home", 0) or 0) + (match.get("goals", {}).get("away", 0) or 0),
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
            "xg": {"home": 0.0, "away": 0.0},
            "pressure": {"home": 0, "away": 0},
            "momentum": {"home": 0, "away": 0},
        }
    
    def _extract_alert_metrics(self, match: Dict, stats: Optional[List] = None, events: Optional[List] = None) -> Dict:
        """Extract alert metrics from match data"""
        # Use the existing sports API method
        return sports_api._extract_alert_metrics(match, stats, events)
    
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
            # Use the longest cache TTL to ensure we don't delete entries that might still be valid
            max_cache_ttl = max(self.basic_cache_ttl, self.detailed_cache_ttl, self.live_cache_ttl)
            expired_entries = db.query(MatchCache).filter(
                MatchCache.last_updated < datetime.utcnow() - timedelta(seconds=max_cache_ttl)
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