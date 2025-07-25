from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Alert
from datetime import datetime
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

from pydantic import BaseModel
import json

class AlertCreate(BaseModel):
    name: str
    conditions: str  # JSON string with alert conditions

@router.post("/")
async def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new alert with advanced conditions"""
    try:
        # Parse the conditions JSON
        conditions = json.loads(alert_data.conditions)
        
        # Check if this is an advanced alert with multiple conditions
        if isinstance(conditions, dict) and 'conditions' in conditions:
            # Advanced alert with multiple conditions
            return await create_advanced_alert(alert_data, conditions, db, current_user.id)
        else:
            # Simple alert with single condition
            return await create_simple_alert(alert_data, conditions, db, current_user.id)
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid conditions format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating alert: {str(e)}")

async def create_simple_alert(alert_data: AlertCreate, conditions: dict, db: Session, user_id: int):
    """Create a simple alert with single condition"""
    # Extract basic info for the alert
    team = conditions.get('team', '')
    condition_type = conditions.get('condition_type', 'goals')
    operator = conditions.get('operator', '>=')
    value = conditions.get('value', 0)
    time_window = conditions.get('time_window')
    description = conditions.get('description', '')
    
    # Create a readable condition string
    condition_str = f"{team} {condition_type} {operator} {value}"
    if time_window:
        condition_str += f" (within {time_window} minutes)"
    
    alert = Alert(
        name=alert_data.name,
        team=team,
        alert_type=condition_type,
        threshold=float(value) if isinstance(value, (int, float)) else 0,
        condition=condition_str,
        time_window=int(time_window) if time_window else None,
        user_phone="",  # Will be added later
        is_active=True,
        created_at=datetime.utcnow(),
        user_id=user_id
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

async def create_advanced_alert(alert_data: AlertCreate, conditions: dict, db: Session, user_id: int):
    """Create an advanced alert with multiple conditions"""
    # Extract advanced alert info
    description = conditions.get('description', '')
    logic_operator = conditions.get('logic_operator', 'AND')
    condition_list = conditions.get('conditions', [])
    time_windows = conditions.get('time_windows', [])
    sequences = conditions.get('sequences', [])
    user_phone = conditions.get('user_phone', '')
    
    # Create a comprehensive condition string
    condition_parts = []
    
    # Add main conditions
    for i, cond in enumerate(condition_list):
        team = cond.get('team', 'any team')
        cond_type = cond.get('type', 'goals')
        operator = cond.get('operator', '>=')
        value = cond.get('value', 0)
        cond_desc = cond.get('description', '')
        
        condition_part = f"{team} {cond_type} {operator} {value}"
        if cond_desc:
            condition_part += f" ({cond_desc})"
        condition_parts.append(condition_part)
    
    # Add time windows
    for i, window in enumerate(time_windows):
        start = window.get('start_minute', 0)
        end = window.get('end_minute', 90)
        condition_parts.append(f"time window {start}-{end} minutes")
    
    # Add sequences
    for i, seq in enumerate(sequences):
        events = seq.get('events', [])
        time_limit = seq.get('time_limit', 0)
        if events:
            event_descs = [f"{e.get('type', 'event')} {e.get('operator', '>=')} {e.get('value', 0)}" for e in events]
            condition_parts.append(f"sequence: {' -> '.join(event_descs)} within {time_limit}s")
    
    # Combine with logic operator
    condition_str = f" {logic_operator} ".join(condition_parts)
    if description:
        condition_str = f"{description}: {condition_str}"
    
    # Store the full conditions as JSON for the alert engine
    full_conditions = {
        "description": description,
        "logic_operator": logic_operator,
        "conditions": condition_list,
        "time_windows": time_windows,
        "sequences": sequences,
        "user_phone": user_phone
    }
    
    alert = Alert(
        name=alert_data.name,
        team="",  # Will be determined by conditions
        alert_type="advanced",
        threshold=0,  # Not applicable for advanced alerts
        condition=json.dumps(full_conditions),  # Store full conditions as JSON
        time_window=None,  # Handled in conditions
        user_phone=user_phone,
        is_active=True,
        created_at=datetime.utcnow(),
        user_id=user_id
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    return {
        "id": alert.id,
        "name": alert.name,
        "team": "Multiple",  # Advanced alerts can involve multiple teams
        "alert_type": "advanced",
        "threshold": 0,
        "condition": condition_str,
        "is_active": alert.is_active,
        "created_at": alert.created_at.isoformat()
    }

@router.get("/")
async def get_all_alerts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all alerts"""
    try:
        alerts = db.query(Alert).filter(Alert.user_id == current_user.id).all()
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
async def toggle_alert(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Toggle alert active status"""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        if alert.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to toggle this alert")

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
async def delete_alert(
    alert_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Delete an alert"""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        if alert.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to delete this alert")

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
        advanced_alerts = db.query(Alert).filter(Alert.alert_type == "advanced").count()
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "inactive_alerts": total_alerts - active_alerts,
            "advanced_alerts": advanced_alerts,
            "simple_alerts": total_alerts - advanced_alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alert stats: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_alerts(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get alerts for a specific user"""
    try:
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to view this user's alerts")

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
                    "user_phone": alert.user_phone,
                    "is_active": alert.is_active,
                    "created_at": alert.created_at.isoformat()
                }
                for alert in alerts
            ],
            "count": len(alerts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user alerts: {str(e)}")

@router.get("/templates")
async def get_alert_templates():
    """Get predefined alert templates"""
    templates = [
        {
            "id": "high_scoring",
            "name": "High Scoring Matches",
            "description": "Alert when any team scores 3+ goals",
            "conditions": {
                "logic_operator": "OR",
                "conditions": [
                    {
                        "type": "goals",
                        "team": "home",
                        "operator": ">=",
                        "value": 3,
                        "description": "Home team scores 3+ goals"
                    },
                    {
                        "type": "goals",
                        "team": "away",
                        "operator": ">=",
                        "value": 3,
                        "description": "Away team scores 3+ goals"
                    }
                ]
            }
        },
        {
            "id": "close_matches",
            "name": "Close Matches",
            "description": "Alert when score difference is 1 goal or less",
            "conditions": {
                "logic_operator": "AND",
                "conditions": [
                    {
                        "type": "score_difference",
                        "team": "any",
                        "operator": "<=",
                        "value": 1,
                        "description": "Score difference ≤ 1 goal"
                    }
                ]
            }
        },
        {
            "id": "high_xg",
            "name": "High Expected Goals",
            "description": "Alert when expected goals (xG) is high",
            "conditions": {
                "logic_operator": "OR",
                "conditions": [
                    {
                        "type": "xg",
                        "team": "home",
                        "operator": ">=",
                        "value": 0.5,
                        "description": "Home team xG ≥ 0.5"
                    },
                    {
                        "type": "xg",
                        "team": "away",
                        "operator": ">=",
                        "value": 0.5,
                        "description": "Away team xG ≥ 0.5"
                    }
                ]
            }
        }
    ]
    return {"templates": templates} 