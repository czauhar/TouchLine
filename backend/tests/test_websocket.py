#!/usr/bin/env python3
"""
Test script for WebSocket functionality
Tests real-time notifications and WebSocket connections
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.websocket_manager import websocket_manager, WebSocketMessage

class MockWebSocket:
    """Mock WebSocket for testing"""
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.sent_messages = []
        self.closed = False
    
    async def accept(self):
        pass
    
    async def send_text(self, message):
        self.sent_messages.append(message)
    
    async def close(self):
        self.closed = True

async def test_websocket_manager():
    """Test WebSocket manager functionality"""
    print("🧪 Testing WebSocket Manager...")
    
    # Test connection management
    print("\n📡 Test 1: Connection Management")
    
    # Create mock WebSocket connections
    user_ws1 = MockWebSocket(user_id=1)
    user_ws2 = MockWebSocket(user_id=1)
    broadcast_ws = MockWebSocket()
    
    # Connect users
    await websocket_manager.connect(user_ws1, user_id=1)
    await websocket_manager.connect(user_ws2, user_id=1)
    await websocket_manager.connect(broadcast_ws)
    
    print(f"✅ Connected users: {len(websocket_manager.active_connections)}")
    print(f"✅ Broadcast connections: {len(websocket_manager.broadcast_connections)}")
    
    assert len(websocket_manager.active_connections) == 1
    assert len(websocket_manager.broadcast_connections) == 1
    assert len(websocket_manager.active_connections[1]) == 2
    
    # Test personal message sending
    print("\n📨 Test 2: Personal Message Sending")
    
    alert_data = {
        "alert_id": 123,
        "alert_name": "Test Alert",
        "trigger_message": "Test condition met",
        "match_info": {"home_team": "Arsenal", "away_team": "Chelsea"},
        "alert_type": "player_goals",
        "team": "Arsenal",
        "player_name": "Bukayo Saka"
    }
    
    await websocket_manager.send_alert_notification(1, alert_data)
    
    # Check that both user connections received the message
    assert len(user_ws1.sent_messages) == 1
    assert len(user_ws2.sent_messages) == 1
    
    # Parse the sent message
    message1 = json.loads(user_ws1.sent_messages[0])
    print(f"✅ Message sent to user 1: {message1['type']}")
    print(f"   Alert ID: {message1['data']['alert_id']}")
    print(f"   Alert Name: {message1['data']['alert_name']}")
    
    assert message1['type'] == 'alert_triggered'
    assert message1['data']['alert_id'] == 123
    assert message1['data']['alert_name'] == 'Test Alert'
    
    # Test broadcast message sending
    print("\n📢 Test 3: Broadcast Message Sending")
    
    match_data = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "home_score": 2,
        "away_score": 1,
        "elapsed": 75
    }
    
    await websocket_manager.send_match_update(match_data)
    
    # Check that broadcast connection received the message
    assert len(broadcast_ws.sent_messages) == 1
    
    broadcast_message = json.loads(broadcast_ws.sent_messages[0])
    print(f"✅ Broadcast message sent: {broadcast_message['type']}")
    print(f"   Match: {broadcast_message['data']['home_team']} vs {broadcast_message['data']['away_team']}")
    
    assert broadcast_message['type'] == 'match_update'
    assert broadcast_message['data']['home_team'] == 'Arsenal'
    
    # Test system status message
    print("\n🖥️ Test 4: System Status Message")
    
    status_data = {
        "status": "healthy",
        "active_matches": 5,
        "active_alerts": 12,
        "uptime": "2h 15m"
    }
    
    await websocket_manager.send_system_status(status_data)
    
    # Check that broadcast connection received the status message
    assert len(broadcast_ws.sent_messages) == 2
    
    status_message = json.loads(broadcast_ws.sent_messages[1])
    print(f"✅ System status sent: {status_message['type']}")
    print(f"   Status: {status_message['data']['status']}")
    print(f"   Active matches: {status_message['data']['active_matches']}")
    
    assert status_message['type'] == 'system_status'
    assert status_message['data']['status'] == 'healthy'
    
    # Test player update message
    print("\n⚽ Test 5: Player Update Message")
    
    player_data = {
        "player_id": 12345,
        "player_name": "Bukayo Saka",
        "team": "Arsenal",
        "stat_type": "goals",
        "value": 2,
        "match_id": 123456
    }
    
    await websocket_manager.send_player_update(player_data)
    
    # Check that broadcast connection received the player message
    assert len(broadcast_ws.sent_messages) == 3
    
    player_message = json.loads(broadcast_ws.sent_messages[2])
    print(f"✅ Player update sent: {player_message['type']}")
    print(f"   Player: {player_message['data']['player_name']}")
    print(f"   Stat: {player_message['data']['stat_type']} = {player_message['data']['value']}")
    
    assert player_message['type'] == 'player_update'
    assert player_message['data']['player_name'] == 'Bukayo Saka'
    assert player_message['data']['stat_type'] == 'goals'
    
    # Test connection statistics
    print("\n📊 Test 6: Connection Statistics")
    
    stats = websocket_manager.get_connection_count()
    print(f"✅ Total connections: {stats['total_connections']}")
    print(f"✅ User connections: {stats['user_connections']}")
    print(f"✅ Broadcast connections: {stats['broadcast_connections']}")
    print(f"✅ Active users: {stats['active_users']}")
    
    assert stats['total_connections'] == 3
    assert stats['user_connections'] == 2
    assert stats['broadcast_connections'] == 1
    assert stats['active_users'] == 1
    
    # Test disconnection
    print("\n🔌 Test 7: Connection Disconnection")
    
    websocket_manager.disconnect(user_ws1)
    
    # Check that connection was removed
    assert len(websocket_manager.active_connections[1]) == 1
    
    websocket_manager.disconnect(user_ws2)
    
    # Check that user connections are cleaned up
    assert 1 not in websocket_manager.active_connections
    
    websocket_manager.disconnect(broadcast_ws)
    
    # Check that broadcast connections are cleaned up
    assert len(websocket_manager.broadcast_connections) == 0
    
    print("✅ All connections properly disconnected")
    
    # Test WebSocketMessage class
    print("\n📝 Test 8: WebSocketMessage Class")
    
    message = WebSocketMessage(
        type="test_message",
        data={"test": "data"},
        timestamp=datetime.utcnow().isoformat(),
        user_id=1
    )
    
    message_dict = message.to_dict()
    print(f"✅ Message created: {message_dict['type']}")
    print(f"   Data: {message_dict['data']}")
    print(f"   User ID: {message_dict['user_id']}")
    
    assert message_dict['type'] == 'test_message'
    assert message_dict['data']['test'] == 'data'
    assert message_dict['user_id'] == 1
    
    print("\n" + "=" * 50)
    print("✅ All WebSocket Tests Passed!")
    print("\n🎯 Key Features Tested:")
    print("   • Connection management")
    print("   • Personal message sending")
    print("   • Broadcast message sending")
    print("   • Alert notifications")
    print("   • Match updates")
    print("   • System status updates")
    print("   • Player updates")
    print("   • Connection statistics")
    print("   • Disconnection handling")
    print("   • Message serialization")
    
    print("\n🚀 Next Steps:")
    print("1. Test with real WebSocket connections")
    print("2. Integrate with frontend components")
    print("3. Test with live alert triggers")
    print("4. Monitor connection performance")

if __name__ == "__main__":
    asyncio.run(test_websocket_manager()) 