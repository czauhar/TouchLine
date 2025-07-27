#!/usr/bin/env python3
"""
Test script for Player-Specific Alert Types
Tests player statistics tracking and alert evaluation
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.analytics import AnalyticsEngine, MatchMetrics, PlayerStats, Condition, ConditionType, Operator
from app.alert_engine import MatchMonitor, AlertCondition, AlertType

# Global test instances
analytics_engine = AnalyticsEngine()
match_monitor = MatchMonitor()

def test_player_stats():
    """Test PlayerStats dataclass properties"""
    print("\n🧪 Testing PlayerStats properties...")
    
    player = PlayerStats(
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
    
    print(f"✅ Player: {player.player_name}")
    print(f"   Goals: {player.goals}, Assists: {player.assists}")
    print(f"   Goal Contributions: {player.goal_contributions}")
    print(f"   Pass Accuracy: {player.pass_accuracy:.1f}%")
    
    assert player.goal_contributions == 3  # 2 goals + 1 assist
    assert abs(player.pass_accuracy - 88.9) < 0.1  # 40/45 * 100
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

@pytest.mark.asyncio
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
        operator=Operator.EQUALS,
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
    assert "Lionel Messi assists: 1 ==" in message
    
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

@pytest.mark.asyncio
async def test_alert_engine_player_alerts():
    """Test alert engine with player-specific alerts"""
    print("\n🧪 Testing alert engine player alerts...")
    
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
    
    # Create test alert condition
    alert_condition = AlertCondition(
        alert_id=1,
        alert_type=AlertType.PLAYER_GOALS,
        team="Inter Miami",
        condition="Messi scores 2+ goals",
        threshold=2.0,
        player_id=12345,
        player_name="Lionel Messi"
    )
    
    # Test player goals alert evaluation
    result, message = match_monitor.evaluate_player_goals_alert(alert_condition, metrics)
    
    print(f"✅ Player Goals Alert: {result}")
    print(f"   Message: {message}")
    
    assert result == True
    assert "Lionel Messi has scored 2 goals" in message
    
    # Test player goal contributions alert
    contributions_condition = AlertCondition(
        alert_id=2,
        alert_type=AlertType.PLAYER_GOAL_CONTRIBUTIONS,
        team="Inter Miami",
        condition="Messi involved in 3+ goals",
        threshold=3.0,
        player_id=12345,
        player_name="Lionel Messi"
    )
    
    result, message = match_monitor.evaluate_player_goal_contributions_alert(contributions_condition, metrics)
    
    print(f"✅ Player Goal Contributions Alert: {result}")
    print(f"   Message: {message}")
    
    assert result == True
    assert "Lionel Messi has 3 goal contributions" in message
    
    print("✅ Alert engine player alerts tests passed!")

@pytest.mark.asyncio
async def test_player_data_extraction():
    """Test player data extraction from match data"""
    print("\n🧪 Testing player data extraction...")
    
    # Simulate match data with events and lineups
    match_data = {
        "fixture": {"id": 123456},
        "teams": {
            "home": {"name": "Inter Miami", "id": 1},
            "away": {"name": "LA Galaxy", "id": 2}
        },
        "goals": {"home": 3, "away": 1},
        "events": [
            {
                "player": {"id": 12345, "name": "Lionel Messi"},
                "type": "Goal",
                "team": {"name": "Inter Miami"},
                "time": {"elapsed": 15}
            },
            {
                "player": {"id": 12345, "name": "Lionel Messi"},
                "type": "Goal",
                "team": {"name": "Inter Miami"},
                "time": {"elapsed": 45}
            },
            {
                "player": {"id": 12346, "name": "Luis Suarez"},
                "type": "Goal",
                "team": {"name": "Inter Miami"},
                "time": {"elapsed": 60}
            }
        ],
        "lineups": [
            {
                "team": {"name": "Inter Miami"},
                "formation": "4-3-3",
                "startXI": [
                    {"player": {"id": 12345, "name": "Lionel Messi", "pos": "F"}},
                    {"player": {"id": 12346, "name": "Luis Suarez", "pos": "F"}}
                ]
            }
        ]
    }
    
    # Calculate metrics
    metrics = analytics_engine.calculate_all_metrics(match_data)
    
    print(f"✅ Extracted {len(metrics.players)} players")
    print(f"   Messi: {metrics.players[12345].goals} goals")
    print(f"   Suarez: {metrics.players[12346].goals} goals")
    
    assert len(metrics.players) >= 2
    assert metrics.players[12345].goals == 2
    assert metrics.players[12346].goals == 1
    assert metrics.players[12345].player_name == "Lionel Messi"
    assert metrics.players[12346].player_name == "Luis Suarez"
    
    print("✅ Player data extraction tests passed!")

async def run_all_tests():
    """Run all player alert tests"""
    print("🚀 Running Player Alert Tests...")
    
    # Run synchronous tests
    test_player_stats()
    test_match_metrics_with_players()
    
    # Run asynchronous tests
    await test_player_condition_evaluation()
    await test_alert_engine_player_alerts()
    await test_player_data_extraction()
    
    print("\n🎉 All Player Alert Tests Passed!")

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 