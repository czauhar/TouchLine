from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database import engine, create_tables, get_db
from app.models import Base
from app.sports_api import sports_api
from app.services import MatchService, AlertService, UserService
from app.sms_service import sms_service
from app.alert_engine import alert_engine

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 TouchLine Backend starting up...")
    # Create database tables
    create_tables()
    print("📊 Database tables created")
    yield
    # Shutdown
    print("🛑 TouchLine Backend shutting down...")

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

@app.get("/")
async def root():
    return {"message": "TouchLine API is running! 🏈"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "TouchLine Backend"}

@app.get("/api/status")
async def api_status():
    return {
        "backend": "running",
        "database": "configured",
        "sms_service": "configured" if sms_service.is_configured else "not_configured",
        "sports_api": "configured" if sports_api.api_key else "not_configured",
        "alert_engine": "running" if alert_engine.is_running else "stopped"
    }

# Sports API endpoints
@app.get("/api/matches/live")
async def get_live_matches():
    """Get currently live matches"""
    matches = await sports_api.get_live_matches()
    formatted_matches = [sports_api.format_match_data(match) for match in matches]
    return {"matches": formatted_matches, "count": len(formatted_matches)}

@app.get("/api/matches/today")
async def get_todays_matches():
    """Get today's matches"""
    matches = await sports_api.get_todays_matches()
    formatted_matches = [sports_api.format_match_data(match) for match in matches]
    return {"matches": formatted_matches, "count": len(formatted_matches)}

@app.get("/api/matches/{fixture_id}/statistics")
async def get_match_statistics(fixture_id: int):
    """Get detailed statistics for a specific match"""
    stats = await sports_api.get_match_statistics(fixture_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Match statistics not found")
    return {"statistics": stats}

@app.get("/api/leagues/{league_id}/matches")
async def get_league_matches(league_id: int, season: int = 2024):
    """Get matches for a specific league and season"""
    matches = await sports_api.get_league_matches(league_id, season)
    formatted_matches = [sports_api.format_match_data(match) for match in matches]
    return {"matches": formatted_matches, "count": len(formatted_matches)}

# Database endpoints
@app.get("/api/db/matches/live")
async def get_db_live_matches():
    """Get live matches from database"""
    try:
        db = next(get_db())
        matches = MatchService.get_live_matches(db)
        return {
            "matches": [
                {
                    "id": match.id,
                    "external_id": match.external_id,
                    "home_team": match.home_team,
                    "away_team": match.away_team,
                    "league": match.league,
                    "start_time": match.start_time.isoformat(),
                    "status": match.status,
                    "home_score": match.home_score,
                    "away_score": match.away_score
                }
                for match in matches
            ],
            "count": len(matches)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/db/matches/today")
async def get_db_todays_matches():
    """Get today's matches from database"""
    try:
        db = next(get_db())
        matches = MatchService.get_todays_matches(db)
        return {
            "matches": [
                {
                    "id": match.id,
                    "external_id": match.external_id,
                    "home_team": match.home_team,
                    "away_team": match.away_team,
                    "league": match.league,
                    "start_time": match.start_time.isoformat(),
                    "status": match.status,
                    "home_score": match.home_score,
                    "away_score": match.away_score
                }
                for match in matches
            ],
            "count": len(matches)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/db/matches/sync")
async def sync_matches():
    """Sync live matches from sports API to database"""
    try:
        db = next(get_db())
        synced_matches = await MatchService.sync_live_matches(db)
        return {
            "message": f"Successfully synced {len(synced_matches)} matches",
            "synced_count": len(synced_matches)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing matches: {str(e)}")

# Alert endpoints
@app.post("/api/alerts")
async def create_alert(
    user_id: int,
    name: str,
    alert_type: str,
    threshold: float,
    condition: str,
    team_filter: str = None,
    league_filter: str = None,
    db: Session = Depends(get_db)
):
    """Create a new alert"""
    try:
        alert = AlertService.create_alert(
            db=db,
            user_id=user_id,
            name=name,
            alert_type=alert_type,
            threshold=threshold,
            condition=condition,
            team_filter=team_filter,
            league_filter=league_filter
        )
        return {
            "id": alert.id,
            "name": alert.name,
            "alert_type": alert.alert_type,
            "threshold": alert.threshold,
            "condition": alert.condition,
            "team_filter": alert.team_filter,
            "league_filter": alert.league_filter,
            "is_active": alert.is_active
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating alert: {str(e)}")

@app.get("/api/alerts/user/{user_id}")
async def get_user_alerts(user_id: int, db: Session = Depends(get_db)):
    """Get all alerts for a user"""
    alerts = AlertService.get_user_alerts(db, user_id)
    return {
        "alerts": [
            {
                "id": alert.id,
                "name": alert.name,
                "alert_type": alert.alert_type,
                "threshold": alert.threshold,
                "condition": alert.condition,
                "team_filter": alert.team_filter,
                "league_filter": alert.league_filter,
                "is_active": alert.is_active
            }
            for alert in alerts
        ],
        "count": len(alerts)
    }

# SMS and Alert Engine endpoints
@app.post("/api/sms/test")
async def test_sms(to_number: str, message: str = "TouchLine SMS test"):
    """Test SMS sending"""
    result = sms_service.send_alert(to_number, message)
    return result

@app.post("/api/alert-engine/start")
async def start_alert_engine():
    """Start the alert monitoring engine"""
    if not alert_engine.is_running:
        # Start in background
        asyncio.create_task(alert_engine.start_monitoring())
        return {"message": "Alert engine started", "status": "running"}
    else:
        return {"message": "Alert engine already running", "status": "running"}

@app.post("/api/alert-engine/stop")
async def stop_alert_engine():
    """Stop the alert monitoring engine"""
    alert_engine.stop_monitoring()
    return {"message": "Alert engine stopped", "status": "stopped"}

@app.get("/api/alert-engine/status")
async def get_alert_engine_status():
    """Get alert engine status"""
    return {
        "is_running": alert_engine.is_running,
        "check_interval": alert_engine.check_interval
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 