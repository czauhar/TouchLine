from fastapi import APIRouter, HTTPException, Depends, status, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import RegisterRequest, UserUpdate, UserBase
from app.auth import AuthService, get_current_user
from app.services import UserService
from app.sms_service import sms_service
from app.sports_api import sports_api
from app.alert_engine import match_monitor
from app.services.health_monitor import health_monitor
from app.utils.logger import log_user_action
import os
from pydantic import BaseModel, EmailStr

router = APIRouter(tags=["system"])

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    phone_number: str = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.get("/")
async def root():
    return {"message": "TouchLine API is running! 🏈"}

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "service": "TouchLine Backend"}

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with comprehensive metrics"""
    try:
        # Generate a new health report
        health_report = await health_monitor.generate_health_report()
        # Return the summary
        return health_monitor.get_health_summary()
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": None
        }

@router.get("/health/history")
async def health_history(hours: int = 24):
    """Get health history for the specified time period"""
    try:
        history = health_monitor.get_health_history(hours)
        return {
            "history": [
                {
                    "timestamp": report.timestamp.isoformat(),
                    "status": report.overall_status.value,
                    "system": {
                        "cpu_percent": report.system_metrics.cpu_percent,
                        "memory_percent": report.system_metrics.memory_percent,
                        "disk_percent": report.system_metrics.disk_percent
                    },
                    "database": {
                        "connection_status": report.database_metrics.connection_status,
                        "response_time_ms": round(report.database_metrics.response_time * 1000, 2)
                    },
                    "api": {
                        "sports_api_status": report.api_metrics.sports_api_status,
                        "sms_service_status": report.api_metrics.sms_service_status,
                        "error_count": report.api_metrics.error_count
                    }
                }
                for report in history
            ],
            "hours": hours
        }
    except Exception as e:
        return {"error": str(e), "history": []}

@router.get("/api/status")
async def api_status():
    return {
        "backend": "running",
        "database": "configured",
        "sms_service": "configured" if sms_service.is_configured else "not_configured",
        "sports_api": "configured" if sports_api.api_key else "not_configured",
        "alert_engine": "running" if match_monitor.running else "stopped"
    }

@router.post("/api/sms/test")
async def test_sms(to_number: str, message: str = "TouchLine SMS test"):
    """Test SMS functionality"""
    try:
        result = sms_service.send_sms(to_number, message)
        return {"success": True, "message": "SMS sent successfully", "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/api/alert-engine/start")
async def start_alert_engine():
    """Start the alert engine"""
    try:
        await match_monitor.start_monitoring()
        return {"message": "Alert engine started successfully"}
    except Exception as e:
        return {"error": f"Failed to start alert engine: {str(e)}"}

@router.post("/api/alert-engine/stop")
async def stop_alert_engine():
    """Stop the alert engine"""
    try:
        match_monitor.stop_monitoring()
        return {"message": "Alert engine stopped successfully"}
    except Exception as e:
        return {"error": f"Failed to stop alert engine: {str(e)}"}

@router.get("/api/alert-engine/status")
async def get_alert_engine_status():
    """Get alert engine status"""
    return {
        "running": match_monitor.running,
        "status": "running" if match_monitor.running else "stopped"
    }

@router.post("/api/auth/register")
async def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    # Check for existing user
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = AuthService.get_password_hash(data.password)
    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hashed_password,
        phone_number=data.phone_number,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # Create JWT
    token = AuthService.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "user": {"id": user.id, "email": user.email, "username": user.username, "phone_number": user.phone_number}}

@router.post("/api/auth/login")
def login_user(
    data: LoginRequest = Body(...),
    db: Session = Depends(get_db)
):
    user = AuthService.authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = AuthService.create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "phone_number": user.phone_number
        }
    }

@router.get("/api/user/me", response_model=UserBase)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    return current_user

@router.patch("/api/user/me", response_model=UserBase)
def update_my_profile(
    update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user's profile"""
    user = UserService.get_user_by_id(db, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if update.email:
        user.email = update.email
    if update.username:
        user.username = update.username
    if update.phone_number:
        user.phone_number = update.phone_number
    if update.full_name:
        user.full_name = update.full_name
    if update.preferences:
        user.preferences = update.preferences
    if update.password:
        user.hashed_password = AuthService.get_password_hash(update.password)
    db.commit()
    db.refresh(user)
    return user 