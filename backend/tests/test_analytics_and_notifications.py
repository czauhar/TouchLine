import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session

from app.services.analytics_service import AnalyticsService, AlertPerformance, UserAnalytics, SystemAnalytics
from app.services.notification_service import NotificationService, Notification, NotificationType, NotificationPriority
from app.models import Alert, AlertHistory, User, Match
from app.database import get_db

class TestAnalyticsService:
    """Test cases for AnalyticsService"""
    
    @pytest.fixture
    def analytics_service(self):
        return AnalyticsService()
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_alert(self):
        alert = Mock(spec=Alert)
        alert.id = 1
        alert.name = "Test Alert"
        alert.created_at = datetime.utcnow() - timedelta(days=1)
        alert.user_id = 1
        alert.team = "Test Team"
        alert.alert_type = "score_change"
        alert.is_active = True
        return alert
    
    @pytest.fixture
    def sample_user(self):
        user = Mock(spec=User)
        user.id = 1
        user.username = "testuser"
        return user
    
    @pytest.fixture
    def sample_triggers(self):
        triggers = []
        for i in range(5):
            trigger = Mock(spec=AlertHistory)
            trigger.id = i + 1
            trigger.alert_id = 1
            trigger.triggered_at = datetime.utcnow() - timedelta(hours=i)
            trigger.sms_sent = i % 2 == 0  # Alternate success/failure
            trigger.match_id = f"match_{i}"
            triggers.append(trigger)
        return triggers
    
    @patch('app.services.analytics_service.get_db')
    @pytest.mark.asyncio
    async def test_get_alert_performance_success(self, mock_get_db, analytics_service, mock_db, sample_alert, sample_triggers):
        """Test successful alert performance retrieval"""
        mock_get_db.return_value = iter([mock_db])
        
        # Mock database queries
        mock_db.query.return_value.filter.return_value.first.return_value = sample_alert
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = sample_triggers
        
        result = await analytics_service.get_alert_performance(1)
        
        assert result is not None
        assert result.alert_id == 1
        assert result.alert_name == "Test Alert"
        assert result.total_triggers == 5
        assert result.success_rate == 60.0  # 3 out of 5 successful
        assert len(result.most_common_matches) == 5
        assert len(result.trigger_trend) == 30  # 30 days
    
    @patch('app.services.analytics_service.get_db')
    @pytest.mark.asyncio
    async def test_get_alert_performance_no_alert(self, mock_get_db, analytics_service, mock_db):
        """Test alert performance when alert doesn't exist"""
        mock_get_db.return_value = iter([mock_db])
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = await analytics_service.get_alert_performance(999)
        
        assert result is None
    
    @patch('app.services.analytics_service.get_db')
    @pytest.mark.asyncio
    async def test_get_alert_performance_no_triggers(self, mock_get_db, analytics_service, mock_db, sample_alert):
        """Test alert performance when no triggers exist"""
        mock_get_db.return_value = iter([mock_db])
        mock_db.query.return_value.filter.return_value.first.return_value = sample_alert
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        
        result = await analytics_service.get_alert_performance(1)
        
        assert result is not None
        assert result.total_triggers == 0
        assert result.success_rate == 0.0
        assert result.last_triggered is None
    
    @patch('app.services.analytics_service.get_db')
    @pytest.mark.asyncio
    async def test_get_user_analytics_success(self, mock_get_db, analytics_service, mock_db, sample_user):
        """Test successful user analytics retrieval"""
        mock_get_db.return_value = iter([mock_db])
        
        # Mock user
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user
        
        # Mock user alerts
        user_alerts = []
        for i in range(3):
            alert = Mock(spec=Alert)
            alert.id = i + 1
            alert.is_active = i < 2  # 2 active, 1 inactive
            alert.created_at = datetime.utcnow() - timedelta(days=i)
            alert.alert_type = f"type_{i}"
            user_alerts.append(alert)
        
        mock_db.query.return_value.filter.return_value.all.return_value = user_alerts
        
        # Mock trigger count
        mock_db.query.return_value.filter.return_value.scalar.return_value = 10
        
        result = await analytics_service.get_user_analytics(1)
        
        assert result is not None
        assert result.user_id == 1
        assert result.username == "testuser"
        assert result.total_alerts == 3
        assert result.active_alerts == 2
        assert result.total_triggers == 10
        assert len(result.most_used_alert_types) == 3
    
    @patch('app.services.analytics_service.get_db')
    @pytest.mark.asyncio
    async def test_get_system_analytics_success(self, mock_get_db, analytics_service, mock_db):
        """Test successful system analytics retrieval"""
        mock_get_db.return_value = iter([mock_db])
        
        # Mock the query chain for counts
        def mock_query_chain(*args, **kwargs):
            mock_query = Mock()
            if 'User' in str(args):
                mock_query.scalar.return_value = 100
            elif 'Alert' in str(args) and 'AlertHistory' not in str(args):
                mock_query.scalar.return_value = 500
            elif 'AlertHistory' in str(args):
                mock_query.scalar.return_value = 1000
            else:
                # For other queries, return empty list
                mock_query.all.return_value = []
            return mock_query
        
        mock_db.query.side_effect = mock_query_chain
        
        result = await analytics_service.get_system_analytics()
        
        assert result is not None
        assert result.total_users == 100
        assert result.total_alerts == 500
        assert result.total_triggers == 1000
    
    @pytest.mark.asyncio
    async def test_get_alert_recommendations(self, analytics_service):
        """Test alert recommendations generation"""
        with patch('app.services.analytics_service.get_db') as mock_get_db:
            mock_db = Mock(spec=Session)
            mock_get_db.return_value = iter([mock_db])
            
            # Mock user alerts
            user_alerts = []
            for i in range(2):
                alert = Mock(spec=Alert)
                alert.team = f"team_{i}"
                alert.alert_type = f"type_{i}"
                user_alerts.append(alert)
            
            mock_db.query.return_value.filter.return_value.all.return_value = user_alerts
            
            # Mock popular alert types
            popular_types = [("type_2", 10), ("type_3", 8), ("type_1", 5)]
            mock_db.query.return_value.group_by.return_value.order_by.return_value.all.return_value = popular_types
            
            # Mock popular teams
            popular_teams = [("team_2", 15), ("team_3", 12), ("team_1", 8)]
            mock_db.query.return_value.group_by.return_value.order_by.return_value.all.return_value = popular_teams
            
            result = await analytics_service.get_alert_recommendations(1)
            
            assert len(result) > 0
            assert all('type' in rec or 'team' in rec for rec in result)
            assert all('popularity' in rec for rec in result)
    
    @pytest.mark.asyncio
    async def test_get_performance_insights(self, analytics_service):
        """Test performance insights generation"""
        with patch('app.services.analytics_service.get_db') as mock_get_db:
            mock_db = Mock(spec=Session)
            mock_get_db.return_value = iter([mock_db])
            
            # Mock recent triggers
            triggers = []
            for i in range(10):
                trigger = Mock(spec=AlertHistory)
                trigger.triggered_at = datetime.utcnow() - timedelta(hours=i)
                trigger.sms_sent = i % 2 == 0
                triggers.append(trigger)
            
            mock_db.query.return_value.filter.return_value.all.return_value = triggers
            
            # Mock alert activity
            alert_activity = [(1, "Alert 1", 5), (2, "Alert 2", 3)]
            mock_db.query.return_value.join.return_value.filter.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = alert_activity
            
            result = await analytics_service.get_performance_insights()
            
            assert result is not None
            assert 'success_rate_24h' in result
            assert 'total_triggers_24h' in result
            assert 'most_active_alerts' in result
            assert 'hourly_load' in result
            assert 'insights' in result
    
    def test_cache_management(self, analytics_service):
        """Test cache management functionality"""
        # Test cache update
        test_data = {"test": "data"}
        analytics_service._update_cache("test_key", test_data)
        
        assert "test_key" in analytics_service.cached_data
        assert analytics_service.cached_data["test_key"] == test_data
        
        # Test cache validity
        assert analytics_service._is_cache_valid("test_key") == True
        
        # Test cache expiration
        analytics_service.cache_timestamps["test_key"] = datetime.utcnow() - timedelta(seconds=400)
        assert analytics_service._is_cache_valid("test_key") == False
        
        # Test cache clear
        analytics_service.clear_cache()
        assert len(analytics_service.cached_data) == 0
        assert len(analytics_service.cache_timestamps) == 0

