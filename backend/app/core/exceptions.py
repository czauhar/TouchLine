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

class RateLimitException(TouchLineException):
    """Rate limiting exceptions"""
    pass

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