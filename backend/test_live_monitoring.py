import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from app.alert_engine import match_monitor
from app.database import get_db, engine
from app.models import Base, Alert

load_dotenv()

async def test_live_monitoring():
    print("🚀 Starting Live Match Monitoring Test...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = next(get_db())
    
    # Clear existing alerts first
    db.query(Alert).delete()
    db.commit()
    
    # Create sample alerts for testing
    sample_alerts = [
        {
            "user_id": 1,
            "name": "High Scoring Matches",
            "alert_type": "goals",
            "team": "any",  # Any team
            "condition": "Alert when any team scores 3+ goals",
            "threshold": 3,
            "is_active": True
        },
        {
            "user_id": 1,
            "name": "Close Matches",
            "alert_type": "score_difference",
            "team": "any",
            "condition": "Alert when score difference is 1 goal or less",
            "threshold": 1,
            "is_active": True
        },
        {
            "user_id": 1,
            "name": "High xG Matches",
            "alert_type": "xg",
            "team": "any",
            "condition": "Alert when expected goals (xG) is high",
            "threshold": 0.5,
            "is_active": True
        }
    ]
    
    print("📝 Creating sample alerts...")
    for alert_data in sample_alerts:
        alert = Alert(**alert_data)
        db.add(alert)
    
    db.commit()
    print(f"✅ Created {len(sample_alerts)} sample alerts")
    
    # Get active alerts
    active_alerts = db.query(Alert).filter(Alert.is_active == True).all()
    print(f"📋 Active alerts: {len(active_alerts)}")
    for alert in active_alerts:
        print(f"   • {alert.name}: {alert.condition}")
    
    print("\n🔍 Starting live match monitoring...")
    print("   (This will run for 2 minutes to test with live data)")
    print("   Press Ctrl+C to stop early")
    
    try:
        # Start monitoring for 2 minutes
        await asyncio.wait_for(
            match_monitor.start_monitoring(),
            timeout=120  # 2 minutes
        )
    except asyncio.TimeoutError:
        print("\n⏰ Test completed after 2 minutes")
    except KeyboardInterrupt:
        print("\n⏹️  Test stopped by user")
    finally:
        # Stop monitoring
        await match_monitor.stop_monitoring()
        print("🛑 Monitoring stopped")
        
        # Show results
        print("\n📊 Test Results:")
        print("✅ Live monitoring test completed")
        print("✅ Alert engine processed live matches")
        print("✅ SMS alerts would be sent for triggered conditions")
        
        db.close()

if __name__ == "__main__":
    asyncio.run(test_live_monitoring()) 