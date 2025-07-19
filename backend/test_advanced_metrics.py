#!/usr/bin/env python3
"""
Test script for Advanced Metrics Calculator
Demonstrates xG, momentum, pressure, and win probability calculations
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.metrics_calculator import metrics_calculator, MatchMetrics
from app.sports_api import sports_api

async def test_advanced_metrics():
    """Test the advanced metrics calculator"""
    print("🧠 Testing Advanced Metrics Calculator...")
    
    # Test 1: Fetch live matches
    print("\n📊 Test 1: Fetching live matches for analysis...")
    live_matches = await sports_api.get_live_matches()
    print(f"✅ Found {len(live_matches)} live matches")
    
    if not live_matches:
        print("❌ No live matches found. Using sample data...")
        # Create sample match data
        sample_match = {
            "fixture": {"id": 12345, "status": {"elapsed": 65}},
            "teams": {
                "home": {"name": "Arsenal"},
                "away": {"name": "Chelsea"}
            },
            "goals": {"home": 2, "away": 1},
            "league": {"name": "Premier League"}
        }
        live_matches = [sample_match]
    
    # Test 2: Calculate advanced metrics for first match
    print("\n🎯 Test 2: Calculating advanced metrics...")
    match_data = live_matches[0]
    metrics = metrics_calculator.calculate_all_metrics(match_data)
    
    print(f"📋 Match: {metrics.home_team} vs {metrics.away_team}")
    print(f"   Score: {metrics.home_score} - {metrics.away_score}")
    print(f"   Time: {metrics.elapsed} minutes")
    print(f"   League: {metrics.league}")
    
    # Test 3: Display all calculated metrics
    print("\n📈 Test 3: Advanced Metrics Breakdown...")
    print(f"🏠 {metrics.home_team}:")
    print(f"   xG: {metrics.home_xg:.2f}")
    print(f"   Momentum: {metrics.home_momentum:.1f}")
    print(f"   Pressure Index: {metrics.home_pressure_index:.2f}")
    print(f"   Win Probability: {metrics.home_win_probability:.1%}")
    print(f"   Possession: {metrics.home_possession:.1f}%")
    print(f"   Shots: {metrics.home_shots} ({metrics.home_shots_on_target} on target)")
    
    print(f"\n✈️ {metrics.away_team}:")
    print(f"   xG: {metrics.away_xg:.2f}")
    print(f"   Momentum: {metrics.away_momentum:.1f}")
    print(f"   Pressure Index: {metrics.away_pressure_index:.2f}")
    print(f"   Win Probability: {metrics.away_win_probability:.1%}")
    print(f"   Possession: {metrics.away_possession:.1f}%")
    print(f"   Shots: {metrics.away_shots} ({metrics.away_shots_on_target} on target)")
    
    print(f"\n🤝 Draw Probability: {metrics.draw_probability:.1%}")
    
    # Test 4: Test team-specific metrics
    print("\n🎯 Test 4: Team-Specific Metrics...")
    home_metrics = metrics_calculator.get_team_metrics(metrics, metrics.home_team)
    away_metrics = metrics_calculator.get_team_metrics(metrics, metrics.away_team)
    
    print(f"📊 {metrics.home_team} metrics:")
    for key, value in home_metrics.items():
        if isinstance(value, float):
            if "probability" in key:
                print(f"   {key}: {value:.1%}")
            else:
                print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    # Test 5: Test advanced alert conditions
    print("\n🚨 Test 5: Advanced Alert Conditions...")
    
    # Test xG alert
    xg_triggered, xg_message = metrics_calculator.evaluate_advanced_condition(
        metrics, "xg > 1.5", metrics.home_team
    )
    print(f"   xG > 1.5 for {metrics.home_team}: {xg_triggered} - {xg_message}")
    
    # Test momentum alert
    momentum_triggered, momentum_message = metrics_calculator.evaluate_advanced_condition(
        metrics, "momentum > 20", metrics.home_team
    )
    print(f"   Momentum > 20 for {metrics.home_team}: {momentum_triggered} - {momentum_message}")
    
    # Test pressure alert
    pressure_triggered, pressure_message = metrics_calculator.evaluate_advanced_condition(
        metrics, "pressure > 0.7", metrics.away_team
    )
    print(f"   Pressure > 0.7 for {metrics.away_team}: {pressure_triggered} - {pressure_message}")
    
    # Test win probability alert
    win_prob_triggered, win_prob_message = metrics_calculator.evaluate_advanced_condition(
        metrics, "win_probability > 0.6", metrics.home_team
    )
    print(f"   Win Probability > 60% for {metrics.home_team}: {win_prob_triggered} - {win_prob_message}")
    
    # Test 6: Show alert examples
    print("\n📱 Test 6: Sample Alert Messages...")
    from app.sms_service import sms_service
    
    match_info = {
        "home_team": metrics.home_team,
        "away_team": metrics.away_team,
        "home_score": metrics.home_score,
        "away_score": metrics.away_score,
        "league": metrics.league,
        "elapsed": metrics.elapsed
    }
    
    # xG alert message
    xg_alert = sms_service.format_alert_message(
        "High xG Alert",
        match_info,
        f"{metrics.home_team} xG: {metrics.home_xg:.2f} (very high expected goals)"
    )
    print("📄 xG Alert Message:")
    print("-" * 40)
    print(xg_alert)
    print("-" * 40)
    
    # Momentum alert message
    momentum_alert = sms_service.format_alert_message(
        "Momentum Alert",
        match_info,
        f"{metrics.home_team} momentum: {metrics.home_momentum:.1f} (strong performance)"
    )
    print("\n📄 Momentum Alert Message:")
    print("-" * 40)
    print(momentum_alert)
    print("-" * 40)
    
    print("\n✅ Advanced Metrics Calculator tests completed!")
    print("\n🚀 Key Features:")
    print("• xG (Expected Goals) - Shot quality analysis")
    print("• Momentum Score - Performance trend analysis")
    print("• Pressure Index - Game situation analysis")
    print("• Win Probability - Real-time outcome prediction")
    print("\n🎯 Next: Integrate with Alert Engine for intelligent alerts!")

if __name__ == "__main__":
    asyncio.run(test_advanced_metrics()) 