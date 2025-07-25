from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.routers import matches, alerts, system, websocket
from app.lifespan import lifespan
from app.core.config import settings

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="TouchLine API",
    description="Sports alert system API",
    version="1.0.0",
    lifespan=lifespan
)

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