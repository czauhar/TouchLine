from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import User, Alert
from ..auth import get_current_user
from ..services.analytics_service import analytics_service
from ..services.notification_service import notification_service
from ..utils.logger import log_user_action

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/alert/{alert_id}/performance")
async def get_alert_performance(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed performance analytics for a specific alert"""
    try:
        # Verify user owns this alert
        alert = db.query(Alert).filter(
            Alert.id == alert_id,
            Alert.user_id == current_user.id
        ).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        performance = await analytics_service.get_alert_performance(alert_id)
        if not performance:
            raise HTTPException(status_code=404, detail="Alert performance data not found")
        
        log_user_action(current_user.id, "viewed_alert_performance", {"alert_id": alert_id})
        
        return {
            "alert_id": performance.alert_id,
            "alert_name": performance.alert_name,
            "total_triggers": performance.total_triggers,
            "success_rate": performance.success_rate,
            "avg_response_time": performance.avg_response_time,
            "last_triggered": performance.last_triggered.isoformat() if performance.last_triggered else None,
            "most_common_matches": performance.most_common_matches,
            "trigger_trend": performance.trigger_trend
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving alert performance: {str(e)}")

@router.get("/user/profile")
async def get_user_analytics(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive analytics for the current user"""
    try:
        analytics = await analytics_service.get_user_analytics(current_user.id)
        if not analytics:
            raise HTTPException(status_code=404, detail="User analytics not found")
        
        log_user_action(current_user.id, "viewed_user_analytics", {})
        
        return {
            "user_id": analytics.user_id,
            "username": analytics.username,
            "total_alerts": analytics.total_alerts,
            "active_alerts": analytics.active_alerts,
            "total_triggers": analytics.total_triggers,
            "avg_alerts_per_day": analytics.avg_alerts_per_day,
            "most_used_alert_types": analytics.most_used_alert_types,
            "activity_trend": analytics.activity_trend
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user analytics: {str(e)}")

@router.get("/system/overview")
async def get_system_analytics(
    current_user: User = Depends(get_current_user)
):
    """Get system-wide analytics (admin only)"""
    try:
        # Check if user is admin (you can implement admin role checking)
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        analytics = await analytics_service.get_system_analytics()
        if not analytics:
            raise HTTPException(status_code=404, detail="System analytics not found")
        
        log_user_action(current_user.id, "viewed_system_analytics", {})
        
        return {
            "total_users": analytics.total_users,
            "total_alerts": analytics.total_alerts,
            "total_triggers": analytics.total_triggers,
            "avg_response_time": analytics.avg_response_time,
            "peak_usage_hours": analytics.peak_usage_hours,
            "most_popular_teams": analytics.most_popular_teams,
            "alert_type_distribution": analytics.alert_type_distribution,
            "system_performance_trend": analytics.system_performance_trend
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving system analytics: {str(e)}")

@router.get("/recommendations")
async def get_alert_recommendations(
    current_user: User = Depends(get_current_user)
):
    """Get personalized alert recommendations for the user"""
    try:
        recommendations = await analytics_service.get_alert_recommendations(current_user.id)
        
        log_user_action(current_user.id, "viewed_recommendations", {
            "recommendations_count": len(recommendations)
        })
        
        return {
            "recommendations": recommendations,
            "count": len(recommendations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving recommendations: {str(e)}")

@router.get("/performance/insights")
async def get_performance_insights(
    current_user: User = Depends(get_current_user)
):
    """Get system performance insights"""
    try:
        insights = await analytics_service.get_performance_insights()
        
        log_user_action(current_user.id, "viewed_performance_insights", {})
        
        return insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving performance insights: {str(e)}")

@router.get("/notifications")
async def get_user_notifications(
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100)
):
    """Get notifications for the current user"""
    try:
        notifications = notification_service.get_user_notifications(current_user.id, limit)
        
        return {
            "notifications": [
                {
                    "id": notif.id,
                    "type": notif.type.value,
                    "priority": notif.priority.value,
                    "title": notif.title,
                    "message": notif.message,
                    "data": notif.data,
                    "timestamp": notif.timestamp.isoformat(),
                    "read": notif.read
                }
                for notif in notifications
            ],
            "count": len(notifications)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving notifications: {str(e)}")

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read"""
    try:
        success = notification_service.mark_notification_read(current_user.id, notification_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        log_user_action(current_user.id, "marked_notification_read", {"notification_id": notification_id})
        
        return {"success": True, "message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking notification as read: {str(e)}")

@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a notification"""
    try:
        success = notification_service.delete_notification(current_user.id, notification_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        log_user_action(current_user.id, "deleted_notification", {"notification_id": notification_id})
        
        return {"success": True, "message": "Notification deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting notification: {str(e)}")

@router.get("/notifications/stats")
async def get_notification_stats(
    current_user: User = Depends(get_current_user)
):
    """Get notification statistics"""
    try:
        stats = notification_service.get_notification_stats()
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving notification stats: {str(e)}")

@router.post("/cache/clear")
async def clear_analytics_cache(
    current_user: User = Depends(get_current_user)
):
    """Clear analytics cache (admin only)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        analytics_service.clear_cache()
        
        log_user_action(current_user.id, "cleared_analytics_cache", {})
        
        return {"success": True, "message": "Analytics cache cleared"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}") 