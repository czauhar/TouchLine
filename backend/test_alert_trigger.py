#!/usr/bin/env python3
"""
Test alert triggering system with demo data
"""

import os
import sys
import asyncio
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import Match, Alert, AlertHistory
from app.sms_service import sms_service

async def check_and_trigger_alerts():
    """Check all matches against all alerts and trigger if conditions are met"""
    print("🔍 Checking alerts against matches...")
    
    # Get database session
    db = next(get_db())
    
    # Get all active alerts
    alerts = db.query(Alert).filter(Alert.is_active == True).all()
    print(f"Found {len(alerts)} active alerts")
    
    # Get all matches
    matches = db.query(Match).all()
    print(f"Found {len(matches)} matches")
    
    triggered_alerts = []
    
    for match in matches:
        print(f"\n📊 Checking match: {match.home_team} vs {match.away_team}")
        print(f"   Score: {match.home_score} - {match.away_score}")
        print(f"   Status: {match.status}")
        
        for alert in alerts:
            print(f"\n🔔 Checking alert: {alert.name}")
            print(f"   Team: {alert.team}")
            print(f"   Type: {alert.alert_type}")
            print(f"   Threshold: {alert.threshold}")
            
            # Check if alert applies to this match
            if alert.team not in [match.home_team, match.away_team]:
                print(f"   ❌ Alert doesn't apply to this match")
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
                    print(f"   ✅ GOAL ALERT TRIGGERED! {team_score} >= {alert.threshold}")
                else:
                    print(f"   ❌ Goal alert not triggered: {team_score} < {alert.threshold}")
            
            elif alert.alert_type == "possession":
                # For demo purposes, simulate possession data
                if alert.team == match.home_team:
                    possession = 65  # Simulate high possession
                else:
                    possession = 35
                
                if possession >= alert.threshold:
                    triggered = True
                    alert_message = f"🚨 ALERT: {alert.team} has {possession}% possession (threshold: {alert.threshold}%)"
                    print(f"   ✅ POSSESSION ALERT TRIGGERED! {possession}% >= {alert.threshold}%")
                else:
                    print(f"   ❌ Possession alert not triggered: {possession}% < {alert.threshold}%")
            
            if triggered:
                print(f"   🎯 ALERT TRIGGERED: {alert_message}")
                
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
                
                # Send SMS if phone number is provided
                if alert.user_phone:
                    try:
                        sms_result = await sms_service.send_sms(
                            to_number=alert.user_phone,
                            message=alert_message
                        )
                        print(f"   📱 SMS sent: {sms_result}")
                    except Exception as e:
                        print(f"   ❌ SMS failed: {e}")
                else:
                    print(f"   ⚠️ No phone number for SMS")
                
                triggered_alerts.append({
                    "alert": alert,
                    "match": match,
                    "message": alert_message
                })
    
    # Commit all changes
    db.commit()
    
    print(f"\n🎉 Alert check complete!")
    print(f"📊 Triggered {len(triggered_alerts)} alerts")
    
    for triggered in triggered_alerts:
        print(f"   ✅ {triggered['alert'].name} - {triggered['message']}")
    
    return triggered_alerts

async def main():
    """Main function to test alert triggering"""
    print("🚀 Testing alert triggering system...")
    
    try:
        triggered_alerts = await check_and_trigger_alerts()
        
        if triggered_alerts:
            print(f"\n🎯 Successfully triggered {len(triggered_alerts)} alerts!")
        else:
            print("\n📭 No alerts were triggered")
            
    except Exception as e:
        print(f"❌ Error testing alerts: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
