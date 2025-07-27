import time
import asyncio
from typing import Dict, Optional, Callable
from collections import defaultdict
from dataclasses import dataclass
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import json

from ..core.exceptions import RateLimitException
from ..utils.logger import log_user_action

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_minute: int
    requests_per_hour: int
    burst_limit: int = 10
    window_size: int = 60  # seconds

class RateLimiter:
    """Rate limiting system with multiple strategies"""
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.burst_requests: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()
        
        # Rate limit configurations for different endpoints
        self.endpoint_configs = {
            # Authentication endpoints - stricter limits
            "/api/auth/login": RateLimitConfig(5, 20, 3),
            "/api/auth/register": RateLimitConfig(3, 10, 2),
            "/api/auth/refresh": RateLimitConfig(10, 50, 5),
            
            # API endpoints - moderate limits
            "/api/matches/live": RateLimitConfig(30, 300, 20),
            "/api/matches/today": RateLimitConfig(30, 300, 20),
            "/api/alerts": RateLimitConfig(60, 600, 30),
            "/api/alerts/templates": RateLimitConfig(30, 300, 20),
            
            # User management - moderate limits
            "/api/user/me": RateLimitConfig(60, 600, 30),
            "/api/user/me/password": RateLimitConfig(5, 20, 3),
            
            # System endpoints - higher limits
            "/health": RateLimitConfig(120, 1200, 60),
            "/docs": RateLimitConfig(60, 600, 30),
            
            # Default configuration
            "default": RateLimitConfig(60, 600, 30)
        }
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for the client"""
        # Try to get user ID from JWT token first
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        
        return f"ip:{request.client.host}"
    
    def _get_endpoint_config(self, path: str) -> RateLimitConfig:
        """Get rate limit configuration for an endpoint"""
        # Check exact match first
        if path in self.endpoint_configs:
            return self.endpoint_configs[path]
        
        # Check prefix matches
        for endpoint, config in self.endpoint_configs.items():
            if endpoint != "default" and path.startswith(endpoint):
                return config
        
        # Return default configuration
        return self.endpoint_configs["default"]
    
    async def _cleanup_old_requests(self, client_id: str, window_size: int):
        """Remove old requests outside the time window"""
        current_time = time.time()
        
        # Clean up regular requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if current_time - req_time < window_size
        ]
        
        # Clean up burst requests (shorter window)
        burst_window = min(window_size // 6, 10)  # 10 seconds or window_size/6
        self.burst_requests[client_id] = [
            req_time for req_time in self.burst_requests[client_id]
            if current_time - req_time < burst_window
        ]
    
    async def _check_rate_limit(self, client_id: str, config: RateLimitConfig) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        
        # Clean up old requests
        await self._cleanup_old_requests(client_id, config.window_size)
        
        # Check burst limit (short-term)
        burst_count = len(self.burst_requests[client_id])
        if burst_count >= config.burst_limit:
            return False
        
        # Check per-minute limit
        minute_ago = current_time - 60
        minute_requests = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        if len(minute_requests) >= config.requests_per_minute:
            return False
        
        # Check per-hour limit
        hour_ago = current_time - 3600
        hour_requests = [
            req_time for req_time in self.requests[client_id]
            if req_time > hour_ago
        ]
        if len(hour_requests) >= config.requests_per_hour:
            return False
        
        return True
    
    async def _record_request(self, client_id: str):
        """Record a new request"""
        current_time = time.time()
        self.requests[client_id].append(current_time)
        self.burst_requests[client_id].append(current_time)
    
    async def _get_retry_after(self, client_id: str, config: RateLimitConfig) -> int:
        """Calculate retry-after time in seconds"""
        current_time = time.time()
        
        # Check which limit was exceeded
        minute_ago = current_time - 60
        minute_requests = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        if len(minute_requests) >= config.requests_per_minute:
            # Return time until oldest request in the minute window expires
            oldest_request = min(minute_requests)
            return int(60 - (current_time - oldest_request)) + 1
        
        # Check burst limit
        burst_window = min(config.window_size // 6, 10)
        burst_ago = current_time - burst_window
        burst_requests = [
            req_time for req_time in self.burst_requests[client_id]
            if req_time > burst_ago
        ]
        
        if len(burst_requests) >= config.burst_limit:
            oldest_burst = min(burst_requests)
            return int(burst_window - (current_time - oldest_burst)) + 1
        
        # Hour limit
        hour_ago = current_time - 3600
        hour_requests = [
            req_time for req_time in self.requests[client_id]
            if req_time > hour_ago
        ]
        
        if len(hour_requests) >= config.requests_per_hour:
            oldest_hour = min(hour_requests)
            return int(3600 - (current_time - oldest_hour)) + 1
        
        return 60  # Default fallback
    
    async def check_rate_limit(self, request: Request) -> bool:
        """Main rate limiting check"""
        async with self.lock:
            client_id = self._get_client_identifier(request)
            config = self._get_endpoint_config(request.url.path)
            
            # Check if request is allowed
            allowed = await self._check_rate_limit(client_id, config)
            
            if allowed:
                await self._record_request(client_id)
                return True
            
            # Rate limit exceeded
            retry_after = await self._get_retry_after(client_id, config)
            
            # Log the rate limit violation
            user_id = getattr(request.state, 'user_id', None)
            log_user_action(
                user_id or 0,
                "rate_limit_exceeded",
                {
                    "client_id": client_id,
                    "endpoint": request.url.path,
                    "method": request.method,
                    "retry_after": retry_after,
                    "user_agent": request.headers.get("User-Agent", "")
                }
            )
            
            # Raise rate limit exception
            raise RateLimitException(
                message=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                error_code="RATE_LIMIT_EXCEEDED",
                details={
                    "retry_after": retry_after,
                    "endpoint": request.url.path,
                    "limits": {
                        "requests_per_minute": config.requests_per_minute,
                        "requests_per_hour": config.requests_per_hour,
                        "burst_limit": config.burst_limit
                    }
                }
            )
    
    def get_rate_limit_headers(self, request: Request) -> Dict[str, str]:
        """Get rate limit headers for response"""
        client_id = self._get_client_identifier(request)
        config = self._get_endpoint_config(request.url.path)
        
        # Calculate current usage
        current_time = time.time()
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        
        minute_requests = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        hour_requests = [
            req_time for req_time in self.requests[client_id]
            if req_time > hour_ago
        ]
        
        return {
            "X-RateLimit-Limit-Minute": str(config.requests_per_minute),
            "X-RateLimit-Limit-Hour": str(config.requests_per_hour),
            "X-RateLimit-Remaining-Minute": str(max(0, config.requests_per_minute - len(minute_requests))),
            "X-RateLimit-Remaining-Hour": str(max(0, config.requests_per_hour - len(hour_requests))),
            "X-RateLimit-Reset-Minute": str(int(minute_ago + 60)),
            "X-RateLimit-Reset-Hour": str(int(hour_ago + 3600))
        }

# Global rate limiter instance
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """FastAPI middleware for rate limiting"""
    try:
        # Skip rate limiting for certain paths
        skip_paths = ["/docs", "/openapi.json", "/favicon.ico"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            response = await call_next(request)
            return response
        
        # Check rate limit
        await rate_limiter.check_rate_limit(request)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        headers = rate_limiter.get_rate_limit_headers(request)
        for key, value in headers.items():
            response.headers[key] = value
        
        return response
        
    except RateLimitException as e:
        # Return rate limit error response
        retry_after = e.details.get("retry_after", 60)
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": e.message,
                "retry_after": retry_after,
                "details": e.details
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Reset": str(int(time.time() + retry_after))
            }
        )
    except Exception as e:
        # Log unexpected errors but don't block the request
        from ..utils.logger import logger
        logger.error(f"Rate limiting error: {e}")
        return await call_next(request)

# Convenience function for manual rate limiting
async def check_rate_limit(request: Request) -> bool:
    """Manual rate limit check for specific endpoints"""
    return await rate_limiter.check_rate_limit(request) 