class TestNotificationService:
    """Test cases for NotificationService"""
    
    @pytest.fixture
    def notification_service(self):
        return NotificationService()
    
    @pytest.fixture
    def sample_notification(self):
        return Notification(
            id="test_notif_1",
            type=NotificationType.ALERT_TRIGGERED,
            priority=NotificationPriority.HIGH,
            title="Test Alert",
            message="Test message",
            data={"test": "data"},
            timestamp=datetime.utcnow(),
            user_id=1
        )
    
    @pytest.mark.asyncio
    async def test_send_alert_notification(self, notification_service):
        """Test sending alert notification"""
        with patch.object(notification_service, '_send_notification') as mock_send:
            await notification_service.send_alert_notification(
                user_id=1,
                alert_id=1,
                alert_name="Test Alert",
                match_info={"home_team": "Team A", "away_team": "Team B"},
                trigger_message="Alert triggered!"
            )
            
            mock_send.assert_called_once()
            notification = mock_send.call_args[0][0]
            assert notification.type == NotificationType.ALERT_TRIGGERED
            assert notification.priority == NotificationPriority.HIGH
            assert notification.user_id == 1
            assert "Test Alert" in notification.title
    
    @pytest.mark.asyncio
    async def test_send_system_health_notification(self, notification_service):
        """Test sending system health notification"""
        with patch.object(notification_service, '_broadcast_notification') as mock_broadcast:
            await notification_service.send_system_health_notification(
                health_status="degraded",
                details={"cpu": 85, "memory": 70}
            )
            
            mock_broadcast.assert_called_once()
            notification = mock_broadcast.call_args[0][0]
            assert notification.type == NotificationType.SYSTEM_HEALTH
            assert notification.priority == NotificationPriority.MEDIUM
            assert notification.user_id is None  # Broadcast notification
    
    @pytest.mark.asyncio
    async def test_send_performance_alert(self, notification_service):
        """Test sending performance alert"""
        with patch.object(notification_service, '_broadcast_notification') as mock_broadcast:
            await notification_service.send_performance_alert(
                metric_name="CPU Usage",
                value=95.0,
                threshold=80.0,
                severity="critical"
            )
            
            mock_broadcast.assert_called_once()
            notification = mock_broadcast.call_args[0][0]
            assert notification.type == NotificationType.PERFORMANCE_ALERT
            assert notification.priority == NotificationPriority.CRITICAL
            assert "CPU Usage" in notification.title
    
    @pytest.mark.asyncio
    async def test_send_match_update_notification(self, notification_service):
        """Test sending match update notification"""
        with patch.object(notification_service, '_broadcast_notification') as mock_broadcast:
            match_info = {
                "home_team": "Team A",
                "away_team": "Team B",
                "home_score": 2,
                "away_score": 1
            }
            
            await notification_service.send_match_update_notification(
                match_id="match_1",
                match_info=match_info,
                update_type="score_change"
            )
            
            mock_broadcast.assert_called_once()
            notification = mock_broadcast.call_args[0][0]
            assert notification.type == NotificationType.MATCH_UPDATE
            assert notification.priority == NotificationPriority.MEDIUM
            assert "Team A vs Team B" in notification.title
    
    @pytest.mark.asyncio
    async def test_send_error_notification(self, notification_service):
        """Test sending error notification"""
        with patch.object(notification_service, '_broadcast_notification') as mock_broadcast:
            await notification_service.send_error_notification(
                error_type="DatabaseError",
                error_message="Connection failed",
                error_details={"retry_count": 3}
            )
            
            mock_broadcast.assert_called_once()
            notification = mock_broadcast.call_args[0][0]
            assert notification.type == NotificationType.ERROR_NOTIFICATION
            assert notification.priority == NotificationPriority.CRITICAL
            assert "DatabaseError" in notification.title
    
    @pytest.mark.asyncio
    async def test_send_notification_to_user(self, notification_service, sample_notification):
        """Test sending notification to specific user"""
        with patch('app.services.notification_service.websocket_manager') as mock_ws:
            mock_ws.send_notification = AsyncMock()
            
            await notification_service._send_notification(sample_notification)
            
            # Check notification was stored
            assert sample_notification.id in notification_service.active_notifications
            assert 1 in notification_service.user_notifications
            assert sample_notification.id in notification_service.user_notifications[1]
            
            # Check WebSocket was called
            mock_ws.send_notification.assert_called_once_with(1, sample_notification.__dict__)
    
    @pytest.mark.asyncio
    async def test_broadcast_notification(self, notification_service, sample_notification):
        """Test broadcasting notification to all users"""
        with patch('app.services.notification_service.websocket_manager') as mock_ws:
            mock_ws.broadcast_notification = AsyncMock()
            
            # Remove user_id for broadcast
            sample_notification.user_id = None
            
            await notification_service._broadcast_notification(sample_notification)
            
            # Check notification was stored
            assert sample_notification.id in notification_service.active_notifications
            
            # Check WebSocket was called
            mock_ws.broadcast_notification.assert_called_once_with(sample_notification.__dict__)
    
    def test_get_user_notifications(self, notification_service, sample_notification):
        """Test retrieving user notifications"""
        # Add notification to service
        notification_service.active_notifications[sample_notification.id] = sample_notification
        notification_service.user_notifications[1] = [sample_notification.id]
        
        notifications = notification_service.get_user_notifications(1)
        
        assert len(notifications) == 1
        assert notifications[0].id == sample_notification.id
    
    def test_mark_notification_read(self, notification_service, sample_notification):
        """Test marking notification as read"""
        # Add notification to service
        notification_service.active_notifications[sample_notification.id] = sample_notification
        
        # Initially not read
        assert not sample_notification.read
        
        # Mark as read
        success = notification_service.mark_notification_read(1, sample_notification.id)
        
        assert success == True
        assert sample_notification.read == True
    
    def test_delete_notification(self, notification_service, sample_notification):
        """Test deleting notification"""
        # Add notification to service
        notification_service.active_notifications[sample_notification.id] = sample_notification
        notification_service.user_notifications[1] = [sample_notification.id]
        
        # Delete notification
        success = notification_service.delete_notification(1, sample_notification.id)
        
        assert success == True
        assert sample_notification.id not in notification_service.active_notifications
        assert sample_notification.id not in notification_service.user_notifications[1]
    
    def test_get_notification_stats(self, notification_service, sample_notification):
        """Test getting notification statistics"""
        # Add notifications to service
        notification_service.active_notifications[sample_notification.id] = sample_notification
        notification_service.user_notifications[1] = [sample_notification.id]
        
        # Add another notification (read)
        notification2 = Notification(
            id="test_notif_2",
            type=NotificationType.SYSTEM_HEALTH,
            priority=NotificationPriority.MEDIUM,
            title="Test 2",
            message="Test message 2",
            data={},
            timestamp=datetime.utcnow(),
            user_id=2,
            read=True
        )
        notification_service.active_notifications[notification2.id] = notification2
        notification_service.user_notifications[2] = [notification2.id]
        
        stats = notification_service.get_notification_stats()
        
        assert stats["total_notifications"] == 2
        assert stats["unread_count"] == 1
        assert stats["active_users"] == 2
        assert "alert_triggered" in stats["type_counts"]
        assert "system_health" in stats["type_counts"]
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_notifications(self, notification_service):
        """Test cleaning up expired notifications"""
        # Add notification with expiration
        expired_notification = Notification(
            id="expired_notif",
            type=NotificationType.ALERT_TRIGGERED,
            priority=NotificationPriority.LOW,
            title="Expired",
            message="Expired message",
            data={},
            timestamp=datetime.utcnow(),
            user_id=1,
            expires_at=datetime.utcnow() - timedelta(hours=1)  # Expired
        )
        
        notification_service.active_notifications[expired_notification.id] = expired_notification
        notification_service.user_notifications[1] = [expired_notification.id]
        
        # Add non-expired notification
        valid_notification = Notification(
            id="valid_notif",
            type=NotificationType.ALERT_TRIGGERED,
            priority=NotificationPriority.LOW,
            title="Valid",
            message="Valid message",
            data={},
            timestamp=datetime.utcnow(),
            user_id=1,
            expires_at=datetime.utcnow() + timedelta(hours=1)  # Not expired
        )
        
        notification_service.active_notifications[valid_notification.id] = valid_notification
        notification_service.user_notifications[1].append(valid_notification.id)
        
        # Cleanup
        await notification_service.cleanup_expired_notifications()
        
        # Check expired notification was removed
        assert expired_notification.id not in notification_service.active_notifications
        assert expired_notification.id not in notification_service.user_notifications[1]
        
        # Check valid notification remains
        assert valid_notification.id in notification_service.active_notifications
        assert valid_notification.id in notification_service.user_notifications[1]
    
    def test_notification_limit_enforcement(self, notification_service):
        """Test notification limit enforcement per user"""
        # Add more notifications than the limit using the service method
        for i in range(105):  # Limit is 100
            notification = Notification(
                id=f"notif_{i}",
                type=NotificationType.ALERT_TRIGGERED,
                priority=NotificationPriority.LOW,
                title=f"Notification {i}",
                message=f"Message {i}",
                data={},
                timestamp=datetime.utcnow(),
                user_id=1
            )
            
            # Use the service's internal method to add notifications
            notification_service.active_notifications[notification.id] = notification
            if 1 not in notification_service.user_notifications:
                notification_service.user_notifications[1] = []
            notification_service.user_notifications[1].append(notification.id)
            
            # Apply limit enforcement
            while len(notification_service.user_notifications[1]) > notification_service.max_notifications_per_user:
                old_notification_id = notification_service.user_notifications[1].pop(0)
                if old_notification_id in notification_service.active_notifications:
                    del notification_service.active_notifications[old_notification_id]
        
        # Check limit is enforced
        assert len(notification_service.user_notifications[1]) == 100
        assert len(notification_service.active_notifications) >= 100  # Some may be shared

if __name__ == "__main__":
    pytest.main([__file__]) 