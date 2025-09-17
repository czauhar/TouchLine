#!/usr/bin/env python3
"""
SMS Testing Script for TouchLine
Tests SMS notifications and alert formatting
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.sms_service import sms_service
from app.core.config import settings

def test_sms_configuration():
    """Test SMS service configuration"""
    print("🔧 Testing SMS Configuration...")
    print(f"Twilio Account SID: {'✅ Set' if settings.TWILIO_ACCOUNT_SID else '❌ Not Set'}")
    print(f"Twilio Auth Token: {'✅ Set' if settings.TWILIO_AUTH_TOKEN else '❌ Not Set'}")
    print(f"Twilio Phone Number: {'✅ Set' if settings.TWILIO_PHONE_NUMBER else '❌ Not Set'}")
    print(f"SMS Service Configured: {'✅ Yes' if sms_service.is_configured else '❌ No'}")
    return sms_service.is_configured

def test_alert_message_formatting():
    """Test alert message formatting"""
    print("\n📱 Testing Alert Message Formatting...")
    
    # Sample match data
    match_info = {
        "home_team": "Manchester United",
        "away_team": "Liverpool",
        "home_score": 2,
        "away_score": 1,
        "league": "Premier League",
        "elapsed": 75
    }
    
    # Test different alert types
    alert_tests = [
        {
            "name": "High Scoring Match",
            "condition": "Total goals >= 3"
        },
        {
            "name": "Close Match Alert",
            "condition": "Score difference <= 1"
        },
        {
            "name": "Late Goal Alert",
            "condition": "Goal scored after 80 minutes"
        }
    ]
    
    for test in alert_tests:
        message = sms_service.format_alert_message(
            test["name"],
            match_info,
            test["condition"]
        )
        print(f"\n📨 {test['name']}:")
        print(f"   {message}")
    
    return True

def test_sms_sending(phone_number: str = None):
    """Test actual SMS sending"""
    if not sms_service.is_configured:
        print("❌ SMS service not configured. Please set Twilio credentials.")
        return False
    
    if not phone_number:
        phone_number = input("Enter your phone number (with country code, e.g., +1234567890): ")
    
    print(f"\n📱 Testing SMS to {phone_number}...")
    
    # Test message
    test_message = "🧪 TouchLine Test Message\n\nThis is a test SMS from TouchLine to verify SMS notifications are working correctly.\n\n⚽ TouchLine Alert System"
    
    try:
        success = sms_service.send_sms(phone_number, test_message)
        if success:
            print("✅ Test SMS sent successfully!")
            print("📱 Check your phone for the test message.")
            return True
        else:
            print("❌ Failed to send test SMS.")
            return False
    except Exception as e:
        print(f"❌ Error sending test SMS: {e}")
        return False

def test_alert_scenarios():
    """Test different alert scenarios"""
    print("\n🎯 Testing Alert Scenarios...")
    
    scenarios = [
        {
            "name": "Goal Alert",
            "match": {
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "home_score": 1,
                "away_score": 0,
                "league": "Premier League",
                "elapsed": 45
            },
            "condition": "Arsenal scored their first goal"
        },
        {
            "name": "Late Equalizer",
            "match": {
                "home_team": "Barcelona",
                "away_team": "Real Madrid",
                "home_score": 2,
                "away_score": 2,
                "league": "La Liga",
                "elapsed": 89
            },
            "condition": "Real Madrid equalized in the 89th minute"
        },
        {
            "name": "High Scoring Game",
            "match": {
                "home_team": "Bayern Munich",
                "away_team": "Borussia Dortmund",
                "home_score": 4,
                "away_score": 3,
                "league": "Bundesliga",
                "elapsed": 90
            },
            "condition": "Total goals reached 7"
        }
    ]
    
    for scenario in scenarios:
        message = sms_service.format_alert_message(
            scenario["name"],
            scenario["match"],
            scenario["condition"]
        )
        print(f"\n📨 {scenario['name']}:")
        print(f"   {message}")

def main():
    """Main test function"""
    print("🚀 TouchLine SMS Testing Script")
    print("=" * 50)
    
    # Test configuration
    if not test_sms_configuration():
        print("\n❌ SMS service not configured. Please set up Twilio credentials in .env file:")
        print("TWILIO_ACCOUNT_SID=your_account_sid")
        print("TWILIO_AUTH_TOKEN=your_auth_token")
        print("TWILIO_PHONE_NUMBER=your_twilio_phone_number")
        return
    
    # Test message formatting
    test_alert_message_formatting()
    
    # Test alert scenarios
    test_alert_scenarios()
    
    # Test actual SMS sending
    print("\n" + "=" * 50)
    send_test = input("Do you want to send a test SMS? (y/n): ").lower().strip()
    if send_test == 'y':
        test_sms_sending()
    
    print("\n✅ SMS testing completed!")

if __name__ == "__main__":
    main()
