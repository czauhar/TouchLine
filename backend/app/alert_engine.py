import asyncio
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from .database import get_db
from .models import Match, Alert, AlertHistory
from .services import AlertService
from .sms_service import sms_service

class AlertEngine:
    def __init__(self):
        self.is_running = False
        self.check_interval = 30  # Check every 30 seconds
    
    async def start_monitoring(self):
        """Start the alert monitoring service"""
        self.is_running = True
        print("🚨 Alert Engine started - monitoring for triggers...")
        
        while self.is_running:
            try:
                await self.check_alerts()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                print(f"❌ Alert Engine error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def stop_monitoring(self):
        """Stop the alert monitoring service"""
        self.is_running = False
        print("🛑 Alert Engine stopped")
    
    async def check_alerts(self):
        """Check all active matches for alert triggers"""
        try:
            db = next(get_db())
            
            # Get all live matches
            live_matches = db.query(Match).filter(Match.status == "LIVE").all()
            
            for match in live_matches:
                await self.check_match_alerts(db, match)
                
        except Exception as e:
            print(f"❌ Error checking alerts: {e}")
    
    async def check_match_alerts(self, db: Session, match: Match):
        """Check if any alerts should be triggered for a specific match"""
        try:
            # Get all active alerts
            active_alerts = db.query(Alert).filter(Alert.is_active == True).all()
            
            for alert in active_alerts:
                # Check if alert applies to this match
                if not self._alert_applies_to_match(alert, match):
                    continue
                
                # Check if alert condition is met
                if self._check_alert_condition(alert, match):
                    # Check if we already sent this alert for this match
                    if not self._alert_already_sent(db, alert, match):
                        await self._trigger_alert(db, alert, match)
                        
        except Exception as e:
            print(f"❌ Error checking match alerts: {e}")
    
    def _alert_applies_to_match(self, alert: Alert, match: Match) -> bool:
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
    
    def _check_alert_condition(self, alert: Alert, match: Match) -> bool:
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
    
    def _alert_already_sent(self, db: Session, alert: Alert, match: Match) -> bool:
        """Check if this alert was already sent for this match"""
        existing = db.query(AlertHistory).filter(
            AlertHistory.alert_id == alert.id,
            AlertHistory.match_id == match.id
        ).first()
        return existing is not None
    
    async def _trigger_alert(self, db: Session, alert: Alert, match: Match):
        """Trigger an alert and send SMS"""
        try:
            # Format match info
            match_info = {
                "home_team": match.home_team,
                "away_team": match.away_team,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "league": match.league,
                "elapsed": 0  # We'll get this from API later
            }
            
            # Create condition description
            condition_met = self._format_condition_met(alert, match)
            
            # Format SMS message
            message = sms_service.format_alert_message(
                alert.name, 
                match_info, 
                condition_met
            )
            
            # For now, use a default phone number (user phone will come from user system)
            # TODO: Get user's phone number from User model
            default_phone = "+1234567890"  # Placeholder
            
            # Send SMS
            sms_result = sms_service.send_alert(default_phone, message)
            
            # Record alert history
            history = AlertService.record_alert_trigger(
                db=db,
                alert=alert,
                match=match,
                message=message,
                sent_via="sms",
                status="sent" if sms_result["success"] else "failed"
            )
            
            print(f"📱 Alert triggered: {alert.name} - {sms_result['success']}")
            
        except Exception as e:
            print(f"❌ Error triggering alert: {e}")
    
    def _format_condition_met(self, alert: Alert, match: Match) -> str:
        """Format the condition that was met"""
        if alert.alert_type == "home_score":
            return f"{match.home_team} scored {match.home_score} goals"
        elif alert.alert_type == "away_score":
            return f"{match.away_team} scored {match.away_score} goals"
        elif alert.alert_type == "total_goals":
            total = match.home_score + match.away_score
            return f"Total goals: {total}"
        else:
            return f"Condition met: {alert.alert_type}"

# Global instance
alert_engine = AlertEngine() 