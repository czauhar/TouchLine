from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Alert
from datetime import datetime

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.post("/")
async def create_alert(
    name: str,
    team: str,
    alert_type: str,
    threshold: float,
    description: str = "",
    user_phone: str = "",
    db: Session = Depends(get_db)
):
    """Create a new alert"""
    try:
        alert = Alert(
            name=name,
            team=team,
            alert_type=alert_type,
            threshold=threshold,
            condition=f"{team} {alert_type} >= {threshold}",
            user_phone=user_phone,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        return {
            "id": alert.id,
            "name": alert.name,
            "team": alert.team,
            "alert_type": alert.alert_type,
            "threshold": alert.threshold,
            "condition": alert.condition,
            "is_active": alert.is_active,
            "created_at": alert.created_at.isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating alert: {str(e)}")

@router.get("/")
async def get_all_alerts(db: Session = Depends(get_db)):
    """Get all alerts"""
    try:
        alerts = db.query(Alert).all()
        return {
            "alerts": [
                {
                    "id": alert.id,
                    "name": alert.name,
                    "team": alert.team,
                    "alert_type": alert.alert_type,
                    "threshold": alert.threshold,
                    "condition": alert.condition,
                    "user_phone": alert.user_phone,
                    "is_active": alert.is_active,
                    "created_at": alert.created_at.isoformat()
                }
                for alert in alerts
            ],
            "count": len(alerts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")

@router.put("/{alert_id}/toggle")
async def toggle_alert(alert_id: int, db: Session = Depends(get_db)):
    """Toggle alert active status"""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.is_active = not alert.is_active
        db.commit()
        
        return {
            "id": alert.id,
            "is_active": alert.is_active,
            "message": f"Alert {'activated' if alert.is_active else 'deactivated'}"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error toggling alert: {str(e)}")

@router.delete("/{alert_id}")
async def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete an alert"""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        db.delete(alert)
        db.commit()
        
        return {"message": "Alert deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting alert: {str(e)}")

@router.get("/stats")
async def get_alert_stats(db: Session = Depends(get_db)):
    """Get alert statistics"""
    try:
        total_alerts = db.query(Alert).count()
        active_alerts = db.query(Alert).filter(Alert.is_active == True).count()
        inactive_alerts = total_alerts - active_alerts
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "inactive_alerts": inactive_alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alert stats: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_alerts(user_id: int, db: Session = Depends(get_db)):
    """Get alerts for a specific user"""
    try:
        alerts = db.query(Alert).filter(Alert.user_id == user_id).all()
        return {
            "alerts": [
                {
                    "id": alert.id,
                    "name": alert.name,
                    "team": alert.team,
                    "alert_type": alert.alert_type,
                    "threshold": alert.threshold,
                    "condition": alert.condition,
                    "is_active": alert.is_active,
                    "created_at": alert.created_at.isoformat()
                }
                for alert in alerts
            ],
            "count": len(alerts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user alerts: {str(e)}") 