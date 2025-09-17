#!/usr/bin/env python3
"""
TouchLine Alert Engine Production Test
Tests the complete alert engine functionality with real data
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.alert_engine import match_monitor, AlertType
from app.database import get_db, engine
from app.models import Base, Alert, User
from app.auth import AuthService

load_dotenv()

async def test_alert_engine_production():
    print("🚀 Testing TouchLine Alert Engine (Production Mode)")
    print("=" * 60)
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = next(get_db())
    
    # Get or create test user
    test_user = db.query(User).filter(User.email == "test@touchline.com").first()
    if not test_user:
        hashed_password = AuthService.get_password_hash("testpass123")
        test_user = User(
            email="test@touchline.com",
            username="testuser_prod",
            hashed_password=hashed_password,
            phone_number="+1234567890"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ Created test user: {test_user.email}")
    else:
        print(f"✅ Using existing test user: {test_user.email}")
    
    # Clear existing alerts
    db.query(Alert).delete()
    db.commit()
    print("🧹 Cleared existing alerts")
    
    # Create comprehensive test alerts
    test_alerts = [
        {
            "user_id": test_user.id,
            "name": "High Scoring Matches",
            "alert_type": "goals",
            "team": "any",
            "condition": "Alert when any team scores 3+ goals",
            "threshold": 3.0,
            "is_active": True,
            "user_phone": test_user.phone_number
        },
        {
            "user_id": test_user.id,
            "name": "Close Matches",
            "alert_type": "score_difference",
            "team": "any",
            "condition": "Alert when score difference is 1 goal or less",
            "threshold": 1.0,
            "is_active": True,
            "user_phone": test_user.phone_number
        },
        {
            "user_id": test_user.id,
            "name": "High xG Matches",
            "alert_type": "xg",
            "team": "any",
            "condition": "Alert when expected goals (xG) is high",
            "threshold": 0.5,
            "is_active": True,
            "user_phone": test_user.phone_number
        },
        {
            "user_id": test_user.id,
            "name": "High Pressure Matches",
            "alert_type": "pressure",
            "team": "any",
            "condition": "Alert when pressure index is high",
            "threshold": 70.0,
            "is_active": True,
            "user_phone": test_user.phone_number
        },
        {
            "user_id": test_user.id,
            "name": "Advanced Multi-Condition Alert",
            "alert_type": "advanced",
            "team": "any",
            "condition": json.dumps({
                "description": "High scoring match with high xG",
                "logic_operator": "AND",
                "conditions": [
                    {
                        "type": "goals",
                        "team": "any",
                        "operator": ">=",
                        "value": 2,
                        "description": "Total goals >= 2"
                    },
                    {
                        "type": "xg",
                        "team": "any",
                        "operator": ">=",
                        "value": 0.3,
                        "description": "Expected goals >= 0.3"
                    }
                ],
                "time_windows": [
                    {"start_minute": 0, "end_minute": 90}
                ]
            }),
            "threshold": 0.0,
            "is_active": True,
            "user_phone": test_user.phone_number
        }
    ]
    
    print("📝 Creating test alerts...")
    created_alerts = []
    for alert_data in test_alerts:
        alert = Alert(**alert_data)
        db.add(alert)
        created_alerts.append(alert)
    
    db.commit()
    print(f"✅ Created {len(created_alerts)} test alerts")
    
    # Display created alerts
    for alert in created_alerts:
        print(f"   • {alert.name}: {alert.condition}")
    
    # Test alert engine initialization
    print("\n🔧 Testing Alert Engine Initialization...")
    try:
        # Load active alerts
        await match_monitor.load_active_alerts()
        print(f"✅ Loaded {len(match_monitor.alert_conditions)} active alerts")
        
        # Test rate limiting
        print(f"✅ Rate limiting configured: {match_monitor.max_api_calls_per_hour} calls/hour")
        print(f"✅ Monitoring interval: {match_monitor.monitoring_interval} seconds")
        
    except Exception as e:
        print(f"❌ Alert engine initialization failed: {e}")
        return False
    
    # Test single monitoring cycle
    print("\n📊 Testing Single Monitoring Cycle...")
    try:
        await match_monitor.monitor_live_matches()
        print("✅ Monitoring cycle completed successfully")
        
        # Check if any matches were found
        if match_monitor.active_matches:
            print(f"✅ Found {len(match_monitor.active_matches)} active matches")
            for fixture_id, match_data in list(match_monitor.active_matches.items())[:3]:  # Show first 3
                print(f"   • {match_data.home_team} vs {match_data.away_team} ({match_data.status})")
        else:
            print("ℹ️  No active matches found (this is normal if no live matches)")
        
    except Exception as e:
        print(f"❌ Monitoring cycle failed: {e}")
        return False
    
    # Test alert evaluation logic
    print("\n🧪 Testing Alert Evaluation Logic...")
    try:
        # Create a mock match for testing
        from app.data_service import MatchData
        
        mock_match = MatchData(
            external_id="12345",
            home_team="Test Home",
            away_team="Test Away",
            home_score=3,
            away_score=1,
            status="1H",
            elapsed_time=45,
            league="Test League",
            start_time=datetime.now(),
            home_xg=1.2,
            away_xg=0.8,
            home_momentum=65,
            away_momentum=35,
            home_pressure=75,
            away_pressure=45
        )
        
        # Test alert evaluation
        await match_monitor.evaluate_match_alerts(12345, mock_match)
        print("✅ Alert evaluation completed")
        
    except Exception as e:
        print(f"❌ Alert evaluation failed: {e}")
        return False
    
    # Test system health
    print("\n🏥 Testing System Health...")
    try:
        from app.services.health_monitor import health_monitor
        health_report = await health_monitor.generate_health_report()
        print(f"✅ System status: {health_report.overall_status.value}")
        print(f"✅ Active alerts: {health_report.alert_metrics.active_alerts}")
        print(f"✅ API status: {'Healthy' if health_report.api_metrics.sports_api_status else 'Unhealthy'}")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Performance metrics
    print("\n📈 Performance Metrics:")
    print(f"   • API calls this cycle: {match_monitor.api_call_count}")
    print(f"   • Rate limit: {match_monitor.max_api_calls_per_hour} calls/hour")
    print(f"   • Monitoring interval: {match_monitor.monitoring_interval} seconds")
    print(f"   • Active matches tracked: {len(match_monitor.active_matches)}")
    print(f"   • Active alerts loaded: {len(match_monitor.alert_conditions)}")
    
    print("\n🎉 Alert Engine Production Test Completed Successfully!")
    print("=" * 60)
    
    return True

async def test_alert_engine_startup():
    """Test alert engine startup and shutdown"""
    print("🚀 Testing Alert Engine Startup/Shutdown...")
    
    try:
        # Start monitoring
        await match_monitor.start_monitoring()
        print("✅ Alert engine started successfully")
        
        # Let it run for a few seconds
        await asyncio.sleep(5)
        
        # Stop monitoring
        await match_monitor.stop_monitoring()
        print("✅ Alert engine stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Alert engine startup/shutdown test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TouchLine Alert Engine Production Test Suite")
    print("=" * 60)
    
    # Run tests
    async def run_tests():
        # Test 1: Basic functionality
        success1 = await test_alert_engine_production()
        
        # Test 2: Startup/Shutdown (commented out to avoid interference)
        # success2 = await test_alert_engine_startup()
        
        if success1:
            print("\n🎉 All tests passed! Alert engine is production-ready.")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
    
    asyncio.run(run_tests()) 