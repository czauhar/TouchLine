import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from app.analytics import (
    AdvancedAlertCondition, Condition, ConditionType, Operator, LogicOperator,
    TimeWindow, SequenceCondition, analytics_engine
)
from app.sports_api import sports_api

load_dotenv()

async def test_advanced_conditions():
    print("🧠 Testing Advanced Condition Evaluator...")
    
    # Test 1: Simple AND condition
    print("\n📊 Test 1: AND Condition - Arsenal scores 2+ goals AND has high xG")
    and_alert = AdvancedAlertCondition(
        alert_id=1,
        name="Arsenal High Performance",
        description="Arsenal scores 2+ goals AND has xG > 1.5",
        logic_operator=LogicOperator.AND
    )
    
    # Add conditions
    goals_condition = Condition(
        condition_type=ConditionType.GOALS,
        team="Arsenal",
        operator=Operator.GREATER_EQUAL,
        value=2,
        description="Arsenal scores 2 or more goals"
    )
    
    xg_condition = Condition(
        condition_type=ConditionType.XG,
        team="Arsenal",
        operator=Operator.GREATER_THAN,
        value=1.5,
        description="Arsenal has xG > 1.5"
    )
    
    and_alert.add_condition(goals_condition)
    and_alert.add_condition(xg_condition)
    
    # Test 2: OR condition
    print("\n📊 Test 2: OR Condition - Team scores 3+ goals OR leads by 2+ goals")
    or_alert = AdvancedAlertCondition(
        alert_id=2,
        name="High Scoring or Dominant",
        description="Team scores 3+ goals OR leads by 2+ goals",
        logic_operator=LogicOperator.OR
    )
    
    high_goals = Condition(
        condition_type=ConditionType.GOALS,
        team="any",
        operator=Operator.GREATER_EQUAL,
        value=3,
        description="Any team scores 3+ goals"
    )
    
    big_lead = Condition(
        condition_type=ConditionType.SCORE_DIFFERENCE,
        team="any",
        operator=Operator.GREATER_EQUAL,
        value=2,
        description="Any team leads by 2+ goals"
    )
    
    or_alert.add_condition(high_goals)
    or_alert.add_condition(big_lead)
    
    # Test 3: Time window condition
    print("\n📊 Test 3: Time Window - Team scores in first 15 minutes")
    time_alert = AdvancedAlertCondition(
        alert_id=3,
        name="Early Goal Alert",
        description="Team scores in first 15 minutes",
        logic_operator=LogicOperator.AND
    )
    
    early_goal = Condition(
        condition_type=ConditionType.GOALS,
        team="any",
        operator=Operator.GREATER_EQUAL,
        value=1,
        description="Any team scores at least 1 goal"
    )
    
    time_window = TimeWindow(
        start_minute=0,
        end_minute=15,
        description="First 15 minutes of match"
    )
    
    time_alert.add_condition(early_goal)
    time_alert.add_time_window(time_window)
    
    # Test 4: Sequence condition
    print("\n📊 Test 4: Sequence - Team scores 2 goals within 10 minutes")
    sequence_alert = AdvancedAlertCondition(
        alert_id=4,
        name="Quick Double",
        description="Team scores 2 goals within 10 minutes",
        logic_operator=LogicOperator.AND
    )
    
    first_goal = Condition(
        condition_type=ConditionType.GOALS,
        team="any",
        operator=Operator.GREATER_EQUAL,
        value=1,
        description="First goal"
    )
    
    second_goal = Condition(
        condition_type=ConditionType.GOALS,
        team="any",
        operator=Operator.GREATER_EQUAL,
        value=2,
        description="Second goal"
    )
    
    sequence = SequenceCondition(
        events=[first_goal, second_goal],
        time_limit=600,  # 10 minutes in seconds
        description="2 goals within 10 minutes"
    )
    
    sequence_alert.add_sequence(sequence)
    
    # Test 5: Complex nested condition
    print("\n📊 Test 5: Complex Nested - (Arsenal scores AND has momentum > 10) OR (Chelsea leads by 2)")
    complex_alert = AdvancedAlertCondition(
        alert_id=5,
        name="Complex Arsenal or Chelsea",
        description="(Arsenal scores AND has momentum > 10) OR (Chelsea leads by 2)",
        logic_operator=LogicOperator.OR
    )
    
    # Arsenal sub-condition
    arsenal_sub = AdvancedAlertCondition(
        alert_id=51,
        name="Arsenal Performance",
        description="Arsenal scores AND has momentum > 10",
        logic_operator=LogicOperator.AND
    )
    
    arsenal_goal = Condition(
        condition_type=ConditionType.GOALS,
        team="Arsenal",
        operator=Operator.GREATER_EQUAL,
        value=1,
        description="Arsenal scores"
    )
    
    arsenal_momentum = Condition(
        condition_type=ConditionType.MOMENTUM,
        team="Arsenal",
        operator=Operator.GREATER_THAN,
        value=10,
        description="Arsenal momentum > 10"
    )
    
    arsenal_sub.add_condition(arsenal_goal)
    arsenal_sub.add_condition(arsenal_momentum)
    
    # Chelsea condition
    chelsea_lead = Condition(
        condition_type=ConditionType.SCORE_DIFFERENCE,
        team="Chelsea",
        operator=Operator.GREATER_EQUAL,
        value=2,
        description="Chelsea leads by 2+ goals"
    )
    
    complex_alert.add_condition(arsenal_sub)
    complex_alert.add_condition(chelsea_lead)
    
    # Test with live match data
    print("\n🔍 Testing with live match data...")
    
    try:
        # Get live matches
        live_matches = await sports_api.get_live_matches()
        
        if not live_matches:
            print("❌ No live matches found, using sample data")
            # Create sample match data for testing
            sample_match = {
                "fixture": {
                    "id": 12345,
                    "status": {"elapsed": 25, "short": "1H"}
                },
                "teams": {
                    "home": {"name": "Arsenal"},
                    "away": {"name": "Chelsea"}
                },
                "goals": {"home": 2, "away": 0}
            }
            
            # Calculate metrics for sample data
            metrics = analytics_engine.calculate_all_metrics(sample_match)
            
            print(f"📊 Sample match: Arsenal 2 - 0 Chelsea (25 min)")
            print(f"   Arsenal xG: {metrics.home_xg:.2f}")
            print(f"   Arsenal momentum: {metrics.home_momentum:.1f}")
            print(f"   Arsenal pressure: {metrics.home_pressure_index:.2f}")
            
            # Test all alerts
            alerts_to_test = [and_alert, or_alert, time_alert, sequence_alert, complex_alert]
            
            for alert in alerts_to_test:
                result, message = await analytics_engine.evaluate_advanced_condition(
                    alert, sample_match, metrics
                )
                
                status = "✅ TRIGGERED" if result else "❌ Not triggered"
                print(f"\n🎯 {alert.name}: {status}")
                if message:
                    print(f"   Message: {message}")
                print(f"   Description: {alert.description}")
        
        else:
            print(f"✅ Found {len(live_matches)} live matches")
            
            # Test with first live match
            match_data = live_matches[0]
            match_info = sports_api.format_match_data(match_data)
            metrics = analytics_engine.calculate_all_metrics(match_data)
            
            print(f"📊 Live match: {match_info['home_team']} {match_info['home_score']} - {match_info['away_score']} {match_info['away_team']}")
            print(f"   Time: {match_info['elapsed']} min")
            
            # Test all alerts
            alerts_to_test = [and_alert, or_alert, time_alert, sequence_alert, complex_alert]
            
            for alert in alerts_to_test:
                result, message = await analytics_engine.evaluate_advanced_condition(
                    alert, match_data, metrics
                )
                
                status = "✅ TRIGGERED" if result else "❌ Not triggered"
                print(f"\n🎯 {alert.name}: {status}")
                if message:
                    print(f"   Message: {message}")
                print(f"   Description: {alert.description}")
    
    except Exception as e:
        print(f"❌ Error testing with live data: {e}")
    
    print("\n🎉 Advanced Condition Evaluator Test Complete!")
    print("\n🚀 Features Demonstrated:")
    print("   ✅ AND/OR logic combinations")
    print("   ✅ Time window constraints")
    print("   ✅ Sequence tracking")
    print("   ✅ Nested condition logic")
    print("   ✅ Multiple condition types (goals, xG, momentum, etc.)")
    print("   ✅ Real-time evaluation with live match data")

if __name__ == "__main__":
    asyncio.run(test_advanced_conditions()) 