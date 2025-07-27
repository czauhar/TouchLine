"""
Custom exceptions for TouchLine application
"""

class TouchLineException(Exception):
    """Base exception for TouchLine application"""
    pass

class SportsAPIError(TouchLineException):
    """Raised when sports API encounters an error"""
    def __init__(self, message: str, status_code: int = None, api_response: dict = None):
        self.message = message
        self.status_code = status_code
        self.api_response = api_response
        super().__init__(self.message)

class AlertEvaluationError(TouchLineException):
    """Raised when alert evaluation fails"""
    def __init__(self, alert_id: int, message: str, condition_data: dict = None):
        self.alert_id = alert_id
        self.message = message
        self.condition_data = condition_data
        super().__init__(f"Alert {alert_id}: {message}")

class PlayerDataError(TouchLineException):
    """Raised when player data processing fails"""
    def __init__(self, player_id: int = None, player_name: str = None, message: str = ""):
        self.player_id = player_id
        self.player_name = player_name
        self.message = message
        identifier = f"Player {player_id}" if player_id else f"Player {player_name}" if player_name else "Unknown player"
        super().__init__(f"{identifier}: {message}")

class MatchDataError(TouchLineException):
    """Raised when match data processing fails"""
    def __init__(self, match_id: str = None, message: str = ""):
        self.match_id = match_id
        self.message = message
        identifier = f"Match {match_id}" if match_id else "Unknown match"
        super().__init__(f"{identifier}: {message}")

class WebSocketError(TouchLineException):
    """Raised when WebSocket operations fail"""
    def __init__(self, user_id: int = None, message: str = ""):
        self.user_id = user_id
        self.message = message
        identifier = f"User {user_id}" if user_id else "Unknown user"
        super().__init__(f"WebSocket error for {identifier}: {message}")

class DatabaseError(TouchLineException):
    """Raised when database operations fail"""
    def __init__(self, operation: str, table: str = None, message: str = ""):
        self.operation = operation
        self.table = table
        self.message = message
        identifier = f"{operation} on {table}" if table else operation
        super().__init__(f"Database error during {identifier}: {message}")

class ValidationError(TouchLineException):
    """Raised when data validation fails"""
    def __init__(self, field: str, value: any, message: str = ""):
        self.field = field
        self.value = value
        self.message = message
        super().__init__(f"Validation error for field '{field}' with value '{value}': {message}")

class ConfigurationError(TouchLineException):
    """Raised when configuration is invalid or missing"""
    def __init__(self, config_key: str, message: str = ""):
        self.config_key = config_key
        self.message = message
        super().__init__(f"Configuration error for '{config_key}': {message}")

class RateLimitError(TouchLineException):
    """Raised when API rate limit is exceeded"""
    def __init__(self, api_name: str, retry_after: int = None):
        self.api_name = api_name
        self.retry_after = retry_after
        message = f"Rate limit exceeded for {api_name}"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message)

class CacheError(TouchLineException):
    """Raised when cache operations fail"""
    def __init__(self, operation: str, key: str = None, message: str = ""):
        self.operation = operation
        self.key = key
        self.message = message
        identifier = f"{operation} for key '{key}'" if key else operation
        super().__init__(f"Cache error during {identifier}: {message}") 