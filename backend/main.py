from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import time
from dotenv import load_dotenv
from app.routers import matches, alerts, system, websocket, analytics
from app.lifespan import lifespan
from app.core.config import settings
from app.core.exceptions import TouchLineException, handle_touchline_exception
from app.middleware.rate_limiter import rate_limit_middleware
from app.utils.logger import log_api_request, log_system_event

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="TouchLine API",
    description="Sports alert system API",
    version="1.0.0",
    lifespan=lifespan
)

# Global exception handler for TouchLine exceptions
@app.exception_handler(TouchLineException)
async def touchline_exception_handler(request: Request, exc: TouchLineException):
    """Handle TouchLine-specific exceptions"""
    return handle_touchline_exception(exc)

# Global exception handler for general exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    log_system_event("unhandled_exception", {
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
        "endpoint": request.url.path,
        "method": request.method
    })
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": {}
        }
    )

# Request timing middleware
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    """Middleware to log request timing"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate response time
    response_time = time.time() - start_time
    
    # Log API request
    user_id = getattr(request.state, 'user_id', None)
    log_api_request(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
        response_time=response_time,
        user_id=user_id
    )
    
    # Add timing header
    response.headers["X-Response-Time"] = f"{response_time:.3f}s"
    
    return response

# Rate limiting middleware
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    return await rate_limit_middleware(request, call_next)

# CORS middleware with dynamic origins
allowed_origins = settings.ALLOWED_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(system.router)
app.include_router(matches.router)
app.include_router(alerts.router)
app.include_router(websocket.router)
app.include_router(analytics.router)

if __name__ == "__main__":
    import uvicorn
    host = settings.HOST
    port = settings.PORT
    debug = settings.DEBUG
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    ) 