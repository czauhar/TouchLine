import asyncio
import time
import psutil
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from ..database import get_db
from ..sports_api import sports_api
from ..sms_service import sms_service
from ..utils.logger import log_system_event, log_performance_metric
from ..core.exceptions import SportsAPIException, SMSException

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, float]
    uptime: float
    timestamp: datetime

@dataclass
class DatabaseMetrics:
    """Database health metrics"""
    connection_status: bool
    response_time: float
    active_connections: int
    table_count: int
    last_backup: Optional[datetime]
    timestamp: datetime

@dataclass
class APIMetrics:
    """External API health metrics"""
    sports_api_status: bool
    sports_api_response_time: float
    sms_service_status: bool
    sms_service_response_time: float
    last_successful_call: Optional[datetime]
    error_count: int
    timestamp: datetime

@dataclass
class AlertMetrics:
    """Alert system metrics"""
    active_alerts: int
    alerts_triggered_today: int
    sms_sent_today: int
    sms_failed_today: int
    average_response_time: float
    last_trigger: Optional[datetime]
    timestamp: datetime

@dataclass
class HealthReport:
    """Complete health report"""
    overall_status: HealthStatus
    system_metrics: SystemMetrics
    database_metrics: DatabaseMetrics
    api_metrics: APIMetrics
    alert_metrics: AlertMetrics
    timestamp: datetime
    version: str = "1.0.0"

