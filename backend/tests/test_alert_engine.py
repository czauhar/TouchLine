#!/usr/bin/env python3
"""
Test script for the Alert Engine
Run this to test the match monitoring and alert evaluation
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.alert_engine import MatchMonitor, AlertType, AlertCondition
from app.sports_api import sports_api

load_dotenv()

@pytest.mark.asyncio
async def test_alert_engine():
    """Test the alert engine with sample data"""
    print("🚨 Testing Alert Engine...")
    
    # Test 1: Fetch live matches
    print("\n📊 Test 1: Fetching live matches...")
    live_matches = await sports_api.get_live_matches()
    print(f"✅ Found {len(live_matches)} live matches")
    
    if live_matches:
        # Show first match details
        first_match = live_matches[0]
        match_info = sports_api.format_match_data(first_match)
        print(f"📋 Sample match: {match_info['home_team']} vs {match_info['away_team']}")
        print(f"   Score: {match_info['home_score']} - {match_info['away_score']}")
        print(f"   Status: {match_info['status']}")
    
    # Test 2: Create sample alert condition
    print("\n🎯 Test 2: Creating sample alert condition...")
    sample_condition = AlertCondition(
        alert_id=1,
        alert_type=AlertType.GOALS,
        team="Arsenal",  # Example team
        condition="goals >= 2",
        threshold=2.0,
        user_phone="+17172711742"  # Your verified number
    )
    
    # Test 3: Evaluate alert condition
    print("\n🔍 Test 3: Evaluating alert conditions...")
    if live_matches:
        match_data = live_matches[0]
        match_info = sports_api.format_match_data(match_data)
        
        # Test if Arsenal is playing
        home_team = match_info.get("home_team", "").lower()
        away_team = match_info.get("away_team", "").lower()
        target_team = sample_condition.team.lower()
        
        if target_team in home_team or target_team in away_team:
            print(f"✅ Arsenal is playing in this match!")
            
            # Test goals evaluation
            team_score = match_info.get("home_score", 0) if target_team in home_team else match_info.get("away_score", 0)
            triggered = team_score >= sample_condition.threshold
            
            print(f"   Arsenal score: {team_score}")
            print(f"   Threshold: {sample_condition.threshold}")
            print(f"   Alert triggered: {triggered}")
            
            if triggered:
                print("   🚨 This would send an SMS alert!")
        else:
            print(f"❌ Arsenal is not playing in this match")
            print(f"   Teams: {match_info.get('home_team')} vs {match_info.get('away_team')}")
    
    # Test 4: Test SMS formatting
    print("\n📱 Test 4: Testing SMS message formatting...")
    from app.sms_service import sms_service
    
    sample_match_info = {
        "home_team": "Arsenal",
        "away_team": "Chelsea", 
        "home_score": 2,
        "away_score": 1,
        "league": "Premier League",
        "elapsed": 75
    }
    
    message = sms_service.format_alert_message(
        "Test Alert",
        sample_match_info,
        "Arsenal has scored 2 goals"
    )
    
    print("📄 Sample SMS message:")
    print("-" * 40)
    print(message)
    print("-" * 40)
    
    print("\n✅ Alert Engine tests completed!")
    print("\n🚀 Next steps:")
    print("1. Start the background monitor: await match_monitor.start_monitoring()")
    print("2. Create real alerts in the database")
    print("3. Test with live matches")

if __name__ == "__main__":
    asyncio.run(test_alert_engine()) 