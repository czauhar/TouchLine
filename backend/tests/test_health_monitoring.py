import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to the path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.health_monitor import (
    HealthMonitor, HealthStatus, SystemMetrics, DatabaseMetrics, 
    APIMetrics, AlertMetrics, HealthReport
)
from main import app

client = TestClient(app)

class TestHealthMonitor:
    """Test cases for the health monitoring system"""
    
    @pytest.fixture
    def health_monitor(self):
        """Create a fresh health monitor instance for each test"""
        return HealthMonitor()
    
    @pytest.fixture
    def mock_system_metrics(self):
        """Mock system metrics"""
        return SystemMetrics(
            cpu_percent=25.5,
            memory_percent=45.2,
            disk_percent=30.1,
            network_io={
                "bytes_sent": 1024000,
                "bytes_recv": 2048000,
                "packets_sent": 1000,
                "packets_recv": 2000
            },
            uptime=3600.0,
            timestamp=datetime.utcnow()
        )
    
    @pytest.fixture
    def mock_database_metrics(self):
        """Mock database metrics"""
        return DatabaseMetrics(
            connection_status=True,
            response_time=0.05,
            active_connections=1,
            table_count=8,
            last_backup=None,
            timestamp=datetime.utcnow()
        )
    
    @pytest.fixture
    def mock_api_metrics(self):
        """Mock API metrics"""
        return APIMetrics(
            sports_api_status=True,
            sports_api_response_time=0.2,
            sms_service_status=True,
            sms_service_response_time=0.1,
            last_successful_call=datetime.utcnow(),
            error_count=0,
            timestamp=datetime.utcnow()
        )
    
    @pytest.fixture
    def mock_alert_metrics(self):
        """Mock alert metrics"""
        return AlertMetrics(
            active_alerts=5,
            alerts_triggered_today=3,
            sms_sent_today=3,
            sms_failed_today=0,
            average_response_time=2.5,
            last_trigger=datetime.utcnow(),
            timestamp=datetime.utcnow()
        )
    
    def test_health_status_enum(self):
        """Test health status enum values"""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"
    
    def test_system_metrics_dataclass(self, mock_system_metrics):
        """Test system metrics dataclass"""
        assert mock_system_metrics.cpu_percent == 25.5
        assert mock_system_metrics.memory_percent == 45.2
        assert mock_system_metrics.disk_percent == 30.1
        assert mock_system_metrics.uptime == 3600.0
        assert isinstance(mock_system_metrics.timestamp, datetime)
    
    def test_database_metrics_dataclass(self, mock_database_metrics):
        """Test database metrics dataclass"""
        assert mock_database_metrics.connection_status is True
        assert mock_database_metrics.response_time == 0.05
        assert mock_database_metrics.active_connections == 1
        assert mock_database_metrics.table_count == 8
        assert isinstance(mock_database_metrics.timestamp, datetime)
    
    def test_api_metrics_dataclass(self, mock_api_metrics):
        """Test API metrics dataclass"""
        assert mock_api_metrics.sports_api_status is True
        assert mock_api_metrics.sms_service_status is True
        assert mock_api_metrics.sports_api_response_time == 0.2
        assert mock_api_metrics.sms_service_response_time == 0.1
        assert mock_api_metrics.error_count == 0
        assert isinstance(mock_api_metrics.timestamp, datetime)
    
    def test_alert_metrics_dataclass(self, mock_alert_metrics):
        """Test alert metrics dataclass"""
        assert mock_alert_metrics.active_alerts == 5
        assert mock_alert_metrics.alerts_triggered_today == 3
        assert mock_alert_metrics.sms_sent_today == 3
        assert mock_alert_metrics.sms_failed_today == 0
        assert mock_alert_metrics.average_response_time == 2.5
        assert isinstance(mock_alert_metrics.timestamp, datetime)
    
    def test_health_report_dataclass(self, mock_system_metrics, mock_database_metrics, 
                                   mock_api_metrics, mock_alert_metrics):
        """Test health report dataclass"""
        report = HealthReport(
            overall_status=HealthStatus.HEALTHY,
            system_metrics=mock_system_metrics,
            database_metrics=mock_database_metrics,
            api_metrics=mock_api_metrics,
            alert_metrics=mock_alert_metrics,
            timestamp=datetime.utcnow()
        )
        
        assert report.overall_status == HealthStatus.HEALTHY
        assert report.system_metrics == mock_system_metrics
        assert report.database_metrics == mock_database_metrics
        assert report.api_metrics == mock_api_metrics
        assert report.alert_metrics == mock_alert_metrics
        assert report.version == "1.0.0"
    
    def test_health_monitor_initialization(self, health_monitor):
        """Test health monitor initialization"""
        assert health_monitor.last_check is None
        assert len(health_monitor.health_history) == 0
        assert health_monitor.error_counts == {
            "sports_api": 0,
            "sms_service": 0,
            "database": 0
        }
        assert health_monitor.max_history_size == 100
    
    @patch('app.services.health_monitor.psutil')
    async def test_get_system_metrics_success(self, mock_psutil, health_monitor):
        """Test successful system metrics collection"""
        # Mock psutil responses
        mock_psutil.cpu_percent.return_value = 25.5
        mock_psutil.virtual_memory.return_value = Mock(percent=45.2)
        mock_psutil.disk_usage.return_value = Mock(percent=30.1)
        mock_psutil.net_io_counters.return_value = Mock(
            bytes_sent=1024000,
            bytes_recv=2048000,
            packets_sent=1000,
            packets_recv=2000
        )
        mock_psutil.boot_time.return_value = datetime.now().timestamp() - 3600
        
        metrics = await health_monitor.get_system_metrics()
        
        assert metrics.cpu_percent == 25.5
        assert metrics.memory_percent == 45.2
        assert metrics.disk_percent == 30.1
        assert metrics.network_io["bytes_sent"] == 1024000
        assert metrics.network_io["bytes_recv"] == 2048000
        assert metrics.uptime > 0
        assert isinstance(metrics.timestamp, datetime)
    
    @patch('app.services.health_monitor.psutil')
    async def test_get_system_metrics_error(self, mock_psutil, health_monitor):
        """Test system metrics collection with error"""
        mock_psutil.cpu_percent.side_effect = Exception("CPU error")
        
        metrics = await health_monitor.get_system_metrics()
        
        # Should return default metrics on error
        assert metrics.cpu_percent == 0.0
        assert metrics.memory_percent == 0.0
        assert metrics.disk_percent == 0.0
        assert isinstance(metrics.timestamp, datetime)
    
    @patch('app.services.health_monitor.get_db')
    async def test_get_database_metrics_success(self, mock_get_db, health_monitor):
        """Test successful database metrics collection"""
        mock_db = Mock()
        mock_db.execute.return_value.fetchone.return_value = (1,)
        mock_db.execute.return_value.fetchall.return_value = [("users",), ("alerts",), ("matches",)]
        mock_get_db.return_value = iter([mock_db])
        
        metrics = await health_monitor.get_database_metrics()
        
        assert metrics.connection_status is True
        assert metrics.response_time > 0
        assert metrics.active_connections == 1
        assert metrics.table_count == 3
        assert isinstance(metrics.timestamp, datetime)
    
    @patch('app.services.health_monitor.get_db')
    async def test_get_database_metrics_error(self, mock_get_db, health_monitor):
        """Test database metrics collection with error"""
        mock_get_db.side_effect = Exception("Database error")
        
        metrics = await health_monitor.get_database_metrics()
        
        assert metrics.connection_status is False
        assert metrics.response_time > 0
        assert metrics.active_connections == 0
        assert metrics.table_count == 0
        assert health_monitor.error_counts["database"] == 1
    
    @patch('app.services.health_monitor.sports_api')
    @patch('app.services.health_monitor.sms_service')
    async def test_get_api_metrics_success(self, mock_sms_service, mock_sports_api, health_monitor):
        """Test successful API metrics collection"""
        # Mock sports API
        mock_sports_api.get_live_matches = AsyncMock(return_value=[])
        
        # Mock SMS service
        mock_sms_service.is_configured.return_value = True
        
        metrics = await health_monitor.get_api_metrics()
        
        assert metrics.sports_api_status is True
        assert metrics.sms_service_status is True
        assert metrics.sports_api_response_time > 0
        assert metrics.sms_service_response_time > 0
        assert metrics.error_count == 0
        assert isinstance(metrics.timestamp, datetime)
    
    @patch('app.services.health_monitor.sports_api')
    @patch('app.services.health_monitor.sms_service')
    async def test_get_api_metrics_error(self, mock_sms_service, mock_sports_api, health_monitor):
        """Test API metrics collection with error"""
        # Mock sports API error
        mock_sports_api.get_live_matches = AsyncMock(side_effect=Exception("API error"))
        
        # Mock SMS service error
        mock_sms_service.is_configured.side_effect = Exception("SMS error")
        
        metrics = await health_monitor.get_api_metrics()
        
        assert metrics.sports_api_status is False
        assert metrics.sms_service_status is False
        assert metrics.error_count == 2
        assert health_monitor.error_counts["sports_api"] == 1
        assert health_monitor.error_counts["sms_service"] == 1
    
    @patch('app.services.health_monitor.get_db')
    async def test_get_alert_metrics_success(self, mock_get_db, health_monitor):
        """Test successful alert metrics collection"""
        mock_db = Mock()
        mock_db.execute.return_value.scalar.side_effect = [5, 3, 3, 0, 2.5, "2024-01-01T12:00:00"]
        mock_get_db.return_value = iter([mock_db])
        
        metrics = await health_monitor.get_alert_metrics()
        
        assert metrics.active_alerts == 5
        assert metrics.alerts_triggered_today == 3
        assert metrics.sms_sent_today == 3
        assert metrics.sms_failed_today == 0
        assert metrics.average_response_time == 2.5
        assert isinstance(metrics.timestamp, datetime)
    
    def test_determine_overall_status_healthy(self, health_monitor, mock_system_metrics, 
                                            mock_database_metrics, mock_api_metrics, mock_alert_metrics):
        """Test overall status determination for healthy system"""
        status = health_monitor.determine_overall_status(
            mock_system_metrics, mock_database_metrics, mock_api_metrics, mock_alert_metrics
        )
        assert status == HealthStatus.HEALTHY
    
    def test_determine_overall_status_unhealthy_database(self, health_monitor, mock_system_metrics, 
                                                        mock_api_metrics, mock_alert_metrics):
        """Test overall status determination for unhealthy database"""
        unhealthy_db = DatabaseMetrics(
            connection_status=False,
            response_time=1.0,
            active_connections=0,
            table_count=0,
            last_backup=None,
            timestamp=datetime.utcnow()
        )
        
        status = health_monitor.determine_overall_status(
            mock_system_metrics, unhealthy_db, mock_api_metrics, mock_alert_metrics
        )
        assert status == HealthStatus.UNHEALTHY
    
    def test_determine_overall_status_degraded_api(self, health_monitor, mock_system_metrics, 
                                                  mock_database_metrics, mock_alert_metrics):
        """Test overall status determination for degraded API"""
        degraded_api = APIMetrics(
            sports_api_status=False,
            sports_api_response_time=5.0,
            sms_service_status=True,
            sms_service_response_time=0.1,
            last_successful_call=None,
            error_count=15,
            timestamp=datetime.utcnow()
        )
        
        status = health_monitor.determine_overall_status(
            mock_system_metrics, mock_database_metrics, degraded_api, mock_alert_metrics
        )
        assert status == HealthStatus.DEGRADED
    
    def test_determine_overall_status_degraded_resources(self, health_monitor, mock_database_metrics, 
                                                        mock_api_metrics, mock_alert_metrics):
        """Test overall status determination for degraded system resources"""
        degraded_system = SystemMetrics(
            cpu_percent=95.0,
            memory_percent=92.0,
            disk_percent=85.0,
            network_io={},
            uptime=3600.0,
            timestamp=datetime.utcnow()
        )
        
        status = health_monitor.determine_overall_status(
            degraded_system, mock_database_metrics, mock_api_metrics, mock_alert_metrics
        )
        assert status == HealthStatus.DEGRADED
    
    @patch('app.services.health_monitor.HealthMonitor.get_system_metrics')
    @patch('app.services.health_monitor.HealthMonitor.get_database_metrics')
    @patch('app.services.health_monitor.HealthMonitor.get_api_metrics')
    @patch('app.services.health_monitor.HealthMonitor.get_alert_metrics')
    async def test_generate_health_report(self, mock_alert_metrics, mock_api_metrics, 
                                        mock_database_metrics, mock_system_metrics, health_monitor,
                                        mock_system_metrics_fixture, mock_database_metrics_fixture,
                                        mock_api_metrics_fixture, mock_alert_metrics_fixture):
        """Test complete health report generation"""
        # Setup mocks
        mock_system_metrics.return_value = mock_system_metrics_fixture
        mock_database_metrics.return_value = mock_database_metrics_fixture
        mock_api_metrics.return_value = mock_api_metrics_fixture
        mock_alert_metrics.return_value = mock_alert_metrics_fixture
        
        report = await health_monitor.generate_health_report()
        
        assert isinstance(report, HealthReport)
        assert report.overall_status == HealthStatus.HEALTHY
        assert len(health_monitor.health_history) == 1
        assert health_monitor.last_check is not None
    
    def test_get_health_history(self, health_monitor):
        """Test health history retrieval"""
        # Add some mock reports
        for i in range(5):
            report = HealthReport(
                overall_status=HealthStatus.HEALTHY,
                system_metrics=Mock(),
                database_metrics=Mock(),
                api_metrics=Mock(),
                alert_metrics=Mock(),
                timestamp=datetime.utcnow() - timedelta(hours=i)
            )
            health_monitor.health_history.append(report)
        
        # Test history retrieval
        history = health_monitor.get_health_history(hours=3)
        assert len(history) == 4  # Should include reports from last 3 hours
        
        history = health_monitor.get_health_history(hours=1)
        assert len(history) == 2  # Should include reports from last 1 hour
    
    def test_get_health_summary(self, health_monitor, mock_system_metrics, mock_database_metrics, 
                               mock_api_metrics, mock_alert_metrics):
        """Test health summary generation"""
        # Add a mock report
        report = HealthReport(
            overall_status=HealthStatus.HEALTHY,
            system_metrics=mock_system_metrics,
            database_metrics=mock_database_metrics,
            api_metrics=mock_api_metrics,
            alert_metrics=mock_alert_metrics,
            timestamp=datetime.utcnow()
        )
        health_monitor.health_history.append(report)
        
        summary = health_monitor.get_health_summary()
        
        assert summary["status"] == "healthy"
        assert "last_check" in summary
        assert "system" in summary
        assert "database" in summary
        assert "api" in summary
        assert "alerts" in summary
    
    def test_get_health_summary_no_history(self, health_monitor):
        """Test health summary with no history"""
        summary = health_monitor.get_health_summary()
        
        assert summary["status"] == "unknown"
        assert summary["last_check"] is None

