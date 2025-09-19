#!/usr/bin/env python3
"""
Create demo match data for testing the alert system
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db, create_tables
from app.models import Match, Alert, User
from app.sports_api import sports_api

async def create_demo_matches():
    """Create demo match data"""
    print("🏈 Creating demo match data...")
    
    # Get database session
    db = next(get_db())
    
    # Create tables if they don't exist
    create_tables()
    
    # Create demo matches
    demo_matches = [
        {
            "external_id": "demo_match_1",
            "home_team": "Manchester United",
            "away_team": "Liverpool",
            "league": "Premier League",
            "start_time": datetime.now() + timedelta(hours=1),
            "status": "scheduled",
            "home_score": 0,
            "away_score": 0
        },
        {
            "external_id": "demo_match_2", 
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "league": "Premier League",
            "start_time": datetime.now() + timedelta(hours=3),
            "status": "scheduled",
            "home_score": 0,
            "away_score": 0
        },
        {
            "external_id": "demo_match_3",
            "home_team": "Barcelona",
            "away_team": "Real Madrid",
            "league": "La Liga",
            "start_time": datetime.now() + timedelta(hours=5),
            "status": "scheduled",
            "home_score": 0,
            "away_score": 0
        }
    ]
    
    # Clear existing demo matches
    db.query(Match).filter(Match.external_id.like("demo_match_%")).delete()
    
    # Create new demo matches
    for match_data in demo_matches:
        match = Match(**match_data)
        db.add(match)
    
    db.commit()
    print(f"✅ Created {len(demo_matches)} demo matches")
    
    return demo_matches

async def create_demo_alerts():
    """Create demo alerts for testing"""
    print("🔔 Creating demo alerts...")
    
    # Get database session
    db = next(get_db())
    
    # Get or create demo user
    demo_user = db.query(User).filter(User.email == "demo@touchline.com").first()
    if not demo_user:
        print("❌ Demo user not found. Please create a user first.")
        return
    
    # Clear existing demo alerts
    db.query(Alert).filter(Alert.name.like("Demo Alert%")).delete()
    
    # Create demo alerts
    demo_alerts = [
        {
            "name": "Demo Alert: Man United Goals",
            "team": "Manchester United",
            "alert_type": "goals",
            "threshold": 1.0,
            "condition": "Manchester United goals >= 1",
            "time_window": None,
            "user_phone": "+1234567890",
            "is_active": True,
            "user_id": demo_user.id
        },
        {
            "name": "Demo Alert: Liverpool Goals",
            "team": "Liverpool", 
            "alert_type": "goals",
            "threshold": 2.0,
            "condition": "Liverpool goals >= 2",
            "time_window": None,
            "user_phone": "+1234567890",
            "is_active": True,
            "user_id": demo_user.id
        },
        {
            "name": "Demo Alert: Arsenal Possession",
            "team": "Arsenal",
            "alert_type": "possession",
            "threshold": 60.0,
            "condition": "Arsenal possession >= 60%",
            "time_window": None,
            "user_phone": "+1234567890",
            "is_active": True,
            "user_id": demo_user.id
        }
    ]
    
    for alert_data in demo_alerts:
        alert = Alert(**alert_data)
        db.add(alert)
    
    db.commit()
    print(f"✅ Created {len(demo_alerts)} demo alerts")
    
    return demo_alerts

async def main():
    """Main function to create demo data"""
    print("🚀 Setting up demo data for TouchLine...")
    
    try:
        # Create demo matches
        matches = await create_demo_matches()
        
        # Create demo alerts
        alerts = await create_demo_alerts()
        
        print("\n🎉 Demo data setup complete!")
        print(f"📊 Created {len(matches)} demo matches")
        print(f"🔔 Created {len(alerts)} demo alerts")
        print("\nYou can now test the alert system with this demo data.")
        
    except Exception as e:
        print(f"❌ Error creating demo data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
