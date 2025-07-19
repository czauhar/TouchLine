from fastapi import Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import logging
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

def setup_middleware(app):
    """Setup all middleware for the FastAPI application"""
    
    # Add rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # Development
            "https://touchline.app",  # Production
            "https://www.touchline.app",  # Production with www
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Security headers middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Remove server information
        response.headers.pop("Server", None)
        
        return response
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        response = await call_next(request)
        
        # Log response time
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
        
        return response
    
    # Rate limiting for specific endpoints
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        # Apply stricter rate limiting to sensitive endpoints
        if request.url.path.startswith("/api/auth"):
            # 5 requests per minute for auth endpoints
            if limiter.is_rate_limited(request, "5/minute"):
                raise HTTPException(status_code=429, detail="Too many requests")
        
        elif request.url.path.startswith("/api/alerts"):
            # 10 requests per minute for alert endpoints
            if limiter.is_rate_limited(request, "10/minute"):
                raise HTTPException(status_code=429, detail="Too many requests")
        
        response = await call_next(request)
        return response

class SecurityMiddleware:
    """Additional security middleware"""
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate phone number format"""
        import re
        # Basic phone validation (adjust for your needs)
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Basic input sanitization"""
        import html
        return html.escape(text.strip())
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) 