class TestHealthEndpoints:
    """Test cases for health check endpoints"""
    
    def test_basic_health_check(self):
        """Test basic health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "TouchLine Backend"
    
    @patch('app.services.health_monitor.health_monitor')
    def test_detailed_health_check_success(self, mock_health_monitor):
        """Test detailed health check endpoint success"""
        mock_summary = {
            "status": "healthy",
            "last_check": "2024-01-01T12:00:00",
            "system": {"cpu_percent": 25.5},
            "database": {"connection_status": True},
            "api": {"sports_api_status": True},
            "alerts": {"active_alerts": 5}
        }
        mock_health_monitor.generate_health_report = AsyncMock()
        mock_health_monitor.get_health_summary.return_value = mock_summary
        
        response = client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "system" in data
        assert "database" in data
        assert "api" in data
        assert "alerts" in data
    
    @patch('app.services.health_monitor.health_monitor')
    def test_detailed_health_check_error(self, mock_health_monitor):
        """Test detailed health check endpoint error"""
        mock_health_monitor.generate_health_report = AsyncMock(side_effect=Exception("Health check failed"))
        
        response = client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "error" in data
    
    @patch('app.services.health_monitor.health_monitor')
    def test_health_history(self, mock_health_monitor):
        """Test health history endpoint"""
        mock_history = [
            {
                "timestamp": "2024-01-01T12:00:00",
                "status": "healthy",
                "system": {"cpu_percent": 25.5},
                "database": {"connection_status": True},
                "api": {"sports_api_status": True}
            }
        ]
        mock_health_monitor.get_health_history.return_value = mock_history
        
        response = client.get("/health/history?hours=24")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert data["hours"] == 24
        assert len(data["history"]) == 1
    
    @patch('app.services.health_monitor.health_monitor')
    def test_health_history_error(self, mock_health_monitor):
        """Test health history endpoint error"""
        mock_health_monitor.get_health_history.side_effect = Exception("History error")
        
        response = client.get("/health/history")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["history"] == [] 