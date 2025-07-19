from fastapi import APIRouter
from app.sms_service import sms_service
from app.sports_api import sports_api
from app.alert_engine import match_monitor

router = APIRouter(tags=["system"])

@router.get("/")
async def root():
    return {"message": "TouchLine API is running! 🏈"}

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "TouchLine Backend"}

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