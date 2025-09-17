import asyncio
import json
import logging
from typing import Dict, List, Set, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class WebSocketMessage:
    """Standardized WebSocket message format"""
    type: str
    data: dict
    timestamp: str
    user_id: Optional[int] = None
    
    def to_dict(self) -> dict:
        return asdict(self)

class WebSocketManager:
    """Manages WebSocket connections and real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}  # user_id -> set of connections
        self.connection_users: Dict[WebSocket, int] = {}  # connection -> user_id
        self.broadcast_connections: Set[WebSocket] = set()  # connections for broadcast messages
    
    async def connect(self, websocket: WebSocket, user_id: Optional[int] = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if user_id:
            # User-specific connection
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(websocket)
            self.connection_users[websocket] = user_id
            logger.info(f"User {user_id} connected to WebSocket")
        else:
            # Broadcast connection (for public updates)
            self.broadcast_connections.add(websocket)
            logger.info("Broadcast WebSocket connection established")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        user_id = self.connection_users.get(websocket)
        if user_id:
            # Remove from user-specific connections
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            del self.connection_users[websocket]
            logger.info(f"User {user_id} disconnected from WebSocket")
        else:
            # Remove from broadcast connections
            self.broadcast_connections.discard(websocket)
            logger.info("Broadcast WebSocket connection closed")
    
    async def send_personal_message(self, message: WebSocketMessage, user_id: int):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message.to_dict()))
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.disconnect(connection)
    
    async def broadcast_message(self, message: WebSocketMessage):
        """Send a message to all broadcast connections"""
        disconnected = set()
        for connection in self.broadcast_connections:
            try:
                await connection.send_text(json.dumps(message.to_dict()))
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_alert_notification(self, user_id: int, alert_data: dict):
        """Send an alert notification to a specific user"""
        message = WebSocketMessage(
            type="alert_triggered",
            data=alert_data,
            timestamp=datetime.utcnow().isoformat(),
            user_id=user_id
        )
        await self.send_personal_message(message, user_id)
    
    async def broadcast_pattern_notification(self, pattern_data: dict):
        """Send a pattern notification to all broadcast connections"""
        message = WebSocketMessage(
            type="pattern_detected",
            data=pattern_data,
            timestamp=datetime.utcnow().isoformat()
        )
        await self.broadcast_message(message)
    
    async def send_match_update(self, match_data: dict):
        """Send match update to all broadcast connections"""
        message = WebSocketMessage(
            type="match_update",
            data=match_data,
            timestamp=datetime.utcnow().isoformat()
        )
        await self.broadcast_message(message)
    
    async def send_system_status(self, status_data: dict):
        """Send system status update to all connections"""
        message = WebSocketMessage(
            type="system_status",
            data=status_data,
            timestamp=datetime.utcnow().isoformat()
        )
        await self.broadcast_message(message)
    
    async def send_player_update(self, player_data: dict):
        """Send player statistics update"""
        message = WebSocketMessage(
            type="player_update",
            data=player_data,
            timestamp=datetime.utcnow().isoformat()
        )
        await self.broadcast_message(message)
    
    def get_connection_count(self) -> dict:
        """Get current connection statistics"""
        user_connections = sum(len(connections) for connections in self.active_connections.values())
        broadcast_connections = len(self.broadcast_connections)
        total_connections = user_connections + broadcast_connections
        
        return {
            "total_connections": total_connections,
            "user_connections": user_connections,
            "broadcast_connections": broadcast_connections,
            "active_users": len(self.active_connections)
        }

# Global WebSocket manager instance
websocket_manager = WebSocketManager() 