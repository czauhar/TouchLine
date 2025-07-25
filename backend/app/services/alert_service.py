from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models import Alert, AlertHistory
from app.core.exceptions import AlertException
from app.core.config import settings
import json
from datetime import datetime

class AlertService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_alert(self, alert_data: Dict) -> Alert:
        """Create a new alert with validation"""
        try:
            # Parse conditions
            conditions = json.loads(alert_data.get('conditions', '{}'))
            
            # Validate required fields
            if not conditions.get('team'):
                raise AlertException("Team is required", 400)
            
            # Create alert
            alert = Alert(
                name=alert_data.get('name', ''),
                team=conditions.get('team', ''),
                alert_type=conditions.get('condition_type', 'goals'),
                threshold=float(conditions.get('value', 0)),
                condition=self._format_condition(conditions),
                time_window=conditions.get('time_window'),
                user_phone=alert_data.get('user_phone', ''),
                is_active=True
            )
            
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            
            return alert
            
        except json.JSONDecodeError:
            raise AlertException("Invalid conditions format", 400)
        except Exception as e:
            self.db.rollback()
            raise AlertException(f"Error creating alert: {str(e)}", 500)
    
    def get_all_alerts(self) -> List[Alert]:
        """Get all alerts"""
        try:
            return self.db.query(Alert).all()
        except Exception as e:
            raise AlertException(f"Error fetching alerts: {str(e)}", 500)
    
    def toggle_alert(self, alert_id: int) -> Alert:
        """Toggle alert active status"""
        try:
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                raise AlertException("Alert not found", 404)
            
            alert.is_active = not alert.is_active
            self.db.commit()
            
            return alert
            
        except AlertException:
            raise
        except Exception as e:
            self.db.rollback()
            raise AlertException(f"Error toggling alert: {str(e)}", 500)
    
    def delete_alert(self, alert_id: int) -> bool:
        """Delete an alert"""
        try:
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                raise AlertException("Alert not found", 404)
            
            self.db.delete(alert)
            self.db.commit()
            
            return True
            
        except AlertException:
            raise
        except Exception as e:
            self.db.rollback()
            raise AlertException(f"Error deleting alert: {str(e)}", 500)
    
    def get_alert_stats(self) -> Dict:
        """Get alert statistics"""
        try:
            total_alerts = self.db.query(Alert).count()
            active_alerts = self.db.query(Alert).filter(Alert.is_active == True).count()
            
            return {
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "inactive_alerts": total_alerts - active_alerts
            }
        except Exception as e:
            raise AlertException(f"Error fetching alert stats: {str(e)}", 500)
    
    def _format_condition(self, conditions: Dict) -> str:
        """Format conditions into readable string"""
        team = conditions.get('team', '')
        condition_type = conditions.get('condition_type', 'goals')
        operator = conditions.get('operator', '>=')
        value = conditions.get('value', 0)
        time_window = conditions.get('time_window')
        
        condition_str = f"{team} {condition_type} {operator} {value}"
        if time_window:
            condition_str += f" (within {time_window} minutes)"
        
        return condition_str 