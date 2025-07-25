from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Optional
import json
import logging
from ..websocket_manager import websocket_manager
from ..auth import get_current_user_optional
from ..database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/user")
async def websocket_user_endpoint(websocket: WebSocket, token: Optional[str] = None):
    """WebSocket endpoint for user-specific updates (requires authentication)"""
    try:
        # Try to authenticate user
        user_id = None
        if token:
            try:
                # Simple token validation - in production, use proper JWT validation
                db = next(get_db())
                # For now, assume token contains user_id (simplified)
                # In production, decode JWT and validate
                user_id = int(token) if token.isdigit() else None
            except Exception as e:
                logger.warning(f"Invalid token for WebSocket connection: {e}")
        
        await websocket_manager.connect(websocket, user_id)
        
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong", "timestamp": "now"}))
                elif message.get("type") == "subscribe":
                    # Handle subscription requests
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "data": message.get("data", {}),
                        "timestamp": "now"
                    }))
                
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            websocket_manager.disconnect(websocket)
            
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        try:
            await websocket.close()
        except:
            pass

@router.websocket("/ws/broadcast")
async def websocket_broadcast_endpoint(websocket: WebSocket):
    """WebSocket endpoint for broadcast updates (no authentication required)"""
    try:
        await websocket_manager.connect(websocket)
        
        try:
            while True:
                # Keep connection alive
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle ping/pong for connection health
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong", "timestamp": "now"}))
                
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"Broadcast WebSocket error: {e}")
            websocket_manager.disconnect(websocket)
            
    except Exception as e:
        logger.error(f"Broadcast WebSocket connection error: {e}")
        try:
            await websocket.close()
        except:
            pass

@router.get("/ws/status")
async def get_websocket_status():
    """Get WebSocket connection statistics"""
    return websocket_manager.get_connection_count() 