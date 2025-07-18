from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from .database import get_db
from .models import User, Match, Alert, AlertHistory, Base
from .sports_api import sports_api

class MatchService:
    @staticmethod
    async def sync_live_matches(db: Session) -> List[Match]:
        """Sync live matches from sports API to database"""
        live_matches_data = await sports_api.get_live_matches()
        synced_matches = []
        
        for match_data in live_matches_data:
            formatted_data = sports_api.format_match_data(match_data)
            
            # Check if match already exists
            existing_match = db.query(Match).filter(
                Match.external_id == formatted_data["external_id"]
            ).first()
            
            if existing_match:
                # Update existing match
                existing_match.home_score = formatted_data["home_score"]
                existing_match.away_score = formatted_data["away_score"]
                existing_match.status = formatted_data["status"]
                synced_matches.append(existing_match)
            else:
                # Create new match
                new_match = Match(
                    external_id=formatted_data["external_id"],
                    home_team=formatted_data["home_team"],
                    away_team=formatted_data["away_team"],
                    league=formatted_data["league"],
                    start_time=datetime.fromisoformat(formatted_data["start_time"].replace('Z', '+00:00')),
                    status=formatted_data["status"],
                    home_score=formatted_data["home_score"],
                    away_score=formatted_data["away_score"]
                )
                db.add(new_match)
                synced_matches.append(new_match)
        
        db.commit()
        return synced_matches
    
    @staticmethod
    def get_live_matches(db: Session) -> List[Match]:
        """Get live matches from database"""
        return db.query(Match).filter(Match.status == "LIVE").all()
    
    @staticmethod
    def get_todays_matches(db: Session) -> List[Match]:
        """Get today's matches from database"""
        today = datetime.now().date()
        return db.query(Match).filter(
            and_(
                Match.start_time >= today,
                Match.start_time < today + timedelta(days=1)
            )
        ).all()
    
    @staticmethod
    def get_match_by_external_id(db: Session, external_id: str) -> Optional[Match]:
        """Get match by external ID"""
        return db.query(Match).filter(Match.external_id == external_id).first()

class AlertService:
    @staticmethod
    def create_alert(
        db: Session,
        user_id: int,
        name: str,
        alert_type: str,
        threshold: float,
        condition: str,
        team_filter: Optional[str] = None,
        league_filter: Optional[str] = None
    ) -> Alert:
        """Create a new alert"""
        alert = Alert(
            user_id=user_id,
            name=name,
            alert_type=alert_type,
            threshold=threshold,
            condition=condition,
            team_filter=team_filter,
            league_filter=league_filter
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert
    
    @staticmethod
    def get_user_alerts(db: Session, user_id: int) -> List[Alert]:
        """Get all alerts for a user"""
        return db.query(Alert).filter(
            and_(
                Alert.user_id == user_id,
                Alert.is_active == True
            )
        ).all()
    
    @staticmethod
    def check_alerts_for_match(db: Session, match: Match) -> List[Alert]:
        """Check which alerts should be triggered for a given match"""
        # Get all active alerts
        active_alerts = db.query(Alert).filter(Alert.is_active == True).all()
        triggered_alerts = []
        
        for alert in active_alerts:
            # Check if alert applies to this match
            if not AlertService._alert_applies_to_match(alert, match):
                continue
            
            # Check if alert condition is met
            if AlertService._check_alert_condition(alert, match):
                triggered_alerts.append(alert)
        
        return triggered_alerts
    
    @staticmethod
    def _alert_applies_to_match(alert: Alert, match: Match) -> bool:
        """Check if alert applies to the given match"""
        # Check team filter
        if alert.team_filter:
            if alert.team_filter.lower() not in [match.home_team.lower(), match.away_team.lower()]:
                return False
        
        # Check league filter
        if alert.league_filter:
            if alert.league_filter.lower() not in match.league.lower():
                return False
        
        return True
    
    @staticmethod
    def _check_alert_condition(alert: Alert, match: Match) -> bool:
        """Check if alert condition is met"""
        # Get the relevant value based on alert type
        if alert.alert_type == "home_score":
            value = match.home_score
        elif alert.alert_type == "away_score":
            value = match.away_score
        elif alert.alert_type == "total_goals":
            value = match.home_score + match.away_score
        else:
            return False
        
        # Check condition
        if alert.condition == "greater_than":
            return value > alert.threshold
        elif alert.condition == "less_than":
            return value < alert.threshold
        elif alert.condition == "equals":
            return value == alert.threshold
        elif alert.condition == "greater_than_or_equal":
            return value >= alert.threshold
        elif alert.condition == "less_than_or_equal":
            return value <= alert.threshold
        
        return False
    
    @staticmethod
    def record_alert_trigger(
        db: Session,
        alert: Alert,
        match: Match,
        message: str,
        sent_via: str = "sms",
        status: str = "sent"
    ) -> AlertHistory:
        """Record that an alert was triggered"""
        history = AlertHistory(
            alert_id=alert.id,
            match_id=match.id,
            message=message,
            sent_via=sent_via,
            status=status
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        return history

class UserService:
    @staticmethod
    def create_user(
        db: Session,
        email: str,
        username: str,
        hashed_password: str,
        phone_number: Optional[str] = None
    ) -> User:
        """Create a new user"""
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            phone_number=phone_number
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first() 