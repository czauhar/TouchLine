import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session

from .sports_api import sports_api
from .database import get_db
from .models import MatchCache, MatchMetrics, Match
from .cache_service import cache_service

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
    
    # Raw data for reference - optimized for memory
    raw_data: Optional[Dict] = None
    stats_data: Optional[List] = None
    events_data: Optional[List] = None
    lineups_data: Optional[List] = None
    
    def __post_init__(self):
        """Optimize memory usage after initialization"""
        # Only keep essential raw data, remove large objects
        if self.raw_data:
            # Keep only essential fields to reduce memory footprint
            essential_fields = ['fixture', 'teams', 'goals', 'league']
            self.raw_data = {k: v for k, v in self.raw_data.items() if k in essential_fields}
        
        # Limit stats and events data size
        if self.stats_data and len(self.stats_data) > 50:
            self.stats_data = self.stats_data[:50]
        
        if self.events_data and len(self.events_data) > 100:
            self.events_data = self.events_data[:100]

class DataService:
    """Efficient data fetching, caching, and structuring service with intelligent API optimization"""
    
    def __init__(self):
        # Tiered caching strategy - optimized for API efficiency
        self.basic_cache_ttl = 600  # 10 minutes for basic match data (increased)
        self.detailed_cache_ttl = 300  # 5 minutes for detailed stats (increased)
        self.live_cache_ttl = 60  # 1 minute for live matches (keep fast)
        self.todays_cache_ttl = 1800  # 30 minutes for today's matches (much longer)
        self.batch_size = 10  # Smaller batches for better rate limiting
        
        # API call optimization - balanced for performance
        self.max_concurrent_requests = 5  # More reasonable
        self.request_delay = 0.1  # 100ms between requests (reduced)
        self.last_request_time = 0
        self.api_call_count = 0
        self.api_call_limit = 300  # Higher limit for better performance
        
        # Smart refresh intervals
        self.live_match_refresh_interval = 30  # 30 seconds for live matches
        self.finished_match_refresh_interval = 300  # 5 minutes for finished matches
        
        # Memory optimization - more aggressive settings
        self.last_cleanup = time.time()
        self.cleanup_interval = 60  # 1 minute (reduced from 5 minutes)
        self.max_cache_entries = 500  # Reduced from 1000 to save memory
    
    async def _rate_limit_check(self):
        """Check and enforce rate limiting"""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.last_request_time > 60:
            self.api_call_count = 0
            self.last_request_time = current_time
        
        # Check if we're approaching the limit
        if self.api_call_count >= self.api_call_limit:
            wait_time = 60 - (current_time - self.last_request_time)
            if wait_time > 0:
                logger.warning(f"Rate limit reached, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                self.api_call_count = 0
                self.last_request_time = time.time()
        
        # Increment counter
        self.api_call_count += 1
        
        # Add delay between requests
        await asyncio.sleep(self.request_delay)
        
    async def get_live_matches_efficient(self) -> List[MatchData]:
        """Get live matches with intelligent caching and minimal API calls"""
        try:
            # Check Redis cache first
            cache_key = "live_matches"
            cached_data = await cache_service.get(cache_key)
            if cached_data:
                logger.debug("📋 Using Redis cache for live matches")
                return [MatchData(**match) for match in cached_data]
            
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
            
            # Cache in Redis for 30 seconds (live matches change frequently)
            if match_data_list:
                cache_data = [match.__dict__ for match in match_data_list]
                await cache_service.set(cache_key, cache_data, ttl=30)
            
            logger.info(f"📊 Processed {len(match_data_list)} live matches with Redis caching")
            
            # Trigger memory cleanup
            await self.cleanup_expired_cache()
            
            return match_data_list
            
        except Exception as e:
            logger.error(f"Error fetching live matches: {e}")
            return []
    
    async def get_todays_matches_efficient(self) -> List[MatchData]:
        """Get today's matches with intelligent caching and minimal API calls"""
        try:
            # Check Redis cache first
            cache_key = "todays_matches"
            cached_data = await cache_service.get(cache_key)
            if cached_data:
                logger.debug("📋 Using Redis cache for today's matches")
                return [MatchData(**match) for match in cached_data]
            
            # Get basic today's matches
            raw_matches = await sports_api.get_todays_matches()
            if not raw_matches:
                return []
            
            # Smart filtering: prioritize live and important matches
            live_matches = []
            important_matches = []
            other_matches = []
            
            for match in raw_matches:
                status = match.get("fixture", {}).get("status", {}).get("short", "").upper()
                league = match.get("league", {}).get("name", "")
                
                if status in ["1H", "HT", "2H", "ET", "P", "BT"]:
                    live_matches.append(match)
                elif any(important_league in league for important_league in ["Premier League", "La Liga", "Serie A", "Bundesliga", "Champions League"]):
                    important_matches.append(match)
                else:
                    other_matches.append(match)
            
            # Process live matches first with full details
            match_data_list = []
            if live_matches:
                logger.info(f"📡 Processing {len(live_matches)} live matches with full details")
                live_data = await self._process_match_batch_optimized(live_matches, is_live=True)
                match_data_list.extend(live_data)
            
            # Process important matches with basic details
            if important_matches:
                logger.info(f"⭐ Processing {len(important_matches)} important matches with basic details")
                important_data = await self._process_match_batch_optimized(important_matches[:20], is_live=False)  # Limit to 20
                match_data_list.extend(important_data)
            
            # Process other matches with minimal details (limit to 50)
            if other_matches:
                logger.info(f"📅 Processing {min(50, len(other_matches))} other matches with minimal details")
                other_data = await self._process_match_batch_optimized(other_matches[:50], is_live=False)
                match_data_list.extend(other_data)
            
            # Cache in Redis for 5 minutes (today's matches change less frequently)
            if match_data_list:
                cache_data = [match.__dict__ for match in match_data_list]
                await cache_service.set(cache_key, cache_data, ttl=300)
            
            logger.info(f"📅 Processed {len(match_data_list)} today's matches with Redis caching")
            
            # Trigger memory cleanup
            await self.cleanup_expired_cache()
            
            return match_data_list
            
        except Exception as e:
            logger.error(f"Error fetching today's matches: {e}")
            return []
    
    async def _process_match_batch_optimized(self, matches: List[Dict], is_live: bool = False) -> List[MatchData]:
        """Process a batch of matches with intelligent caching and API optimization"""
        # Process matches in smaller sub-batches to avoid overwhelming the API
        sub_batch_size = 5  # Even smaller sub-batches
        all_results = []
        
        for i in range(0, len(matches), sub_batch_size):
            sub_batch = matches[i:i + sub_batch_size]
            
            tasks = []
            for match in sub_batch:
                task = self._process_single_match_optimized(match, is_live)
                tasks.append(task)
            
            # Execute with concurrency control
            semaphore = asyncio.Semaphore(self.max_concurrent_requests)
            
            async def controlled_task(task):
                async with semaphore:
                    await self._rate_limit_check()  # Use rate limiting
                    return await task
            
            controlled_tasks = [controlled_task(task) for task in tasks]
            results = await asyncio.gather(*controlled_tasks, return_exceptions=True)
            
            # Filter out errors and add valid results
            for result in results:
                if isinstance(result, MatchData):
                    all_results.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Error processing match: {result}")
            
            # Add delay between sub-batches to be more API-friendly
            if i + sub_batch_size < len(matches):
                await asyncio.sleep(0.5)  # 500ms delay between sub-batches
        
        return all_results
    
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
            return self.basic_cache_ttl  # 10 minutes for finished matches
        elif status in ["NS", "TBD", "PST"]:
            return self.todays_cache_ttl  # 30 minutes for scheduled matches
        else:
            return self.basic_cache_ttl
    
    def _get_detail_level_for_match(self, match: Dict, is_live: bool) -> str:
        """Determine appropriate detail level for API calls - optimized for API efficiency"""
        status = match.get("fixture", {}).get("status", {}).get("short", "").upper()
        
        if is_live or status in ["1H", "HT", "2H", "ET", "P", "BT"]:
            return "full"  # Full details for live matches only
        elif status in ["FT", "AET", "PEN"]:
            return "basic"  # Basic info for finished matches (no detailed stats)
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
        try:
            fixture_id = match.get("fixture", {}).get("id")
            if not fixture_id:
                return match
            
            import httpx
            async with httpx.AsyncClient() as client:
                # Get statistics, events, and lineups with proper error handling
                stats = await self._get_match_stats_safe(fixture_id, client)
                events = await self._get_match_events_safe(fixture_id, client)
                lineups = await self._get_match_lineups_safe(fixture_id, client)
                
                # Create enhanced match data
                enhanced_match = match.copy()
                enhanced_match["detailed_stats"] = stats or []
                enhanced_match["events"] = events or []
                enhanced_match["lineups"] = lineups or []
                enhanced_match["alert_metrics"] = self._extract_alert_metrics_safe(match, stats, events)
                
                return enhanced_match
        except Exception as e:
            logger.error(f"Error enhancing match data for {match.get('fixture', {}).get('id')}: {e}")
            # Fall back to basic match data if enhancement fails
            return await self._fetch_basic_match_data(match)
    
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
    
    async def _get_match_stats_safe(self, fixture_id: int, client) -> List:
        """Get match statistics with safe error handling"""
        try:
            response = await client.get(
                f"{sports_api.base_url}/fixtures/statistics",
                headers=sports_api.headers,
                params={"fixture": fixture_id},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            result = data.get("response", [])
            return result if isinstance(result, list) else []
        except Exception as e:
            logger.warning(f"Failed to fetch stats for fixture {fixture_id}: {e}")
            return []
    
    async def _get_match_events_safe(self, fixture_id: int, client) -> List:
        """Get match events with safe error handling"""
        try:
            response = await client.get(
                f"{sports_api.base_url}/fixtures/events",
                headers=sports_api.headers,
                params={"fixture": fixture_id},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            result = data.get("response", [])
            return result if isinstance(result, list) else []
        except Exception as e:
            logger.warning(f"Failed to fetch events for fixture {fixture_id}: {e}")
            return []
    
    async def _get_match_lineups_safe(self, fixture_id: int, client) -> List:
        """Get match lineups with safe error handling"""
        try:
            response = await client.get(
                f"{sports_api.base_url}/fixtures/lineups",
                headers=sports_api.headers,
                params={"fixture": fixture_id},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            result = data.get("response", [])
            return result if isinstance(result, list) else []
        except Exception as e:
            logger.warning(f"Failed to fetch lineups for fixture {fixture_id}: {e}")
            return []
    
    def _extract_alert_metrics_safe(self, match: Dict, stats: Optional[List] = None, events: Optional[List] = None) -> Dict:
        """Extract alert metrics with safe error handling"""
        try:
            # Use the existing sports API method but with error handling
            return sports_api._extract_alert_metrics(match, stats, events)
        except Exception as e:
            logger.warning(f"Error extracting alert metrics: {e}")
            # Return basic metrics as fallback
            return self._extract_basic_metrics(match)
    
    def _extract_basic_metrics(self, match: Dict) -> Dict:
        """Extract basic metrics without API calls - enhanced for alerts"""
        # Extract basic match info
        goals = match.get("goals", {})
        fixture = match.get("fixture", {})
        teams = match.get("teams", {})
        
        home_score = goals.get("home", 0) or 0
        away_score = goals.get("away", 0) or 0
        status = fixture.get("status", {})
        
        # Enhanced basic metrics for alerts
        return {
            "basic": {
                "home_score": home_score,
                "away_score": away_score,
                "score_difference": abs(home_score - away_score),
                "total_goals": home_score + away_score,
                "match_status": status.get("short", "Unknown"),
                "elapsed_time": status.get("elapsed", 0) or 0,
                "referee": fixture.get("referee", "Unknown"),
                "venue": fixture.get("venue", {}).get("name", "Unknown"),
                "weather": fixture.get("weather", {}),
                "home_team": teams.get("home", {}).get("name", "Unknown"),
                "away_team": teams.get("away", {}).get("name", "Unknown"),
            },
            # Enhanced metrics for alerts - provide reasonable defaults
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
        
        # Ensure we always have usable metrics for alerts
        if not alert_metrics:
            alert_metrics = self._extract_basic_metrics(match_data)
        
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
        """Clean up expired cache entries and optimize memory usage"""
        current_time = time.time()
        
        # Only run cleanup if enough time has passed
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
            
        self.last_cleanup = current_time
        
        db = next(get_db())
        try:
            # Clean up expired entries
            max_cache_ttl = max(self.basic_cache_ttl, self.detailed_cache_ttl, self.live_cache_ttl)
            expired_entries = db.query(MatchCache).filter(
                MatchCache.last_updated < datetime.utcnow() - timedelta(seconds=max_cache_ttl)
            ).all()
            
            for entry in expired_entries:
                db.delete(entry)
            
            # Limit total cache entries to prevent memory bloat
            total_entries = db.query(MatchCache).count()
            if total_entries > self.max_cache_entries:
                # Delete oldest entries beyond the limit
                excess_entries = db.query(MatchCache).order_by(MatchCache.last_updated.asc()).limit(
                    total_entries - self.max_cache_entries
                ).all()
                
                for entry in excess_entries:
                    db.delete(entry)
            
            db.commit()
            logger.info(f"🧹 Memory cleanup: Removed {len(expired_entries)} expired entries, total cache size: {db.query(MatchCache).count()}")
            
            # Force garbage collection
            import gc
            gc.collect()
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            db.rollback()
        finally:
            db.close()

# Global instance
data_service = DataService() 