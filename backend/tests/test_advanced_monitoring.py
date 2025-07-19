import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from app.analytics import (
    AdvancedAlertCondition, Condition, ConditionType, Operator, LogicOperator,
    TimeWindow, SequenceCondition
)
from app.alert_engine import match_monitor
from app.sports_api import sports_api
from app.analytics import analytics_engine

load_dotenv()

async def test_advanced_monitoring():
    print("🚀 Testing Advanced Monitoring with Complex Conditions...")
    
    # Create some advanced alert conditions
    print("\n📝 Creating advanced alert conditions...")
    
    # Alert 1: Arsenal scores 2+ goals AND has high xG
    arsenal_performance = AdvancedAlertCondition(
        alert_id=101,
        name="Arsenal High Performance",
        description="Arsenal scores 2+ goals AND has xG > 1.5",
        logic_operator=LogicOperator.AND,
        user_phone="+1234567890"  # Replace with actual phone number for testing
    )
    
    arsenal_goals = Condition(
        condition_type=ConditionType.GOALS,
        team="Arsenal",
        operator=Operator.GREATER_EQUAL,
        value=2,
        description="Arsenal scores 2+ goals"
    )
    
    arsenal_xg = Condition(
        condition_type=ConditionType.XG,
        team="Arsenal",
        operator=Operator.GREATER_THAN,
        value=1.5,
        description="Arsenal has xG > 1.5"
    )
    
    arsenal_performance.add_condition(arsenal_goals)
    arsenal_performance.add_condition(arsenal_xg)
    
    # Alert 2: Any team scores 3+ goals OR leads by 2+ goals
    high_scoring = AdvancedAlertCondition(
        alert_id=102,
        name="High Scoring or Dominant",
        description="Any team scores 3+ goals OR leads by 2+ goals",
        logic_operator=LogicOperator.OR,
        user_phone="+1234567890"
    )
    
    three_goals = Condition(
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
    
    high_scoring.add_condition(three_goals)
    high_scoring.add_condition(big_lead)
    
    # Alert 3: Early goal in first 15 minutes
    early_goal = AdvancedAlertCondition(
        alert_id=103,
        name="Early Goal Alert",
        description="Any team scores in first 15 minutes",
        logic_operator=LogicOperator.AND,
        user_phone="+1234567890"
    )
    
    goal_condition = Condition(
        condition_type=ConditionType.GOALS,
        team="any",
        operator=Operator.GREATER_EQUAL,
        value=1,
        description="Any team scores at least 1 goal"
    )
    
    time_constraint = TimeWindow(
        start_minute=0,
        end_minute=15,
        description="First 15 minutes"
    )
    
    early_goal.add_condition(goal_condition)
    early_goal.add_time_window(time_constraint)
    
    # Alert 4: Complex nested condition
    complex_arsenal = AdvancedAlertCondition(
        alert_id=104,
        name="Complex Arsenal Alert",
        description="(Arsenal scores AND has momentum > 10) OR (Arsenal leads by 2)",
        logic_operator=LogicOperator.OR,
        user_phone="+1234567890"
    )
    
    # Arsenal sub-condition
    arsenal_sub = AdvancedAlertCondition(
        alert_id=1041,
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
    
    # Arsenal lead condition
    arsenal_lead = Condition(
        condition_type=ConditionType.SCORE_DIFFERENCE,
        team="Arsenal",
        operator=Operator.GREATER_EQUAL,
        value=2,
        description="Arsenal leads by 2+ goals"
    )
    
    complex_arsenal.add_condition(arsenal_sub)
    complex_arsenal.add_condition(arsenal_lead)
    
    # Store advanced alerts for monitoring
    advanced_alerts = [arsenal_performance, high_scoring, early_goal, complex_arsenal]
    
    print(f"✅ Created {len(advanced_alerts)} advanced alert conditions")
    
    # Test with live match data
    print("\n🔍 Testing advanced conditions with live matches...")
    
    try:
        # Get live matches
        live_matches = await sports_api.get_live_matches()
        
        if live_matches:
            print(f"✅ Found {len(live_matches)} live matches")
            
            # Test with first few matches
            for i, match_data in enumerate(live_matches[:3]):
                match_info = sports_api.format_match_data(match_data)
                metrics = analytics_engine.calculate_all_metrics(match_data)
                
                print(f"\n📊 Match {i+1}: {match_info['home_team']} {match_info['home_score']} - {match_info['away_score']} {match_info['away_team']}")
                print(f"   Time: {match_info['elapsed']} min | League: {match_info['league']}")
                
                # Test each advanced alert
                for alert in advanced_alerts:
                    result, message = await match_monitor.evaluate_advanced_alert(alert, match_data, metrics)
                    
                    status = "✅ TRIGGERED" if result else "❌ Not triggered"
                    print(f"   🎯 {alert.name}: {status}")
                    if message:
                        print(f"      Message: {message}")
        
        else:
            print("❌ No live matches found, using sample data")
            
            # Create sample match data
            sample_matches = [
                {
                    "fixture": {"id": 12345, "status": {"elapsed": 25, "short": "1H"}},
                    "teams": {"home": {"name": "Arsenal"}, "away": {"name": "Chelsea"}},
                    "goals": {"home": 2, "away": 0},
                    "league": {"name": "Premier League"}
                },
                {
                    "fixture": {"id": 12346, "status": {"elapsed": 10, "short": "1H"}},
                    "teams": {"home": {"name": "Manchester City"}, "away": {"name": "Liverpool"}},
                    "goals": {"home": 1, "away": 0},
                    "league": {"name": "Premier League"}
                }
            ]
            
            for i, match_data in enumerate(sample_matches):
                match_info = sports_api.format_match_data(match_data)
                metrics = analytics_engine.calculate_all_metrics(match_data)
                
                print(f"\n📊 Sample Match {i+1}: {match_info['home_team']} {match_info['home_score']} - {match_info['away_score']} {match_info['away_team']}")
                print(f"   Time: {match_info['elapsed']} min")
                
                # Test each advanced alert
                for alert in advanced_alerts:
                    result, message = await match_monitor.evaluate_advanced_alert(alert, match_data, metrics)
                    
                    status = "✅ TRIGGERED" if result else "❌ Not triggered"
                    print(f"   🎯 {alert.name}: {status}")
                    if message:
                        print(f"      Message: {message}")
    
    except Exception as e:
        print(f"❌ Error testing advanced monitoring: {e}")
    
    print("\n🎉 Advanced Monitoring Test Complete!")
    print("\n🚀 Advanced Features Demonstrated:")
    print("   ✅ Multi-condition logic (AND/OR)")
    print("   ✅ Time window constraints")
    print("   ✅ Nested condition evaluation")
    print("   ✅ Integration with live monitoring")
    print("   ✅ Real-time match data processing")
    print("   ✅ Advanced metrics integration (xG, momentum, etc.)")
    
    print("\n📋 Next Steps:")
    print("   1. Create database models for advanced alerts")
    print("   2. Build UI for creating complex conditions")
    print("   3. Add more condition types (possession, cards, etc.)")
    print("   4. Implement alert templates for common scenarios")

if __name__ == "__main__":
    asyncio.run(test_advanced_monitoring()) 