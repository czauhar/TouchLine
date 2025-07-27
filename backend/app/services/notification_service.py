import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from ..utils.logger import log_system_event
from ..websocket_manager import websocket_manager

class NotificationType(Enum):
    """Types of notifications"""
    ALERT_TRIGGERED = "alert_triggered"
    SYSTEM_HEALTH = "system_health"
    MATCH_UPDATE = "match_update"
    PERFORMANCE_ALERT = "performance_alert"
    ERROR_NOTIFICATION = "error_notification"
    USER_ACTION = "user_action"

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Notification:
    """Notification data structure"""
    id: str
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[int] = None
    read: bool = False
    expires_at: Optional[datetime] = None

class NotificationService:
    """Service for managing real-time notifications"""
    
    def __init__(self):
        self.active_notifications: Dict[str, Notification] = {}
        self.user_notifications: Dict[int, List[str]] = {}
        self.max_notifications_per_user = 100
    
    def _generate_notification_id(self) -> str:
        """Generate unique notification ID"""
        return f"notif_{datetime.utcnow().timestamp()}_{id(self)}"
    
    async def send_alert_notification(self, user_id: int, alert_id: int, alert_name: str, 
                                    match_info: Dict, trigger_message: str):
        """Send alert trigger notification"""
        notification = Notification(
            id=self._generate_notification_id(),
            type=NotificationType.ALERT_TRIGGERED,
            priority=NotificationPriority.HIGH,
            title=f"Alert Triggered: {alert_name}",
            message=trigger_message,
            data={
                "alert_id": alert_id,
                "alert_name": alert_name,
                "match_info": match_info,
                "trigger_message": trigger_message
            },
            timestamp=datetime.utcnow(),
            user_id=user_id
        )
        
        await self._send_notification(notification)
        log_system_event("alert_notification_sent", {
            "user_id": user_id,
            "alert_id": alert_id,
            "notification_id": notification.id
        })
    
    async def send_system_health_notification(self, health_status: str, details: Dict[str, Any]):
        """Send system health notification to all users"""
        notification = Notification(
            id=self._generate_notification_id(),
            type=NotificationType.SYSTEM_HEALTH,
            priority=NotificationPriority.MEDIUM if health_status == "degraded" else NotificationPriority.HIGH,
            title=f"System Status: {health_status.title()}",
            message=f"System health status changed to {health_status}",
            data={
                "health_status": health_status,
                "details": details
            },
            timestamp=datetime.utcnow()
        )
        
        await self._broadcast_notification(notification)
        log_system_event("system_health_notification_sent", {
            "health_status": health_status,
            "notification_id": notification.id
        })
    
    async def send_performance_alert(self, metric_name: str, value: float, threshold: float, 
                                   severity: str = "warning"):
        """Send performance alert notification"""
        priority = NotificationPriority.CRITICAL if severity == "critical" else NotificationPriority.HIGH
        
        notification = Notification(
            id=self._generate_notification_id(),
            type=NotificationType.PERFORMANCE_ALERT,
            priority=priority,
            title=f"Performance Alert: {metric_name}",
            message=f"{metric_name} is {value} (threshold: {threshold})",
            data={
                "metric_name": metric_name,
                "value": value,
                "threshold": threshold,
                "severity": severity
            },
            timestamp=datetime.utcnow()
        )
        
        await self._broadcast_notification(notification)
        log_system_event("performance_alert_sent", {
            "metric_name": metric_name,
            "value": value,
            "severity": severity,
            "notification_id": notification.id
        })
    
    async def send_match_update_notification(self, match_id: str, match_info: Dict, 
                                           update_type: str = "score_change"):
        """Send match update notification"""
        notification = Notification(
            id=self._generate_notification_id(),
            type=NotificationType.MATCH_UPDATE,
            priority=NotificationPriority.MEDIUM,
            title=f"Match Update: {match_info.get('home_team', '')} vs {match_info.get('away_team', '')}",
            message=f"Match {update_type}: {match_info.get('home_team', '')} {match_info.get('home_score', 0)} - {match_info.get('away_score', 0)} {match_info.get('away_team', '')}",
            data={
                "match_id": match_id,
                "match_info": match_info,
                "update_type": update_type
            },
            timestamp=datetime.utcnow()
        )
        
        await self._broadcast_notification(notification)
        log_system_event("match_update_notification_sent", {
            "match_id": match_id,
            "update_type": update_type,
            "notification_id": notification.id
        })
    
    async def send_error_notification(self, error_type: str, error_message: str, 
                                    error_details: Dict[str, Any] = None):
        """Send error notification to administrators"""
        notification = Notification(
            id=self._generate_notification_id(),
            type=NotificationType.ERROR_NOTIFICATION,
            priority=NotificationPriority.CRITICAL,
            title=f"System Error: {error_type}",
            message=error_message,
            data={
                "error_type": error_type,
                "error_message": error_message,
                "error_details": error_details or {}
            },
            timestamp=datetime.utcnow()
        )
        
        await self._broadcast_notification(notification)
        log_system_event("error_notification_sent", {
            "error_type": error_type,
            "notification_id": notification.id
        })
    
    async def _send_notification(self, notification: Notification):
        """Send notification to specific user"""
        if notification.user_id:
            # Store notification for user
            if notification.user_id not in self.user_notifications:
                self.user_notifications[notification.user_id] = []
            
            self.user_notifications[notification.user_id].append(notification.id)
            
            # Limit notifications per user
            while len(self.user_notifications[notification.user_id]) > self.max_notifications_per_user:
                old_notification_id = self.user_notifications[notification.user_id].pop(0)
                if old_notification_id in self.active_notifications:
                    del self.active_notifications[old_notification_id]
            
            # Store notification
            self.active_notifications[notification.id] = notification
            
            # Send via WebSocket
            await websocket_manager.send_notification(notification.user_id, asdict(notification))
    
    async def _broadcast_notification(self, notification: Notification):
        """Broadcast notification to all connected users"""
        # Store notification
        self.active_notifications[notification.id] = notification
        
        # Broadcast via WebSocket
        await websocket_manager.broadcast_notification(asdict(notification))
    
    def get_user_notifications(self, user_id: int, limit: int = 50) -> List[Notification]:
        """Get notifications for a specific user"""
        if user_id not in self.user_notifications:
            return []
        
        notifications = []
        for notification_id in reversed(self.user_notifications[user_id][-limit:]):
            if notification_id in self.active_notifications:
                notifications.append(self.active_notifications[notification_id])
        
        return notifications
    
    def mark_notification_read(self, user_id: int, notification_id: str) -> bool:
        """Mark a notification as read"""
        if notification_id in self.active_notifications:
            notification = self.active_notifications[notification_id]
            if notification.user_id == user_id:
                notification.read = True
                return True
        return False
    
    def delete_notification(self, user_id: int, notification_id: str) -> bool:
        """Delete a notification for a user"""
        if notification_id in self.active_notifications:
            notification = self.active_notifications[notification_id]
            if notification.user_id == user_id:
                # Remove from user's notification list
                if user_id in self.user_notifications:
                    self.user_notifications[user_id] = [
                        nid for nid in self.user_notifications[user_id] 
                        if nid != notification_id
                    ]
                
                # Remove from active notifications
                del self.active_notifications[notification_id]
                return True
        return False
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        total_notifications = len(self.active_notifications)
        unread_count = sum(1 for n in self.active_notifications.values() if not n.read)
        
        type_counts = {}
        for notification in self.active_notifications.values():
            type_name = notification.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return {
            "total_notifications": total_notifications,
            "unread_count": unread_count,
            "type_counts": type_counts,
            "active_users": len(self.user_notifications)
        }
    
    async def cleanup_expired_notifications(self):
        """Clean up expired notifications"""
        current_time = datetime.utcnow()
        expired_notifications = []
        
        for notification_id, notification in self.active_notifications.items():
            if notification.expires_at and notification.expires_at < current_time:
                expired_notifications.append(notification_id)
        
        for notification_id in expired_notifications:
            # Remove from user's notification list
            for user_id, notification_list in self.user_notifications.items():
                if notification_id in notification_list:
                    notification_list.remove(notification_id)
            
            # Remove from active notifications
            del self.active_notifications[notification_id]
        
        if expired_notifications:
            log_system_event("notifications_cleaned_up", {
                "expired_count": len(expired_notifications)
            })

# Global notification service instance
notification_service = NotificationService() 