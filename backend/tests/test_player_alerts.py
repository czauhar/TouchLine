#!/usr/bin/env python3
"""
Test script for Player-Specific Alert Types
Tests the new player statistics tracking and alert evaluation
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.analytics import analytics_engine, PlayerStats, MatchMetrics, Condition, ConditionType, Operator
from app.alert_engine import AlertCondition, AlertType

def test_player_stats():
    """Test PlayerStats data structure"""
    print("🧪 Testing PlayerStats...")
    
    player = PlayerStats(
        player_id=12345,
        player_name="Lionel Messi",
        team="Inter Miami",
        position="Forward",
        goals=2,
        assists=1,
        yellow_cards=0,
        red_cards=0,
        shots=5,
        shots_on_target=3,
        passes=45,
        passes_accurate=40,
        tackles=2,
        minutes_played=90,
        rating=8.5
    )
    
    print(f"✅ Player: {player.player_name}")
    print(f"   Goals: {player.goals}")
    print(f"   Assists: {player.assists}")
    print(f"   Goal Contributions: {player.goal_contributions}")
    print(f"   Pass Accuracy: {player.pass_accuracy:.1f}%")
    print(f"   Rating: {player.rating}")
    
    assert player.goal_contributions == 3
    assert abs(player.pass_accuracy - 88.9) < 0.1  # Allow for floating point precision
    print("✅ PlayerStats tests passed!")

def test_match_metrics_with_players():
    """Test MatchMetrics with player statistics"""
    print("\n🧪 Testing MatchMetrics with players...")
    
    metrics = MatchMetrics(
        fixture_id=123456,
        home_team="Inter Miami",
        away_team="LA Galaxy",
        home_score=3,
        away_score=1,
        elapsed=90,
        league="MLS"
    )
    
    # Add player statistics
    messi = PlayerStats(
        player_id=12345,
        player_name="Lionel Messi",
        team="Inter Miami",
        position="Forward",
        goals=2,
        assists=1,
        shots=5,
        passes=45,
        passes_accurate=40,
        minutes_played=90,
        rating=8.5
    )
    
    suarez = PlayerStats(
        player_id=12346,
        player_name="Luis Suarez",
        team="Inter Miami",
        position="Forward",
        goals=1,
        assists=0,
        shots=3,
        passes=30,
        passes_accurate=25,
        minutes_played=90,
        rating=7.2
    )
    
    metrics.players[12345] = messi
    metrics.players[12346] = suarez
    
    print(f"✅ Match: {metrics.home_team} {metrics.home_score} - {metrics.away_score} {metrics.away_team}")
    print(f"   Players tracked: {len(metrics.players)}")
    print(f"   Messi goals: {messi.goals}")
    print(f"   Suarez goals: {suarez.goals}")
    
    assert len(metrics.players) == 2
    assert metrics.players[12345].goals == 2
    assert metrics.players[12346].goals == 1
    print("✅ MatchMetrics with players tests passed!")

async def test_player_condition_evaluation():
    """Test player-specific condition evaluation"""
    print("\n🧪 Testing player condition evaluation...")
    
    # Create test metrics
    metrics = MatchMetrics(
        fixture_id=123456,
        home_team="Inter Miami",
        away_team="LA Galaxy",
        home_score=3,
        away_score=1,
        elapsed=90,
        league="MLS"
    )
    
    # Add player
    messi = PlayerStats(
        player_id=12345,
        player_name="Lionel Messi",
        team="Inter Miami",
        position="Forward",
        goals=2,
        assists=1,
        shots=5,
        passes=45,
        passes_accurate=40,
        minutes_played=90,
        rating=8.5
    )
    metrics.players[12345] = messi
    
    # Test player goals condition
    goals_condition = Condition(
        condition_type=ConditionType.PLAYER_GOALS,
        team="Inter Miami",
        operator=Operator.GREATER_EQUAL,
        value=2,
        player_id=12345,
        player_name="Lionel Messi"
    )
    
    result, message = await analytics_engine._evaluate_single_condition(
        goals_condition, {}, metrics
    )
    
    print(f"✅ Player Goals Condition: {result}")
    print(f"   Message: {message}")
    
    assert result == True
    assert "Lionel Messi goals: 2 >=" in message
    
    # Test player assists condition
    assists_condition = Condition(
        condition_type=ConditionType.PLAYER_ASSISTS,
        team="Inter Miami",
        operator=Operator.GREATER_EQUAL,
        value=1,
        player_id=12345,
        player_name="Lionel Messi"
    )
    
    result, message = await analytics_engine._evaluate_single_condition(
        assists_condition, {}, metrics
    )
    
    print(f"✅ Player Assists Condition: {result}")
    print(f"   Message: {message}")
    
    assert result == True
    assert "Lionel Messi assists: 1 >=" in message
    
    # Test player goal contributions condition
    contributions_condition = Condition(
        condition_type=ConditionType.PLAYER_GOAL_CONTRIBUTIONS,
        team="Inter Miami",
        operator=Operator.GREATER_EQUAL,
        value=3,
        player_id=12345,
        player_name="Lionel Messi"
    )
    
    result, message = await analytics_engine._evaluate_single_condition(
        contributions_condition, {}, metrics
    )
    
    print(f"✅ Player Goal Contributions Condition: {result}")
    print(f"   Message: {message}")
    
    assert result == True
    assert "Lionel Messi goal contributions: 3 >=" in message
    
    print("✅ Player condition evaluation tests passed!")

async def test_alert_engine_player_alerts():
    """Test alert engine with player-specific alerts"""
    print("\n🧪 Testing alert engine player alerts...")
    
    from app.alert_engine import match_monitor
    
    # Create test metrics
    metrics = MatchMetrics(
        fixture_id=123456,
        home_team="Inter Miami",
        away_team="LA Galaxy",
        home_score=3,
        away_score=1,
        elapsed=90,
        league="MLS"
    )
    
    # Add player
    messi = PlayerStats(
        player_id=12345,
        player_name="Lionel Messi",
        team="Inter Miami",
        position="Forward",
        goals=2,
        assists=1,
        shots=5,
        passes=45,
        passes_accurate=40,
        minutes_played=90,
        rating=8.5
    )
    metrics.players[12345] = messi
    
    # Test player goals alert
    goals_alert = AlertCondition(
        alert_id=1,
        alert_type=AlertType.PLAYER_GOALS,
        team="Inter Miami",
        condition="Messi scores 2+ goals",
        threshold=2.0,
        player_id=12345,
        player_name="Lionel Messi"
    )
    
    result, message = match_monitor.evaluate_player_goals_alert(goals_alert, metrics)
    
    print(f"✅ Player Goals Alert: {result}")
    print(f"   Message: {message}")
    
    assert result == True
    assert "Lionel Messi has scored 2 goals" in message
    
    # Test player goal contributions alert
    contributions_alert = AlertCondition(
        alert_id=2,
        alert_type=AlertType.PLAYER_GOAL_CONTRIBUTIONS,
        team="Inter Miami",
        condition="Messi involved in 3+ goals",
        threshold=3.0,
        player_id=12345,
        player_name="Lionel Messi"
    )
    
    result, message = match_monitor.evaluate_player_goal_contributions_alert(contributions_alert, metrics)
    
    print(f"✅ Player Goal Contributions Alert: {result}")
    print(f"   Message: {message}")
    
    assert result == True
    assert "Lionel Messi has 3 goal contributions" in message
    
    print("✅ Alert engine player alerts tests passed!")

async def test_player_data_extraction():
    """Test player data extraction from match data"""
    print("\n🧪 Testing player data extraction...")
    
    # Sample match data with events and lineups
    match_data = {
        "fixture": {
            "id": 123456,
            "status": {"elapsed": 90}
        },
        "teams": {
            "home": {"id": 1, "name": "Inter Miami"},
            "away": {"id": 2, "name": "LA Galaxy"}
        },
        "goals": {"home": 3, "away": 1},
        "league": {"name": "MLS"},
        "events": [
            {
                "type": "Goal",
                "player": {"id": 12345, "name": "Lionel Messi"},
                "team": {"id": 1}
            },
            {
                "type": "Goal",
                "player": {"id": 12345, "name": "Lionel Messi"},
                "team": {"id": 1}
            },
            {
                "type": "Card",
                "player": {"id": 12346, "name": "Luis Suarez"},
                "team": {"id": 1},
                "detail": {"type": "yellow"}
            }
        ],
        "lineups": [
            {
                "team": {"id": 1},
                "startXI": [
                    {
                        "player": {"id": 12345, "name": "Lionel Messi"},
                        "pos": "F"
                    }
                ],
                "substitutes": [
                    {
                        "player": {"id": 12346, "name": "Luis Suarez"},
                        "pos": "F"
                    }
                ]
            }
        ]
    }
    
    # Calculate metrics
    metrics = analytics_engine.calculate_all_metrics(match_data)
    
    print(f"✅ Extracted {len(metrics.players)} players")
    
    # Check Messi's stats
    if 12345 in metrics.players:
        messi = metrics.players[12345]
        print(f"   Messi goals: {messi.goals}")
        print(f"   Messi team: {messi.team}")
        print(f"   Messi position: {messi.position}")
        
        assert messi.goals == 2
        assert messi.team == "Inter Miami"
        assert messi.position == "F"
    
    # Check Suarez's stats
    if 12346 in metrics.players:
        suarez = metrics.players[12346]
        print(f"   Suarez yellow cards: {suarez.yellow_cards}")
        print(f"   Suarez team: {suarez.team}")
        
        assert suarez.yellow_cards == 1
        assert suarez.team == "Inter Miami"
    
    print("✅ Player data extraction tests passed!")

async def run_all_tests():
    """Run all player alert tests"""
    print("🚀 Starting Player-Specific Alert Tests...")
    print("=" * 50)
    
    try:
        test_player_stats()
        test_match_metrics_with_players()
        await test_player_condition_evaluation()
        await test_alert_engine_player_alerts()
        await test_player_data_extraction()
        
        print("\n" + "=" * 50)
        print("✅ All Player-Specific Alert Tests Passed!")
        print("\n🎯 Key Features Tested:")
        print("   • PlayerStats data structure")
        print("   • Player-specific condition evaluation")
        print("   • Alert engine player alerts")
        print("   • Player data extraction from match events")
        print("   • Goal contributions calculation")
        print("   • Pass accuracy calculation")
        
        print("\n🚀 Next Steps:")
        print("1. Test with real match data from API")
        print("2. Create player-specific alerts in the UI")
        print("3. Monitor live matches for player events")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 