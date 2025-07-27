"""
Custom exceptions for TouchLine application
"""

from fastapi import HTTPException, status
from typing import Optional, Dict, Any

class TouchLineException(Exception):
    """Base exception for TouchLine application"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class DatabaseException(TouchLineException):
    """Database-related exceptions"""
    pass

class SportsAPIException(TouchLineException):
    """Sports API-related exceptions"""
    pass

class SportsAPIError(SportsAPIException):
    """Sports API error with response details"""
    def __init__(self, message: str, api_response: Dict[str, Any] = None, operation: str = None, status_code: int = None):
        self.api_response = api_response or {}
        self.operation = operation
        self.status_code = status_code
        super().__init__(f"Sports API Error: {message}", "SPORTS_API_ERROR", {
            "api_response": self.api_response,
            "operation": operation,
            "status_code": status_code
        })

class SMSException(TouchLineException):
    """SMS service-related exceptions"""
    pass

class AlertException(TouchLineException):
    """Alert system-related exceptions"""
    pass

class AuthenticationException(TouchLineException):
    """Authentication-related exceptions"""
    pass

class ValidationException(TouchLineException):
    """Data validation exceptions"""
    pass

class ValidationError(ValidationException):
    """Validation error with field details"""
    def __init__(self, message: str, field_errors: Dict[str, str] = None, field: str = None, value: Any = None):
        self.field_errors = field_errors or {}
        self.field = field
        self.value = value
        super().__init__(f"Validation Error: {message}", "VALIDATION_ERROR", {
            "field_errors": self.field_errors,
            "field": field,
            "value": value
        })

class RateLimitException(TouchLineException):
    """Rate limiting exceptions"""
    pass

class CacheError(TouchLineException):
    """Cache-related exceptions"""
    pass

class HealthCheckException(TouchLineException):
    """Health check related exceptions"""
    pass

class NotificationException(TouchLineException):
    """Notification system exceptions"""
    pass

class AnalyticsException(TouchLineException):
    """Analytics system exceptions"""
    pass

class AlertEvaluationError(AlertException):
    """Alert evaluation error with context"""
    def __init__(self, message: str, alert_id: int = None, condition: str = None):
        self.alert_id = alert_id
        self.condition = condition
        super().__init__(f"Alert Evaluation Error: {message}", "ALERT_EVALUATION_ERROR", {
            "alert_id": alert_id,
            "condition": condition
        })

class PlayerDataError(TouchLineException):
    """Player data related errors"""
    def __init__(self, message: str, player_id: int = None, player_name: str = None):
        self.player_id = player_id
        self.player_name = player_name
        super().__init__(f"Player Data Error: {message}", "PLAYER_DATA_ERROR", {
            "player_id": player_id,
            "player_name": player_name
        })

class MatchDataError(TouchLineException):
    """Match data related errors"""
    def __init__(self, message: str, match_id: str = None, match_data: Dict[str, Any] = None):
        self.match_id = match_id
        self.match_data = match_data or {}
        super().__init__(message, "MATCH_DATA_ERROR", {
            "match_id": match_id,
            "match_data": self.match_data
        })

class WebSocketError(TouchLineException):
    """WebSocket related errors"""
    def __init__(self, message: str, connection_id: str = None, event_type: str = None):
        self.connection_id = connection_id
        self.event_type = event_type
        super().__init__(message, "WEBSOCKET_ERROR", {
            "connection_id": connection_id,
            "event_type": event_type
        })

class DatabaseError(DatabaseException):
    """Database error with context"""
    def __init__(self, message: str, operation: str = None, table: str = None):
        self.operation = operation
        self.table = table
        super().__init__(message, "DATABASE_ERROR", {
            "operation": operation,
            "table": table
        })

class ConfigurationError(TouchLineException):
    """Configuration related errors"""
    def __init__(self, message: str, config_key: str = None, config_value: Any = None):
        self.config_key = config_key
        self.config_value = config_value
        super().__init__(message, "CONFIGURATION_ERROR", {
            "config_key": config_key,
            "config_value": config_value
        })

class RateLimitError(RateLimitException):
    """Rate limit error with retry information"""
    def __init__(self, message: str, retry_after: int = None, endpoint: str = None):
        self.retry_after = retry_after
        self.endpoint = endpoint
        super().__init__(f"Rate Limit Error: {message}", "RATE_LIMIT_ERROR", {
            "retry_after": retry_after,
            "endpoint": endpoint
        })

def handle_touchline_exception(exc: TouchLineException) -> HTTPException:
    """Convert TouchLine exceptions to HTTP exceptions"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = exc.error_code or "INTERNAL_ERROR"
    
    # Map specific exceptions to appropriate HTTP status codes
    if isinstance(exc, AuthenticationException):
        status_code = status.HTTP_401_UNAUTHORIZED
        error_code = "AUTHENTICATION_ERROR"
    elif isinstance(exc, ValidationException):
        status_code = status.HTTP_400_BAD_REQUEST
        error_code = "VALIDATION_ERROR"
    elif isinstance(exc, RateLimitException):
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
        error_code = "RATE_LIMIT_EXCEEDED"
    elif isinstance(exc, DatabaseException):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_code = "DATABASE_ERROR"
    elif isinstance(exc, SportsAPIException):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        error_code = "SPORTS_API_ERROR"
    elif isinstance(exc, SMSException):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        error_code = "SMS_SERVICE_ERROR"
    elif isinstance(exc, AlertException):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_code = "ALERT_SYSTEM_ERROR"
    
    return HTTPException(
        status_code=status_code,
        detail={
            "error": error_code,
            "message": exc.message,
            "details": exc.details
        }
    )

# Predefined error messages
ERROR_MESSAGES = {
    "INVALID_CREDENTIALS": "Invalid email or password",
    "USER_NOT_FOUND": "User not found",
    "USER_ALREADY_EXISTS": "User with this email already exists",
    "INVALID_TOKEN": "Invalid or expired token",
    "INSUFFICIENT_PERMISSIONS": "Insufficient permissions",
    "MATCH_NOT_FOUND": "Match not found",
    "ALERT_NOT_FOUND": "Alert not found",
    "INVALID_ALERT_CONDITION": "Invalid alert condition",
    "SPORTS_API_UNAVAILABLE": "Sports API is currently unavailable",
    "SMS_SERVICE_UNAVAILABLE": "SMS service is currently unavailable",
    "RATE_LIMIT_EXCEEDED": "Rate limit exceeded. Please try again later",
    "DATABASE_CONNECTION_ERROR": "Database connection error",
    "INVALID_PHONE_NUMBER": "Invalid phone number format",
    "ALERT_ALREADY_EXISTS": "Alert with this configuration already exists",
    "INVALID_TIME_WINDOW": "Invalid time window specified",
    "PLAYER_NOT_FOUND": "Player not found",
    "INVALID_METRIC_TYPE": "Invalid metric type specified",
    "CONDITION_EVALUATION_ERROR": "Error evaluating alert condition",
    "WEBSOCKET_CONNECTION_ERROR": "WebSocket connection error"
} 