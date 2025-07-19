from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import asyncio
from dotenv import load_dotenv
from app.database import create_tables
from app.alert_engine import match_monitor
from app.routers import matches, alerts, system

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 TouchLine Backend starting up...")
    # Create database tables
    create_tables()
    print("📊 Database tables created")
    
    # Start alert engine in background
    try:
        asyncio.create_task(match_monitor.start_monitoring())
        print("🚨 Alert engine started")
    except Exception as e:
        print(f"❌ Failed to start alert engine: {e}")
    
    yield
    
    # Shutdown
    print("🛑 TouchLine Backend shutting down...")
    match_monitor.stop_monitoring()

# Create FastAPI app
app = FastAPI(
    title="TouchLine API",
    description="Sports alert system API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(system.router)
app.include_router(matches.router)
app.include_router(alerts.router)

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    ) 