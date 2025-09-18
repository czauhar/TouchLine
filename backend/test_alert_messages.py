#!/usr/bin/env python3
"""
Alert Message Examples for TouchLine
Shows what SMS alerts look like
"""

from app.sms_service import sms_service

def show_alert_examples():
    """Show examples of what SMS alerts look like"""
    print("📱 TouchLine SMS Alert Examples")
    print("=" * 50)
    
    # Real-world alert scenarios
    scenarios = [
        {
            "name": "Goal Alert",
            "match": {
                "home_team": "Manchester United",
                "away_team": "Liverpool", 
                "home_score": 1,
                "away_score": 0,
                "league": "Premier League",
                "elapsed": 23
            },
            "condition": "Manchester United scored their first goal"
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
        },
        {
            "name": "Close Match Alert",
            "match": {
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "home_score": 2,
                "away_score": 2,
                "league": "Premier League",
                "elapsed": 67
            },
            "condition": "Score difference is 0 goals"
        },
        {
            "name": "Momentum Alert",
            "match": {
                "home_team": "PSG",
                "away_team": "Marseille",
                "home_score": 3,
                "away_score": 1,
                "league": "Ligue 1",
                "elapsed": 78
            },
            "condition": "PSG momentum index reached 85%"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        message = sms_service.format_alert_message(
            scenario["name"],
            scenario["match"],
            scenario["condition"]
        )
        print(f"\n📨 Example {i}: {scenario['name']}")
        print("-" * 40)
        print(message)
        print("-" * 40)
    
    print(f"\n✅ SMS Service Status: {'✅ Configured' if sms_service.is_configured else '❌ Not Configured'}")
    print("📱 To receive real alerts, create alerts in the TouchLine app!")

if __name__ == "__main__":
    show_alert_examples()
