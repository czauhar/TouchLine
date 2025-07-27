"""
Fallback mechanisms for TouchLine application
Handles API failures and provides alternative data sources
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from ..core.exceptions import SportsAPIError, CacheError
from ..database import get_db
from ..models import MatchCache, Match

logger = logging.getLogger(__name__)

class FallbackManager:
    """Manages fallback mechanisms for API failures"""
    
    def __init__(self):
        self.cache_ttl = 300  # 5 minutes
        self.max_retries = 3
        self.retry_delay = 5  # seconds
    
    async def get_match_data_with_fallback(self, fixture_id: int, api_call_func) -> Dict:
        """Get match data with fallback to cache if API fails"""
        try:
            # Try API call first
            match_data = await self._retry_api_call(api_call_func, fixture_id)
            if match_data:
                # Update cache with fresh data
                await self._update_cache(fixture_id, match_data)
                return match_data
        except Exception as e:
            logger.warning(f"API call failed for fixture {fixture_id}: {e}")
        
        # Fallback to cache
        cached_data = await self._get_from_cache(fixture_id)
        if cached_data:
            logger.info(f"Using cached data for fixture {fixture_id}")
            return cached_data
        
        # Final fallback - return minimal data structure
        logger.warning(f"No data available for fixture {fixture_id}, using fallback structure")
        return self._create_fallback_match_data(fixture_id)
    
    async def _retry_api_call(self, api_call_func, *args, **kwargs) -> Optional[Dict]:
        """Retry API call with exponential backoff"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                result = await api_call_func(*args, **kwargs)
                if result:
                    return result
            except Exception as e:
                last_exception = e
                logger.warning(f"API call attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    await asyncio.sleep(delay)
        
        if last_exception:
            raise SportsAPIError(
                f"API call failed after {self.max_retries} attempts",
                api_response={"error": str(last_exception)}
            )
        
        return None
    
    async def _get_from_cache(self, fixture_id: int) -> Optional[Dict]:
        """Get match data from cache"""
        try:
            db = next(get_db())
            cache_entry = db.query(MatchCache).filter(
                MatchCache.external_id == str(fixture_id)
            ).first()
            
            if cache_entry and not cache_entry.is_expired:
                return cache_entry.match_data
            
            return None
        except Exception as e:
            logger.error(f"Error accessing cache for fixture {fixture_id}: {e}")
            return None
    
    async def _update_cache(self, fixture_id: int, match_data: Dict):
        """Update cache with fresh data"""
        try:
            db = next(get_db())
            
            # Check if cache entry exists
            cache_entry = db.query(MatchCache).filter(
                MatchCache.external_id == str(fixture_id)
            ).first()
            
            if cache_entry:
                # Update existing entry
                cache_entry.match_data = match_data
                cache_entry.last_updated = datetime.utcnow()
            else:
                # Create new entry
                cache_entry = MatchCache(
                    external_id=str(fixture_id),
                    match_data=match_data,
                    last_updated=datetime.utcnow(),
                    cache_ttl=self.cache_ttl
                )
                db.add(cache_entry)
            
            db.commit()
            logger.debug(f"Cache updated for fixture {fixture_id}")
            
        except Exception as e:
            logger.error(f"Error updating cache for fixture {fixture_id}: {e}")
            db.rollback()
    
    def _create_fallback_match_data(self, fixture_id: int) -> Dict:
        """Create minimal fallback match data structure"""
        return {
            "fixture": {
                "id": fixture_id,
                "status": {"elapsed": 0, "short": "NS"}
            },
            "teams": {
                "home": {"name": "Unknown Team", "id": None},
                "away": {"name": "Unknown Team", "id": None}
            },
            "goals": {"home": 0, "away": 0},
            "league": {"name": "Unknown League", "id": None},
            "events": [],
            "lineups": [],
            "is_fallback": True,
            "fallback_timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_live_matches_with_fallback(self, api_call_func) -> List[Dict]:
        """Get live matches with fallback mechanisms"""
        try:
            matches = await self._retry_api_call(api_call_func)
            if matches:
                return matches
        except Exception as e:
            logger.warning(f"Live matches API call failed: {e}")
        
        # Fallback: return matches from database that might be live
        return await self._get_potential_live_matches()
    
    async def _get_potential_live_matches(self) -> List[Dict]:
        """Get potential live matches from database"""
        try:
            db = next(get_db())
            
            # Get matches that started recently and might still be live
            recent_start = datetime.utcnow() - timedelta(hours=3)
            potential_live = db.query(Match).filter(
                Match.start_time >= recent_start,
                Match.status.in_(["NS", "1H", "HT", "2H", "ET", "P"])
            ).all()
            
            matches = []
            for match in potential_live:
                match_data = {
                    "fixture": {
                        "id": int(match.external_id),
                        "status": {"elapsed": 0, "short": match.status}
                    },
                    "teams": {
                        "home": {"name": match.home_team, "id": None},
                        "away": {"name": match.away_team, "id": None}
                    },
                    "goals": {"home": match.home_score, "away": match.away_score},
                    "league": {"name": match.league, "id": None},
                    "is_fallback": True
                }
                matches.append(match_data)
            
            logger.info(f"Returning {len(matches)} potential live matches from database")
            return matches
            
        except Exception as e:
            logger.error(f"Error getting potential live matches: {e}")
            return []
    
    async def validate_and_repair_match_data(self, match_data: Dict) -> Dict:
        """Validate and repair match data structure"""
        if not match_data:
            return self._create_fallback_match_data(0)
        
        # Ensure required fields exist
        required_sections = ['fixture', 'teams', 'goals', 'league']
        for section in required_sections:
            if section not in match_data:
                match_data[section] = {}
        
        # Repair fixture data
        if 'fixture' not in match_data or not match_data['fixture']:
            match_data['fixture'] = {"id": 0, "status": {"elapsed": 0, "short": "NS"}}
        
        # Repair teams data
        if 'teams' not in match_data or not match_data['teams']:
            match_data['teams'] = {
                "home": {"name": "Unknown Team", "id": None},
                "away": {"name": "Unknown Team", "id": None}
            }
        
        # Repair goals data
        if 'goals' not in match_data or not match_data['goals']:
            match_data['goals'] = {"home": 0, "away": 0}
        
        # Ensure goals are integers
        for team in ['home', 'away']:
            if team in match_data['goals']:
                try:
                    match_data['goals'][team] = int(match_data['goals'][team])
                except (ValueError, TypeError):
                    match_data['goals'][team] = 0
        
        # Repair league data
        if 'league' not in match_data or not match_data['league']:
            match_data['league'] = {"name": "Unknown League", "id": None}
        
        # Ensure events and lineups exist
        if 'events' not in match_data:
            match_data['events'] = []
        if 'lineups' not in match_data:
            match_data['lineups'] = []
        
        return match_data
    
    async def get_player_stats_with_fallback(self, player_id: int, match_data: Dict) -> Dict:
        """Get player statistics with fallback mechanisms"""
        try:
            # Try to extract from match data
            if 'events' in match_data and match_data['events']:
                player_stats = self._extract_player_stats_from_events(player_id, match_data['events'])
                if player_stats:
                    return player_stats
        except Exception as e:
            logger.warning(f"Error extracting player stats for {player_id}: {e}")
        
        # Fallback: return minimal player stats
        return {
            "player_id": player_id,
            "player_name": "Unknown Player",
            "team": "Unknown Team",
            "position": "Unknown",
            "goals": 0,
            "assists": 0,
            "yellow_cards": 0,
            "red_cards": 0,
            "shots": 0,
            "passes": 0,
            "minutes_played": 0,
            "is_fallback": True
        }
    
    def _extract_player_stats_from_events(self, player_id: int, events: List[Dict]) -> Optional[Dict]:
        """Extract player statistics from match events"""
        stats = {
            "player_id": player_id,
            "goals": 0,
            "assists": 0,
            "yellow_cards": 0,
            "red_cards": 0,
            "minutes_played": 0
        }
        
        for event in events:
            if event.get('player', {}).get('id') == player_id:
                event_type = event.get('type')
                if event_type == 'Goal':
                    stats['goals'] += 1
                elif event_type == 'Card':
                    card_type = event.get('detail', {}).get('type', 'yellow')
                    if card_type == 'red':
                        stats['red_cards'] += 1
                    else:
                        stats['yellow_cards'] += 1
                elif event_type == 'Subst':
                    # Estimate minutes played
                    stats['minutes_played'] = max(stats['minutes_played'], 45)
        
        return stats if any(v > 0 for v in stats.values() if isinstance(v, int)) else None

# Global fallback manager instance
fallback_manager = FallbackManager() 