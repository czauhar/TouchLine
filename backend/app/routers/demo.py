from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Match, Alert, User
from typing import List

router = APIRouter(prefix="/api/demo", tags=["demo"])

@router.get("/matches")
async def get_demo_matches(db: Session = Depends(get_db)):
    """Get demo matches from database"""
    matches = db.query(Match).all()
    
    return {
        "matches": [
            {
                "id": match.id,
                "external_id": match.external_id,
                "home_team": match.home_team,
                "away_team": match.away_team,
                "league": match.league,
                "start_time": match.start_time.isoformat() if match.start_time else None,
                "status": match.status,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "created_at": match.created_at.isoformat() if match.created_at else None
            }
            for match in matches
        ],
        "count": len(matches)
    }

@router.get("/alerts")
async def get_demo_alerts(db: Session = Depends(get_db)):
    """Get demo alerts from database"""
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
                "time_window": alert.time_window,
                "user_phone": alert.user_phone,
                "is_active": alert.is_active,
                "user_id": alert.user_id,
                "created_at": alert.created_at.isoformat() if alert.created_at else None
            }
            for alert in alerts
        ],
        "count": len(alerts)
    }

@router.post("/matches/{match_id}/update-score")
async def update_match_score(
    match_id: int,
    home_score: int,
    away_score: int,
    db: Session = Depends(get_db)
):
    """Update match score for testing alerts"""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        return {"error": "Match not found"}
    
    match.home_score = home_score
    match.away_score = away_score
    match.status = "live" if match.status == "scheduled" else match.status
    
    db.commit()
    
    return {
        "success": True,
        "match": {
            "id": match.id,
            "home_team": match.home_team,
            "away_team": match.away_team,
            "home_score": match.home_score,
            "away_score": match.away_score,
            "status": match.status
        }
    }

@router.post("/trigger-alerts")
async def trigger_alerts(db: Session = Depends(get_db)):
    """Manually trigger alert checking for all matches"""
    from app.models import AlertHistory
    from app.sms_service import sms_service
    from datetime import datetime
    
    triggered_alerts = []
    
    # Get all active alerts
    alerts = db.query(Alert).filter(Alert.is_active == True).all()
    
    # Get all matches
    matches = db.query(Match).all()
    
    for match in matches:
        for alert in alerts:
            # Check if alert applies to this match
            if alert.team not in [match.home_team, match.away_team]:
                continue
            
            # Check if alert condition is met
            triggered = False
            alert_message = ""
            
            if alert.alert_type == "goals":
                if alert.team == match.home_team:
                    team_score = match.home_score
                else:
                    team_score = match.away_score
                
                if team_score >= alert.threshold:
                    triggered = True
                    alert_message = f"🚨 ALERT: {alert.team} has scored {team_score} goals (threshold: {alert.threshold})"
            
            elif alert.alert_type == "possession":
                # For demo purposes, simulate possession data
                if alert.team == match.home_team:
                    possession = 65  # Simulate high possession
                else:
                    possession = 35
                
                if possession >= alert.threshold:
                    triggered = True
                    alert_message = f"🚨 ALERT: {alert.team} has {possession}% possession (threshold: {alert.threshold}%)"
            
            if triggered:
                # Create alert history record
                alert_history = AlertHistory(
                    alert_id=alert.id,
                    match_id=str(match.id),
                    triggered_at=datetime.utcnow(),
                    trigger_message=alert_message,
                    match_data=str({
                        "home_team": match.home_team,
                        "away_team": match.away_team,
                        "home_score": match.home_score,
                        "away_score": match.away_score,
                        "status": match.status
                    })
                )
                db.add(alert_history)
                
                # Send SMS if phone number is provided and valid
                sms_sent = False
                if alert.user_phone and alert.user_phone != "+1234567890":
                    try:
                        sms_result = sms_service.send_sms(
                            to_number=alert.user_phone,
                            message=alert_message
                        )
                        sms_sent = sms_result
                        print(f"SMS sent successfully: {sms_result}")
                    except Exception as e:
                        print(f"SMS failed: {e}")
                        sms_sent = False
                
                triggered_alerts.append({
                    "alert_id": alert.id,
                    "alert_name": alert.name,
                    "team": alert.team,
                    "message": alert_message,
                    "match": f"{match.home_team} vs {match.away_team}",
                    "sms_sent": sms_sent
                })
    
    # Commit all changes
    db.commit()
    
    return {
        "success": True,
        "triggered_count": len(triggered_alerts),
        "triggered_alerts": triggered_alerts
    }
