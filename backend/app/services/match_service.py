from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional
from ..models import Match
from ..sports_api import sports_api
from ..utils.logger import log_database_operation
import time

class MatchService:
    """Service for managing match data and operations"""
    
    @staticmethod
    def get_live_matches(db: Session) -> List[Match]:
        """Get live matches from database"""
        start_time = time.time()
        try:
            matches = db.query(Match).filter(
                Match.status.in_(["1H", "HT", "2H", "ET", "P", "BT"])
            ).all()
            
            log_database_operation(
                "select", "matches", True, time.time() - start_time
            )
            return matches
        except Exception as e:
            log_database_operation(
                "select", "matches", False, time.time() - start_time, str(e)
            )
            raise
    
    @staticmethod
    def get_todays_matches(db: Session) -> List[Match]:
        """Get today's matches from database"""
        start_time = time.time()
        try:
            today = date.today()
            matches = db.query(Match).filter(
                Match.start_time >= today
            ).all()
            
            log_database_operation(
                "select", "matches", True, time.time() - start_time
            )
            return matches
        except Exception as e:
            log_database_operation(
                "select", "matches", False, time.time() - start_time, str(e)
            )
            raise
    
    @staticmethod
    def get_match_by_external_id(db: Session, external_id: str) -> Optional[Match]:
        """Get match by external ID"""
        start_time = time.time()
        try:
            match = db.query(Match).filter(Match.external_id == external_id).first()
            
            log_database_operation(
                "select", "matches", True, time.time() - start_time
            )
            return match
        except Exception as e:
            log_database_operation(
                "select", "matches", False, time.time() - start_time, str(e)
            )
            raise
    
    @staticmethod
    async def sync_live_matches(db: Session) -> List[Match]:
        """Sync live matches from sports API to database"""
        start_time = time.time()
        try:
            # Get live matches from sports API
            live_matches_data = await sports_api.get_live_matches()
            synced_matches = []
            
            for match_data in live_matches_data:
                # Check if match already exists
                existing_match = MatchService.get_match_by_external_id(db, str(match_data.get("fixture", {}).get("id")))
                
                if existing_match:
                    # Update existing match
                    existing_match.home_score = match_data.get("goals", {}).get("home", 0)
                    existing_match.away_score = match_data.get("goals", {}).get("away", 0)
                    existing_match.status = match_data.get("fixture", {}).get("status", {}).get("short", "")
                    existing_match.updated_at = datetime.utcnow()
                    synced_matches.append(existing_match)
                else:
                    # Create new match
                    new_match = Match(
                        external_id=str(match_data.get("fixture", {}).get("id")),
                        home_team=match_data.get("teams", {}).get("home", {}).get("name", ""),
                        away_team=match_data.get("teams", {}).get("away", {}).get("name", ""),
                        league=match_data.get("league", {}).get("name", ""),
                        start_time=datetime.fromisoformat(match_data.get("fixture", {}).get("date", "")),
                        status=match_data.get("fixture", {}).get("status", {}).get("short", ""),
                        home_score=match_data.get("goals", {}).get("home", 0),
                        away_score=match_data.get("goals", {}).get("away", 0)
                    )
                    db.add(new_match)
                    synced_matches.append(new_match)
            
            db.commit()
            
            log_database_operation(
                "sync", "matches", True, time.time() - start_time
            )
            return synced_matches
        except Exception as e:
            log_database_operation(
                "sync", "matches", False, time.time() - start_time, str(e)
            )
            raise
    
    @staticmethod
    def update_match_scores(db: Session, external_id: str, home_score: int, away_score: int) -> Optional[Match]:
        """Update match scores"""
        start_time = time.time()
        try:
            match = MatchService.get_match_by_external_id(db, external_id)
            if match:
                match.home_score = home_score
                match.away_score = away_score
                match.updated_at = datetime.utcnow()
                db.commit()
                
                log_database_operation(
                    "update", "matches", True, time.time() - start_time
                )
                return match
            
            log_database_operation(
                "update", "matches", False, time.time() - start_time, "Match not found"
            )
            return None
        except Exception as e:
            log_database_operation(
                "update", "matches", False, time.time() - start_time, str(e)
            )
            raise
    
    @staticmethod
    def get_matches_by_team(db: Session, team_name: str) -> List[Match]:
        """Get matches by team name"""
        start_time = time.time()
        try:
            matches = db.query(Match).filter(
                (Match.home_team.contains(team_name)) | (Match.away_team.contains(team_name))
            ).order_by(Match.start_time.desc()).all()
            
            log_database_operation(
                "select", "matches", True, time.time() - start_time
            )
            return matches
        except Exception as e:
            log_database_operation(
                "select", "matches", False, time.time() - start_time, str(e)
            )
            raise
    
    @staticmethod
    def get_matches_by_league(db: Session, league_name: str) -> List[Match]:
        """Get matches by league name"""
        start_time = time.time()
        try:
            matches = db.query(Match).filter(
                Match.league.contains(league_name)
            ).order_by(Match.start_time.desc()).all()
            
            log_database_operation(
                "select", "matches", True, time.time() - start_time
            )
            return matches
        except Exception as e:
            log_database_operation(
                "select", "matches", False, time.time() - start_time, str(e)
            )
            raise 