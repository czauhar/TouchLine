from contextlib import asynccontextmanager
import asyncio
from app.database import create_tables
from app.alert_engine import match_monitor

@asynccontextmanager
async def lifespan(app):
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