class HealthMonitor:
    """Comprehensive health monitoring system"""
    
    def __init__(self):
        self.last_check = None
        self.health_history: List[HealthReport] = []
        self.error_counts = {
            "sports_api": 0,
            "sms_service": 0,
            "database": 0
        }
        self.max_history_size = 100
        
    async def get_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # Calculate uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = (datetime.now() - boot_time).total_seconds()
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                network_io={
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                uptime=uptime,
                timestamp=datetime.utcnow()
            )
            
            # Log performance metrics
            log_performance_metric("cpu_usage", cpu_percent, "%")
            log_performance_metric("memory_usage", memory.percent, "%")
            log_performance_metric("disk_usage", disk.percent, "%")
            
            return metrics
            
        except Exception as e:
            log_system_event("system_metrics_error", {"error": str(e)})
            # Return default metrics on error
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                network_io={},
                uptime=0.0,
                timestamp=datetime.utcnow()
            )
    
    async def get_database_metrics(self) -> DatabaseMetrics:
        """Get database health metrics"""
        start_time = time.time()
        connection_status = False
        active_connections = 0
        table_count = 0
        
        try:
            db = next(get_db())
            
            # Test connection with a simple query
            from sqlalchemy import text
            result = db.execute(text("SELECT 1")).fetchone()
            connection_status = result is not None
            
            # Get table count
            tables = db.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)).fetchall()
            table_count = len(tables)
            
            # Get active connections (approximate)
            active_connections = 1  # SQLite doesn't track connections like PostgreSQL
            
            response_time = time.time() - start_time
            
            metrics = DatabaseMetrics(
                connection_status=connection_status,
                response_time=response_time,
                active_connections=active_connections,
                table_count=table_count,
                last_backup=None,  # SQLite doesn't have built-in backup tracking
                timestamp=datetime.utcnow()
            )
            
            log_performance_metric("database_response_time", response_time * 1000, "ms")
            self.error_counts["database"] = 0
            
            return metrics
            
        except Exception as e:
            response_time = time.time() - start_time
            self.error_counts["database"] += 1
            
            log_system_event("database_health_error", {
                "error": str(e),
                "error_count": self.error_counts["database"]
            })
            
            return DatabaseMetrics(
                connection_status=False,
                response_time=response_time,
                active_connections=0,
                table_count=0,
                last_backup=None,
                timestamp=datetime.utcnow()
            )
    
    async def get_api_metrics(self) -> APIMetrics:
        """Get external API health metrics"""
        sports_api_status = False
        sports_api_response_time = 0.0
        sms_service_status = False
        sms_service_response_time = 0.0
        last_successful_call = None
        
        # Test Sports API
        try:
            start_time = time.time()
            # Make a simple API call to test connectivity
            test_response = await sports_api.get_live_matches()
            sports_api_response_time = time.time() - start_time
            sports_api_status = True
            last_successful_call = datetime.utcnow()
            self.error_counts["sports_api"] = 0
            
            log_performance_metric("sports_api_response_time", sports_api_response_time * 1000, "ms")
            
        except Exception as e:
            sports_api_response_time = time.time() - start_time
            self.error_counts["sports_api"] += 1
            
            log_system_event("sports_api_health_error", {
                "error": str(e),
                "error_count": self.error_counts["sports_api"]
            })
        
        # Test SMS Service
        try:
            start_time = time.time()
            # Test SMS service configuration (don't actually send)
            sms_config_valid = sms_service.check_configuration()
            sms_service_response_time = time.time() - start_time
            sms_service_status = sms_config_valid
            
            if sms_config_valid:
                self.error_counts["sms_service"] = 0
                log_performance_metric("sms_service_response_time", sms_service_response_time * 1000, "ms")
            
        except Exception as e:
            sms_service_response_time = time.time() - start_time
            self.error_counts["sms_service"] += 1
            
            log_system_event("sms_service_health_error", {
                "error": str(e),
                "error_count": self.error_counts["sms_service"]
            })
        
        return APIMetrics(
            sports_api_status=sports_api_status,
            sports_api_response_time=sports_api_response_time,
            sms_service_status=sms_service_status,
            sms_service_response_time=sms_service_response_time,
            last_successful_call=last_successful_call,
            error_count=sum(self.error_counts.values()),
            timestamp=datetime.utcnow()
        )
    
    async def get_alert_metrics(self) -> AlertMetrics:
        """Get alert system metrics"""
        try:
            from sqlalchemy import text
            db = next(get_db())
            
            # Get active alerts count
            active_alerts = db.execute(text("SELECT COUNT(*) FROM alerts WHERE is_active = 1")).scalar()
            
            # Get today's triggered alerts
            today = datetime.utcnow().date()
            alerts_triggered_today = db.execute(text("""
                SELECT COUNT(*) FROM alert_history 
                WHERE DATE(triggered_at) = :today
            """), {"today": today}).scalar()
            
            # Get SMS metrics for today
            sms_sent_today = db.execute(text("""
                SELECT COUNT(*) FROM alert_history 
                WHERE DATE(triggered_at) = :today AND sms_sent = 1
            """), {"today": today}).scalar()
            
            sms_failed_today = db.execute(text("""
                SELECT COUNT(*) FROM alert_history 
                WHERE DATE(triggered_at) = :today AND sms_sent = 0
            """), {"today": today}).scalar()
            
            # Get average response time (approximate)
            response_times = db.execute(text("""
                SELECT AVG(CAST((julianday(triggered_at) - julianday(created_at)) * 86400 AS INTEGER))
                FROM alert_history ah
                JOIN alerts a ON ah.alert_id = a.id
                WHERE ah.triggered_at >= datetime('now', '-1 hour')
            """)).scalar()
            
            average_response_time = response_times or 0.0
            
            # Get last trigger
            last_trigger = db.execute(text("""
                SELECT triggered_at FROM alert_history 
                ORDER BY triggered_at DESC LIMIT 1
            """)).scalar()
            
            last_trigger_dt = datetime.fromisoformat(last_trigger) if last_trigger else None
            
            return AlertMetrics(
                active_alerts=active_alerts,
                alerts_triggered_today=alerts_triggered_today,
                sms_sent_today=sms_sent_today,
                sms_failed_today=sms_failed_today,
                average_response_time=average_response_time,
                last_trigger=last_trigger_dt,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            log_system_event("alert_metrics_error", {"error": str(e)})
            
            return AlertMetrics(
                active_alerts=0,
                alerts_triggered_today=0,
                sms_sent_today=0,
                sms_failed_today=0,
                average_response_time=0.0,
                last_trigger=None,
                timestamp=datetime.utcnow()
            )
    
    def determine_overall_status(self, system: SystemMetrics, database: DatabaseMetrics, 
                               api: APIMetrics, alerts: AlertMetrics) -> HealthStatus:
        """Determine overall system health status"""
        # Check critical components
        if not database.connection_status:
            return HealthStatus.UNHEALTHY
        
        if not api.sports_api_status:
            return HealthStatus.DEGRADED
        
        # Check system resources
        if system.cpu_percent > 90 or system.memory_percent > 90:
            return HealthStatus.DEGRADED
        
        # Check error rates
        if api.error_count > 10:
            return HealthStatus.DEGRADED
        
        # Check alert system
        if alerts.sms_failed_today > alerts.sms_sent_today * 0.5:  # More than 50% failure rate
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    async def generate_health_report(self) -> HealthReport:
        """Generate a complete health report"""
        # Gather all metrics
        system_metrics = await self.get_system_metrics()
        database_metrics = await self.get_database_metrics()
        api_metrics = await self.get_api_metrics()
        alert_metrics = await self.get_alert_metrics()
        
        # Determine overall status
        overall_status = self.determine_overall_status(
            system_metrics, database_metrics, api_metrics, alert_metrics
        )
        
        # Create health report
        report = HealthReport(
            overall_status=overall_status,
            system_metrics=system_metrics,
            database_metrics=database_metrics,
            api_metrics=api_metrics,
            alert_metrics=alert_metrics,
            timestamp=datetime.utcnow()
        )
        
        # Store in history
        self.health_history.append(report)
        if len(self.health_history) > self.max_history_size:
            self.health_history.pop(0)
        
        self.last_check = datetime.utcnow()
        
        # Log health status
        log_system_event("health_check_completed", {
            "overall_status": overall_status.value,
            "system_healthy": system_metrics.cpu_percent < 90,
            "database_healthy": database_metrics.connection_status,
            "api_healthy": api_metrics.sports_api_status,
            "alert_healthy": alert_metrics.sms_failed_today < alert_metrics.sms_sent_today * 0.5
        })
        
        return report
    
    def get_health_history(self, hours: int = 24) -> List[HealthReport]:
        """Get health history for the specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            report for report in self.health_history
            if report.timestamp >= cutoff_time
        ]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of current health status"""
        if not self.health_history:
            return {"status": "unknown", "last_check": None}
        
        latest_report = self.health_history[-1]
        
        return {
            "status": latest_report.overall_status.value,
            "last_check": latest_report.timestamp.isoformat(),
            "system": {
                "cpu_percent": latest_report.system_metrics.cpu_percent,
                "memory_percent": latest_report.system_metrics.memory_percent,
                "disk_percent": latest_report.system_metrics.disk_percent
            },
            "database": {
                "connection_status": latest_report.database_metrics.connection_status,
                "response_time_ms": round(latest_report.database_metrics.response_time * 1000, 2)
            },
            "api": {
                "sports_api_status": latest_report.api_metrics.sports_api_status,
                "sms_service_status": latest_report.api_metrics.sms_service_status,
                "error_count": latest_report.api_metrics.error_count
            },
            "alerts": {
                "active_alerts": latest_report.alert_metrics.active_alerts,
                "alerts_triggered_today": latest_report.alert_metrics.alerts_triggered_today,
                "sms_sent_today": latest_report.alert_metrics.sms_sent_today,
                "sms_failed_today": latest_report.alert_metrics.sms_failed_today
            }
        }

# Global health monitor instance
health_monitor = HealthMonitor() 