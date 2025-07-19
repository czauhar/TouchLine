import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
import json
import redis
from sqlalchemy.orm import Session
from .database import get_db
from .models import Alert, AlertHistory, User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ALERT_TRIGGER_COUNT = Counter('alerts_triggered_total', 'Total alerts triggered', ['alert_type', 'team'])
SMS_SENT_COUNT = Counter('sms_sent_total', 'Total SMS messages sent')
ACTIVE_USERS = Gauge('active_users', 'Number of active users')
ACTIVE_ALERTS = Gauge('active_alerts', 'Number of active alerts')
LIVE_MATCHES = Gauge('live_matches', 'Number of live matches')

class MonitoringService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.start_time = datetime.utcnow()
    
    def track_request(self, request: Request, response: Response, duration: float):
        """Track HTTP request metrics"""
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_DURATION.observe(duration)
        
        # Log request details
        logger.info(f"Request: {request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    
    def track_alert_trigger(self, alert_type: str, team: str):
        """Track alert trigger metrics"""
        ALERT_TRIGGER_COUNT.labels(alert_type=alert_type, team=team).inc()
        
        # Store in Redis for real-time analytics
        key = f"alert_triggers:{datetime.utcnow().strftime('%Y-%m-%d')}"
        self.redis.hincrby(key, f"{alert_type}:{team}", 1)
        self.redis.expire(key, 86400)  # 24 hours
    
    def track_sms_sent(self, success: bool = True):
        """Track SMS sending metrics"""
        SMS_SENT_COUNT.inc()
        
        # Store SMS metrics
        key = f"sms_metrics:{datetime.utcnow().strftime('%Y-%m-%d')}"
        self.redis.hincrby(key, "sent", 1)
        if not success:
            self.redis.hincrby(key, "failed", 1)
        self.redis.expire(key, 86400)
    
    def update_user_metrics(self, db: Session):
        """Update user-related metrics"""
        try:
            active_users = db.query(User).filter(User.is_active == True).count()
            ACTIVE_USERS.set(active_users)
            
            active_alerts = db.query(Alert).filter(Alert.is_active == True).count()
            ACTIVE_ALERTS.set(active_alerts)
            
            # Store in Redis
            self.redis.set("metrics:active_users", active_users)
            self.redis.set("metrics:active_alerts", active_alerts)
            
        except Exception as e:
            logger.error(f"Error updating user metrics: {e}")
    
    def update_match_metrics(self, live_matches_count: int):
        """Update match-related metrics"""
        LIVE_MATCHES.set(live_matches_count)
        self.redis.set("metrics:live_matches", live_matches_count)
    
    def get_alert_analytics(self, days: int = 7) -> Dict:
        """Get alert analytics for the last N days"""
        analytics = {
            "total_triggers": 0,
            "triggers_by_type": {},
            "triggers_by_team": {},
            "success_rate": 0,
            "daily_triggers": []
        }
        
        try:
            # Get alert history from database
            db = next(get_db())
            start_date = datetime.utcnow() - timedelta(days=days)
            
            alert_history = db.query(AlertHistory).filter(
                AlertHistory.triggered_at >= start_date
            ).all()
            
            analytics["total_triggers"] = len(alert_history)
            
            # Calculate success rate
            successful_sms = sum(1 for alert in alert_history if alert.sms_sent)
            analytics["success_rate"] = (successful_sms / len(alert_history) * 100) if alert_history else 0
            
            # Group by alert type and team
            for alert in alert_history:
                alert_obj = db.query(Alert).filter(Alert.id == alert.alert_id).first()
                if alert_obj:
                    alert_type = alert_obj.alert_type
                    team = alert_obj.team
                    
                    analytics["triggers_by_type"][alert_type] = analytics["triggers_by_type"].get(alert_type, 0) + 1
                    analytics["triggers_by_team"][team] = analytics["triggers_by_team"].get(team, 0) + 1
            
            # Daily triggers
            for i in range(days):
                date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
                daily_count = db.query(AlertHistory).filter(
                    AlertHistory.triggered_at >= datetime.strptime(date, '%Y-%m-%d'),
                    AlertHistory.triggered_at < datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)
                ).count()
                
                analytics["daily_triggers"].append({
                    "date": date,
                    "count": daily_count
                })
            
        except Exception as e:
            logger.error(f"Error getting alert analytics: {e}")
        
        return analytics
    
    def get_system_health(self) -> Dict:
        """Get system health metrics"""
        health = {
            "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
            "redis_connected": self.redis.ping(),
            "active_users": self.redis.get("metrics:active_users") or 0,
            "active_alerts": self.redis.get("metrics:active_alerts") or 0,
            "live_matches": self.redis.get("metrics:live_matches") or 0,
            "memory_usage": self.redis.info()["used_memory_human"],
            "last_alert_trigger": None
        }
        
        # Get last alert trigger time
        try:
            db = next(get_db())
            last_alert = db.query(AlertHistory).order_by(AlertHistory.triggered_at.desc()).first()
            if last_alert:
                health["last_alert_trigger"] = last_alert.triggered_at.isoformat()
        except Exception as e:
            logger.error(f"Error getting last alert trigger: {e}")
        
        return health
    
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics"""
        return {
            "request_rate": REQUEST_COUNT._value.sum(),
            "average_response_time": REQUEST_DURATION.observe(0),  # This is a placeholder
            "alert_trigger_rate": ALERT_TRIGGER_COUNT._value.sum(),
            "sms_success_rate": SMS_SENT_COUNT._value.sum(),
        }

# Middleware for request tracking
async def monitoring_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    # Track request if monitoring service is available
    if hasattr(request.app.state, 'monitoring'):
        request.app.state.monitoring.track_request(request, response, duration)
    
    return response

# Prometheus metrics endpoint
def metrics_endpoint():
    """Return Prometheus metrics"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    ) 