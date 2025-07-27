import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
import json

from ..database import get_db
from ..models import Alert, AlertHistory, User, Match
from ..utils.logger import log_system_event, log_user_action

@dataclass
class AlertPerformance:
    """Alert performance metrics"""
    alert_id: int
    alert_name: str
    total_triggers: int
    success_rate: float
    avg_response_time: float
    last_triggered: Optional[datetime]
    most_common_matches: List[str]
    trigger_trend: List[Dict[str, Any]]

@dataclass
class UserAnalytics:
    """User behavior analytics"""
    user_id: int
    username: str
    total_alerts: int
    active_alerts: int
    total_triggers: int
    avg_alerts_per_day: float
    most_used_alert_types: List[str]
    activity_trend: List[Dict[str, Any]]

@dataclass
class SystemAnalytics:
    """System-wide analytics"""
    total_users: int
    total_alerts: int
    total_triggers: int
    avg_response_time: float
    peak_usage_hours: List[int]
    most_popular_teams: List[str]
    alert_type_distribution: Dict[str, int]
    system_performance_trend: List[Dict[str, Any]]

class AnalyticsService:
    """Service for comprehensive analytics and insights"""
    
    def __init__(self):
        self.cache_duration = 300  # 5 minutes
        self.cached_data = {}
        self.cache_timestamps = {}
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache_timestamps:
            return False
        return (datetime.utcnow() - self.cache_timestamps[key]).total_seconds() < self.cache_duration
    
    def _update_cache(self, key: str, data: Any):
        """Update cache with new data"""
        self.cached_data[key] = data
        self.cache_timestamps[key] = datetime.utcnow()
    
    async def get_alert_performance(self, alert_id: int) -> Optional[AlertPerformance]:
        """Get detailed performance analytics for a specific alert"""
        cache_key = f"alert_performance_{alert_id}"
        
        if self._is_cache_valid(cache_key):
            return self.cached_data[cache_key]
        
        try:
            db = next(get_db())
            
            # Get alert details
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                return None
            
            # Get trigger history
            triggers = db.query(AlertHistory).filter(
                AlertHistory.alert_id == alert_id
            ).order_by(desc(AlertHistory.triggered_at)).all()
            
            if not triggers:
                return AlertPerformance(
                    alert_id=alert_id,
                    alert_name=alert.name,
                    total_triggers=0,
                    success_rate=0.0,
                    avg_response_time=0.0,
                    last_triggered=None,
                    most_common_matches=[],
                    trigger_trend=[]
                )
            
            # Calculate metrics
            total_triggers = len(triggers)
            successful_triggers = sum(1 for t in triggers if t.sms_sent)
            success_rate = (successful_triggers / total_triggers) * 100 if total_triggers > 0 else 0
            
            # Calculate average response time (approximate)
            response_times = []
            for trigger in triggers:
                if trigger.triggered_at and alert.created_at:
                    response_time = (trigger.triggered_at - alert.created_at).total_seconds()
                    response_times.append(response_time)
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Get most common matches
            match_counts = {}
            for trigger in triggers:
                match_id = trigger.match_id
                match_counts[match_id] = match_counts.get(match_id, 0) + 1
            
            most_common_matches = sorted(match_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Calculate trigger trend (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_triggers = [t for t in triggers if t.triggered_at >= thirty_days_ago]
            
            trigger_trend = []
            for i in range(30):
                date = thirty_days_ago + timedelta(days=i)
                day_triggers = [t for t in recent_triggers if t.triggered_at.date() == date.date()]
                trigger_trend.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "triggers": len(day_triggers)
                })
            
            performance = AlertPerformance(
                alert_id=alert_id,
                alert_name=alert.name,
                total_triggers=total_triggers,
                success_rate=success_rate,
                avg_response_time=avg_response_time,
                last_triggered=triggers[0].triggered_at if triggers else None,
                most_common_matches=[match_id for match_id, _ in most_common_matches],
                trigger_trend=trigger_trend
            )
            
            self._update_cache(cache_key, performance)
            return performance
            
        except Exception as e:
            log_system_event("analytics_error", {
                "error": str(e),
                "operation": "get_alert_performance",
                "alert_id": alert_id
            })
            return None
    
    async def get_user_analytics(self, user_id: int) -> Optional[UserAnalytics]:
        """Get comprehensive analytics for a specific user"""
        cache_key = f"user_analytics_{user_id}"
        
        if self._is_cache_valid(cache_key):
            return self.cached_data[cache_key]
        
        try:
            db = next(get_db())
            
            # Get user details
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # Get user's alerts
            user_alerts = db.query(Alert).filter(Alert.user_id == user_id).all()
            total_alerts = len(user_alerts)
            active_alerts = sum(1 for alert in user_alerts if alert.is_active)
            
            # Get total triggers for user's alerts
            alert_ids = [alert.id for alert in user_alerts]
            total_triggers = 0
            if alert_ids:
                total_triggers = db.query(func.count(AlertHistory.id)).filter(
                    AlertHistory.alert_id.in_(alert_ids)
                ).scalar()
            
            # Calculate average alerts per day
            if user_alerts:
                oldest_alert = min(user_alerts, key=lambda a: a.created_at)
                days_since_first = (datetime.utcnow() - oldest_alert.created_at).days
                avg_alerts_per_day = total_alerts / max(days_since_first, 1)
            else:
                avg_alerts_per_day = 0
            
            # Get most used alert types
            alert_type_counts = {}
            for alert in user_alerts:
                alert_type = alert.alert_type
                alert_type_counts[alert_type] = alert_type_counts.get(alert_type, 0) + 1
            
            most_used_alert_types = sorted(alert_type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Calculate activity trend (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_alerts = [a for a in user_alerts if a.created_at >= thirty_days_ago]
            
            activity_trend = []
            for i in range(30):
                date = thirty_days_ago + timedelta(days=i)
                day_alerts = [a for a in recent_alerts if a.created_at.date() == date.date()]
                activity_trend.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "alerts_created": len(day_alerts)
                })
            
            analytics = UserAnalytics(
                user_id=user_id,
                username=user.username,
                total_alerts=total_alerts,
                active_alerts=active_alerts,
                total_triggers=total_triggers,
                avg_alerts_per_day=avg_alerts_per_day,
                most_used_alert_types=[alert_type for alert_type, _ in most_used_alert_types],
                activity_trend=activity_trend
            )
            
            self._update_cache(cache_key, analytics)
            return analytics
            
        except Exception as e:
            log_system_event("analytics_error", {
                "error": str(e),
                "operation": "get_user_analytics",
                "user_id": user_id
            })
            return None
    
    async def get_system_analytics(self) -> SystemAnalytics:
        """Get system-wide analytics"""
        cache_key = "system_analytics"
        
        if self._is_cache_valid(cache_key):
            return self.cached_data[cache_key]
        
        try:
            db = next(get_db())
            
            # Basic counts
            total_users = db.query(func.count(User.id)).scalar()
            total_alerts = db.query(func.count(Alert.id)).scalar()
            total_triggers = db.query(func.count(AlertHistory.id)).scalar()
            
            # Calculate average response time
            response_times = []
            alerts_with_triggers = db.query(Alert, AlertHistory).join(
                AlertHistory, Alert.id == AlertHistory.alert_id
            ).all()
            
            for alert, trigger in alerts_with_triggers:
                if trigger.triggered_at and alert.created_at:
                    response_time = (trigger.triggered_at - alert.created_at).total_seconds()
                    response_times.append(response_time)
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Get peak usage hours (based on alert creation)
            hour_counts = {}
            for alert in db.query(Alert).all():
                hour = alert.created_at.hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
            peak_usage_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:6]
            peak_hours = [hour for hour, _ in peak_usage_hours]
            
            # Get most popular teams
            team_counts = {}
            for alert in db.query(Alert).all():
                team = alert.team
                team_counts[team] = team_counts.get(team, 0) + 1
            
            most_popular_teams = sorted(team_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            popular_teams = [team for team, _ in most_popular_teams]
            
            # Get alert type distribution
            alert_type_counts = {}
            for alert in db.query(Alert).all():
                alert_type = alert.alert_type
                alert_type_counts[alert_type] = alert_type_counts.get(alert_type, 0) + 1
            
            # Calculate system performance trend (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_alerts = db.query(Alert).filter(Alert.created_at >= thirty_days_ago).all()
            
            performance_trend = []
            for i in range(30):
                date = thirty_days_ago + timedelta(days=i)
                day_alerts = [a for a in recent_alerts if a.created_at.date() == date.date()]
                performance_trend.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "alerts_created": len(day_alerts)
                })
            
            analytics = SystemAnalytics(
                total_users=total_users,
                total_alerts=total_alerts,
                total_triggers=total_triggers,
                avg_response_time=avg_response_time,
                peak_usage_hours=peak_hours,
                most_popular_teams=popular_teams,
                alert_type_distribution=alert_type_counts,
                system_performance_trend=performance_trend
            )
            
            self._update_cache(cache_key, analytics)
            return analytics
            
        except Exception as e:
            log_system_event("analytics_error", {
                "error": str(e),
                "operation": "get_system_analytics"
            })
            return None
    
    async def get_alert_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get personalized alert recommendations for a user"""
        try:
            db = next(get_db())
            
            # Get user's current alerts
            user_alerts = db.query(Alert).filter(Alert.user_id == user_id).all()
            user_teams = [alert.team for alert in user_alerts]
            user_alert_types = [alert.alert_type for alert in user_alerts]
            
            # Get popular alert types the user doesn't have
            all_alert_types = db.query(Alert.alert_type, func.count(Alert.id)).group_by(
                Alert.alert_type
            ).order_by(desc(func.count(Alert.id))).all()
            
            missing_alert_types = []
            for alert_type, count in all_alert_types:
                if alert_type not in user_alert_types and count > 5:  # Only recommend popular types
                    missing_alert_types.append({
                        "type": alert_type,
                        "popularity": count,
                        "reason": f"Popular alert type used by {count} other users"
                    })
            
            # Get popular teams the user doesn't follow
            all_teams = db.query(Alert.team, func.count(Alert.id)).group_by(
                Alert.team
            ).order_by(desc(func.count(Alert.id))).all()
            
            missing_teams = []
            for team, count in all_teams:
                if team not in user_teams and count > 3:  # Only recommend popular teams
                    missing_teams.append({
                        "team": team,
                        "popularity": count,
                        "reason": f"Popular team with {count} alerts"
                    })
            
            # Combine recommendations
            recommendations = []
            recommendations.extend(missing_alert_types[:3])  # Top 3 missing alert types
            recommendations.extend(missing_teams[:3])  # Top 3 missing teams
            
            # Sort by popularity
            recommendations.sort(key=lambda x: x["popularity"], reverse=True)
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            log_system_event("analytics_error", {
                "error": str(e),
                "operation": "get_alert_recommendations",
                "user_id": user_id
            })
            return []
    
    async def get_performance_insights(self) -> Dict[str, Any]:
        """Get system performance insights"""
        try:
            db = next(get_db())
            
            # Get recent triggers (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_triggers = db.query(AlertHistory).filter(
                AlertHistory.triggered_at >= yesterday
            ).all()
            
            # Calculate success rate
            total_recent = len(recent_triggers)
            successful_recent = sum(1 for t in recent_triggers if t.sms_sent)
            success_rate = (successful_recent / total_recent * 100) if total_recent > 0 else 0
            
            # Get most active alerts
            alert_activity = db.query(
                Alert.id, Alert.name, func.count(AlertHistory.id)
            ).join(AlertHistory).filter(
                AlertHistory.triggered_at >= yesterday
            ).group_by(Alert.id, Alert.name).order_by(
                desc(func.count(AlertHistory.id))
            ).limit(5).all()
            
            most_active_alerts = [
                {"id": alert_id, "name": name, "triggers": count}
                for alert_id, name, count in alert_activity
            ]
            
            # Get system load by hour
            hour_load = {}
            for trigger in recent_triggers:
                hour = trigger.triggered_at.hour
                hour_load[hour] = hour_load.get(hour, 0) + 1
            
            return {
                "success_rate_24h": success_rate,
                "total_triggers_24h": total_recent,
                "most_active_alerts": most_active_alerts,
                "hourly_load": hour_load,
                "insights": [
                    f"System processed {total_recent} alerts in the last 24 hours",
                    f"Success rate: {success_rate:.1f}%",
                    f"Peak activity hour: {max(hour_load.items(), key=lambda x: x[1])[0]}:00" if hour_load else "No recent activity"
                ]
            }
            
        except Exception as e:
            log_system_event("analytics_error", {
                "error": str(e),
                "operation": "get_performance_insights"
            })
            return {}
    
    def clear_cache(self):
        """Clear all cached analytics data"""
        self.cached_data.clear()
        self.cache_timestamps.clear()
        log_system_event("analytics_cache_cleared", {})

# Global analytics service instance
analytics_service = AnalyticsService() 