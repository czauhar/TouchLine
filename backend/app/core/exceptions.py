from fastapi import HTTPException
from typing import Any, Dict, Optional

class TouchLineException(Exception):
    """Base exception for TouchLine application"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class AlertException(TouchLineException):
    """Exception for alert-related errors"""
    pass

class SMSException(TouchLineException):
    """Exception for SMS-related errors"""
    pass

class SportsAPIException(TouchLineException):
    """Exception for sports API errors"""
    pass

class DatabaseException(TouchLineException):
    """Exception for database errors"""
    pass

def handle_touchline_exception(exc: TouchLineException) -> HTTPException:
    """Convert TouchLine exceptions to HTTP exceptions"""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "error": exc.message,
            "details": exc.details
        }
    ) 