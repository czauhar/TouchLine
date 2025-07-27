import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import os

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)

class TouchLineLogger:
    """Centralized logging system for TouchLine"""
    
    def __init__(self, name: str = "touchline"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        # Console handler with structured formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = StructuredFormatter()
        console_handler.setFormatter(console_formatter)
        
        # File handler for persistent logs
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_dir / "touchline.log")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = StructuredFormatter()
        file_handler.setFormatter(file_formatter)
        
        # Error file handler
        error_handler = logging.FileHandler(log_dir / "errors.log")
        error_handler.setLevel(logging.ERROR)
        error_formatter = StructuredFormatter()
        error_handler.setFormatter(error_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
    
    def _log_with_extra(self, level: int, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log with extra structured fields"""
        if extra_fields:
            record = self.logger.makeRecord(
                self.logger.name, level, "", 0, message, (), None
            )
            record.extra_fields = extra_fields
            self.logger.handle(record)
        else:
            self.logger.log(level, message)
    
    def info(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self._log_with_extra(logging.INFO, message, extra_fields)
    
    def debug(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self._log_with_extra(logging.DEBUG, message, extra_fields)
    
    def warning(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self._log_with_extra(logging.WARNING, message, extra_fields)
    
    def error(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log error message"""
        self._log_with_extra(logging.ERROR, message, extra_fields)
    
    def critical(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log critical message"""
        self._log_with_extra(logging.CRITICAL, message, extra_fields)
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, 
                       response_time: float, user_id: Optional[int] = None):
        """Log API request details"""
        extra_fields = {
            "type": "api_request",
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "response_time_ms": round(response_time * 1000, 2),
            "user_id": user_id
        }
        self.info(f"API Request: {method} {endpoint} - {status_code}", extra_fields)
    
    def log_alert_trigger(self, alert_id: int, alert_name: str, match_id: str, 
                         condition_met: str, sms_sent: bool):
        """Log alert trigger events"""
        extra_fields = {
            "type": "alert_trigger",
            "alert_id": alert_id,
            "alert_name": alert_name,
            "match_id": match_id,
            "condition_met": condition_met,
            "sms_sent": sms_sent
        }
        self.info(f"Alert Triggered: {alert_name} for match {match_id}", extra_fields)
    
    def log_sports_api_call(self, endpoint: str, success: bool, response_time: float, 
                           error_message: Optional[str] = None):
        """Log sports API calls"""
        extra_fields = {
            "type": "sports_api_call",
            "endpoint": endpoint,
            "success": success,
            "response_time_ms": round(response_time * 1000, 2),
            "error_message": error_message
        }
        level = logging.INFO if success else logging.ERROR
        message = f"Sports API: {endpoint} - {'Success' if success else 'Failed'}"
        self._log_with_extra(level, message, extra_fields)
    
    def log_sms_send(self, phone_number: str, success: bool, message_id: Optional[str] = None,
                    error_message: Optional[str] = None):
        """Log SMS sending attempts"""
        extra_fields = {
            "type": "sms_send",
            "phone_number": phone_number,
            "success": success,
            "message_id": message_id,
            "error_message": error_message
        }
        level = logging.INFO if success else logging.ERROR
        message = f"SMS Send: {phone_number} - {'Success' if success else 'Failed'}"
        self._log_with_extra(level, message, extra_fields)
    
    def log_database_operation(self, operation: str, table: str, success: bool,
                             execution_time: float, error_message: Optional[str] = None):
        """Log database operations"""
        extra_fields = {
            "type": "database_operation",
            "operation": operation,
            "table": table,
            "success": success,
            "execution_time_ms": round(execution_time * 1000, 2),
            "error_message": error_message
        }
        level = logging.INFO if success else logging.ERROR
        message = f"Database: {operation} on {table} - {'Success' if success else 'Failed'}"
        self._log_with_extra(level, message, extra_fields)
    
    def log_user_action(self, user_id: int, action: str, details: Optional[Dict[str, Any]] = None):
        """Log user actions"""
        extra_fields = {
            "type": "user_action",
            "user_id": user_id,
            "action": action,
            "details": details or {}
        }
        self.info(f"User Action: {action} by user {user_id}", extra_fields)
    
    def log_system_event(self, event: str, details: Optional[Dict[str, Any]] = None):
        """Log system events"""
        extra_fields = {
            "type": "system_event",
            "event": event,
            "details": details or {}
        }
        self.info(f"System Event: {event}", extra_fields)
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "ms"):
        """Log performance metrics"""
        extra_fields = {
            "type": "performance_metric",
            "metric_name": metric_name,
            "value": value,
            "unit": unit
        }
        self.info(f"Performance: {metric_name} = {value}{unit}", extra_fields)

# Global logger instance
logger = TouchLineLogger()

# Convenience functions for common logging patterns
def log_api_request(method: str, endpoint: str, status_code: int, 
                   response_time: float, user_id: Optional[int] = None):
    """Log API request details"""
    logger.log_api_request(method, endpoint, status_code, response_time, user_id)

def log_alert_trigger(alert_id: int, alert_name: str, match_id: str, 
                     condition_met: str, sms_sent: bool):
    """Log alert trigger events"""
    logger.log_alert_trigger(alert_id, alert_name, match_id, condition_met, sms_sent)

def log_sports_api_call(endpoint: str, success: bool, response_time: float, 
                       error_message: Optional[str] = None):
    """Log sports API calls"""
    logger.log_sports_api_call(endpoint, success, response_time, error_message)

def log_sms_send(phone_number: str, success: bool, message_id: Optional[str] = None,
                error_message: Optional[str] = None):
    """Log SMS sending attempts"""
    logger.log_sms_send(phone_number, success, message_id, error_message)

def log_database_operation(operation: str, table: str, success: bool,
                         execution_time: float, error_message: Optional[str] = None):
    """Log database operations"""
    logger.log_database_operation(operation, table, success, execution_time, error_message)

def log_user_action(user_id: int, action: str, details: Optional[Dict[str, Any]] = None):
    """Log user actions"""
    logger.log_user_action(user_id, action, details)

def log_system_event(event: str, details: Optional[Dict[str, Any]] = None):
    """Log system events"""
    logger.log_system_event(event, details)

def log_performance_metric(metric_name: str, value: float, unit: str = "ms"):
    """Log performance metrics"""
    logger.log_performance_metric(metric_name, value, unit) 