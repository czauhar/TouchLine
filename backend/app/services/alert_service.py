from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from ..models import Alert, AlertHistory
from ..core.exceptions import AlertException
from ..core.config import settings
from ..utils.logger import log_database_operation
import json
import time
from datetime import datetime

class AlertService:
    """Service for managing alert data and operations"""
    
    @staticmethod
    def create_alert(db: Session, alert_data: Dict, user_id: int) -> Alert:
        """Create a new alert with validation"""
        start_time = time.time()
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
                condition=AlertService._format_condition(conditions),
                time_window=conditions.get('time_window'),
                user_phone=alert_data.get('user_phone', ''),
                user_id=user_id,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            log_database_operation(
                "insert", "alerts", True, time.time() - start_time
            )
            return alert
            
        except json.JSONDecodeError:
            log_database_operation(
                "insert", "alerts", False, time.time() - start_time, "Invalid JSON"
            )
            raise AlertException("Invalid conditions format", 400)
        except Exception as e:
            db.rollback()
            log_database_operation(
                "insert", "alerts", False, time.time() - start_time, str(e)
            )
            raise AlertException(f"Error creating alert: {str(e)}", 500)
    
    @staticmethod
    def get_all_alerts(db: Session) -> List[Alert]:
        """Get all alerts"""
        start_time = time.time()
        try:
            alerts = db.query(Alert).all()
            log_database_operation(
                "select", "alerts", True, time.time() - start_time
            )
            return alerts
        except Exception as e:
            log_database_operation(
                "select", "alerts", False, time.time() - start_time, str(e)
            )
            raise AlertException(f"Error fetching alerts: {str(e)}", 500)
    
    @staticmethod
    def get_user_alerts(db: Session, user_id: int) -> List[Alert]:
        """Get alerts for a specific user"""
        start_time = time.time()
        try:
            alerts = db.query(Alert).filter(Alert.user_id == user_id).all()
            log_database_operation(
                "select", "alerts", True, time.time() - start_time
            )
            return alerts
        except Exception as e:
            log_database_operation(
                "select", "alerts", False, time.time() - start_time, str(e)
            )
            raise AlertException(f"Error fetching user alerts: {str(e)}", 500)
    
    @staticmethod
    def get_alert_by_id(db: Session, alert_id: int) -> Optional[Alert]:
        """Get alert by ID"""
        start_time = time.time()
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            log_database_operation(
                "select", "alerts", True, time.time() - start_time
            )
            return alert
        except Exception as e:
            log_database_operation(
                "select", "alerts", False, time.time() - start_time, str(e)
            )
            raise
    
    @staticmethod
    def toggle_alert(db: Session, alert_id: int, user_id: int) -> Alert:
        """Toggle alert active status"""
        start_time = time.time()
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                raise AlertException("Alert not found", 404)
            
            if alert.user_id != user_id:
                raise AlertException("Unauthorized", 403)
            
            alert.is_active = not alert.is_active
            db.commit()
            
            log_database_operation(
                "update", "alerts", True, time.time() - start_time
            )
            return alert
            
        except AlertException:
            raise
        except Exception as e:
            db.rollback()
            log_database_operation(
                "update", "alerts", False, time.time() - start_time, str(e)
            )
            raise AlertException(f"Error toggling alert: {str(e)}", 500)
    
    @staticmethod
    def delete_alert(db: Session, alert_id: int, user_id: int) -> bool:
        """Delete an alert"""
        start_time = time.time()
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                raise AlertException("Alert not found", 404)
            
            if alert.user_id != user_id:
                raise AlertException("Unauthorized", 403)
            
            db.delete(alert)
            db.commit()
            
            log_database_operation(
                "delete", "alerts", True, time.time() - start_time
            )
            return True
            
        except AlertException:
            raise
        except Exception as e:
            db.rollback()
            log_database_operation(
                "delete", "alerts", False, time.time() - start_time, str(e)
            )
            raise AlertException(f"Error deleting alert: {str(e)}", 500)
    
    @staticmethod
    def get_alert_stats(db: Session) -> Dict:
        """Get alert statistics"""
        start_time = time.time()
        try:
            total_alerts = db.query(Alert).count()
            active_alerts = db.query(Alert).filter(Alert.is_active == True).count()
            
            log_database_operation(
                "select", "alerts", True, time.time() - start_time
            )
            return {
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "inactive_alerts": total_alerts - active_alerts
            }
        except Exception as e:
            log_database_operation(
                "select", "alerts", False, time.time() - start_time, str(e)
            )
            raise AlertException(f"Error fetching alert stats: {str(e)}", 500)
    
    @staticmethod
    def _format_condition(conditions: Dict) -> str:
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