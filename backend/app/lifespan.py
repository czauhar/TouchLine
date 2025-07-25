from contextlib import asynccontextmanager
import asyncio
from app.database import create_tables
from app.alert_engine import match_monitor
from app.background_tasks import background_task_manager

@asynccontextmanager
async def lifespan(app):
    # Startup
    print("🚀 TouchLine Backend starting up...")
    # Create database tables
    create_tables()
    print("📊 Database tables created")
    
    # Start background tasks
    try:
        await background_task_manager.start_background_tasks()
        print("🔄 Background tasks started")
    except Exception as e:
        print(f"❌ Failed to start background tasks: {e}")
    
    # Start alert engine in background
    try:
        asyncio.create_task(match_monitor.start_monitoring())
        print("🚨 Alert engine started")
    except Exception as e:
        print(f"❌ Failed to start alert engine: {e}")
    
    yield
    
    # Shutdown
    print("🛑 TouchLine Backend shutting down...")
    await background_task_manager.stop_background_tasks()
    await match_monitor.stop_monitoring() 