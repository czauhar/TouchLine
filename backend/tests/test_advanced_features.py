#!/usr/bin/env python3
"""
TouchLine Advanced Features Test
Tests custom metrics, pattern recognition, and enhanced alert engine
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.alert_engine import match_monitor
from app.database import get_db, engine
from app.models import Base, Alert, User
from app.auth import AuthService
from app.services.custom_metrics import custom_metric_service, CustomMetric, MetricType
from app.services.pattern_recognition import pattern_recognition_service, PatternType, PatternSeverity

load_dotenv()

async def test_advanced_features():
    print("🚀 Testing TouchLine Advanced Features")
    print("=" * 60)
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = next(get_db())
    
    # Get or create test user
    test_user = db.query(User).filter(User.email == "test@touchline.com").first()
    if not test_user:
        hashed_password = AuthService.get_password_hash("testpass123")
        test_user = User(
            email="test@touchline.com",
            username="testuser_advanced",
            hashed_password=hashed_password,
            phone_number="+1234567890"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ Created test user: {test_user.email}")
    else:
        print(f"✅ Using existing test user: {test_user.email}")
    
    # Test 1: Custom Metrics
    print("\n📊 Testing Custom Metrics...")
    await test_custom_metrics(test_user.id)
    
    # Test 2: Pattern Recognition
    print("\n🎯 Testing Pattern Recognition...")
    await test_pattern_recognition()
    
    # Test 3: Enhanced Alert Engine
    print("\n🚨 Testing Enhanced Alert Engine...")
    await test_enhanced_alert_engine(test_user.id)
    
    # Test 4: Integration Test
    print("\n🔗 Testing Integration...")
    await test_integration()
    
    print("\n🎉 Advanced Features Test Completed Successfully!")
    print("=" * 60)

async def test_custom_metrics(user_id: int):
    """Test custom metrics functionality"""
    print("   Testing Custom Metric Creation...")
    
    # Create sample custom metrics
    metrics = [
        {
            "name": "Goal Efficiency",
            "description": "Goals per shot on target",
            "formula": "team_goals / max(team_shots_on_target, 1) * 100",
            "metric_type": MetricType.TEAM_BASED,
            "variables": {
                "team_goals": "Number of goals scored by team",
                "team_shots_on_target": "Number of shots on target by team"
            }
        },
        {
            "name": "Match Intensity",
            "description": "Overall match intensity based on goals and time",
            "formula": "(total_goals * 10 + match_elapsed / 90) / 2",
            "metric_type": MetricType.MATCH_BASED,
            "variables": {
                "total_goals": "Total goals in match",
                "match_elapsed": "Match elapsed time in minutes"
            }
        },
        {
            "name": "Pressure Index",
            "description": "Combined pressure and momentum",
            "formula": "(team_pressure + team_momentum) / 2",
            "metric_type": MetricType.TEAM_BASED,
            "variables": {
                "team_pressure": "Team pressure index",
                "team_momentum": "Team momentum index"
            }
        }
    ]
    
    created_metrics = []
    for metric_data in metrics:
        try:
            metric = custom_metric_service.create_metric(
                user_id=user_id,
                name=metric_data["name"],
                description=metric_data["description"],
                formula=metric_data["formula"],
                metric_type=metric_data["metric_type"],
                variables=metric_data["variables"]
            )
            created_metrics.append(metric)
            print(f"   ✅ Created metric: {metric.name}")
        except Exception as e:
            print(f"   ❌ Failed to create metric {metric_data['name']}: {e}")
    
    # Test metric evaluation
    print("   Testing Metric Evaluation...")
    from app.data_service import MatchData
    
    test_match = MatchData(
        external_id="12345",
        home_team="Test Home",
        away_team="Test Away",
        home_score=2,
        away_score=1,
        status="1H",
        elapsed_time=45,
        league="Test League",
        start_time=datetime.now(),
        home_shots_on_target=5,
        away_shots_on_target=3,
        home_pressure=75,
        away_pressure=45,
        home_momentum=65,
        away_momentum=35
    )
    
    # Evaluate metrics for home team
    home_metrics = custom_metric_service.evaluate_user_metrics(user_id, test_match, "Test Home")
    print(f"   📊 Home team metrics: {len(home_metrics)} evaluated")
    for metric_name, value in home_metrics.items():
        print(f"      • {metric_name}: {value:.2f}")
    
    print(f"   ✅ Custom metrics test completed: {len(created_metrics)} metrics created")

async def test_pattern_recognition():
    """Test pattern recognition functionality"""
    print("   Testing Pattern Detection...")
    
    # Configure pattern alerts
    pattern_recognition_service.configure_pattern_alert(
        PatternType.GOAL_SEQUENCE, 
        PatternSeverity.MEDIUM, 
        enabled=True
    )
    pattern_recognition_service.configure_pattern_alert(
        PatternType.MOMENTUM_SHIFT, 
        PatternSeverity.HIGH, 
        enabled=True
    )
    
    # Create test match data with patterns
    from app.data_service import MatchData
    
    # Simulate a match with rapid goals
    test_match = MatchData(
        external_id="67890",
        home_team="Pattern Home",
        away_team="Pattern Away",
        home_score=3,
        away_score=2,
        status="2H",
        elapsed_time=75,
        league="Pattern League",
        start_time=datetime.now(),
        home_yellow_cards=2,
        away_yellow_cards=1,
        home_pressure=80,
        away_pressure=60,
        home_momentum=70,
        away_momentum=30
    )
    
    # Analyze patterns
    patterns = pattern_recognition_service.analyze_match(test_match, "67890")
    print(f"   🎯 Detected {len(patterns)} patterns")
    
    for pattern in patterns:
        print(f"      • {pattern.name}: {pattern.description}")
        print(f"        Severity: {pattern.severity.value}, Confidence: {pattern.confidence:.1%}")
    
    # Test pattern filtering
    high_severity_patterns = pattern_recognition_service.get_high_severity_patterns()
    print(f"   🚨 High severity patterns: {len(high_severity_patterns)}")
    
    goal_sequences = pattern_recognition_service.get_patterns_by_type(PatternType.GOAL_SEQUENCE)
    print(f"   ⚽ Goal sequence patterns: {len(goal_sequences)}")
    
    print("   ✅ Pattern recognition test completed")

async def test_enhanced_alert_engine(user_id: int):
    """Test enhanced alert engine with advanced features"""
    print("   Testing Enhanced Alert Engine...")
    
    # Clear existing alerts
    db = next(get_db())
    db.query(Alert).delete()
    db.commit()
    
    # Create advanced alerts
    advanced_alerts = [
        {
            "user_id": user_id,
            "name": "High Intensity Match",
            "alert_type": "advanced",
            "team": "any",
            "condition": json.dumps({
                "description": "High scoring match with high pressure",
                "logic_operator": "AND",
                "conditions": [
                    {
                        "type": "goals",
                        "team": "any",
                        "operator": ">=",
                        "value": 3,
                        "description": "Total goals >= 3"
                    },
                    {
                        "type": "pressure",
                        "team": "any",
                        "operator": ">=",
                        "value": 70,
                        "description": "Pressure >= 70"
                    }
                ],
                "time_windows": [
                    {"start_minute": 0, "end_minute": 90}
                ]
            }),
            "threshold": 0.0,
            "is_active": True,
            "user_phone": "+1234567890"
        },
        {
            "user_id": user_id,
            "name": "Momentum Shift Alert",
            "alert_type": "momentum",
            "team": "any",
            "condition": "Alert when momentum shifts significantly",
            "threshold": 30.0,
            "is_active": True,
            "user_phone": "+1234567890"
        }
    ]
    
    print("   Creating advanced alerts...")
    for alert_data in advanced_alerts:
        alert = Alert(**alert_data)
        db.add(alert)
        print(f"      ✅ Created alert: {alert.name}")
    
    db.commit()
    
    # Test alert engine initialization
    await match_monitor.load_active_alerts()
    print(f"   📋 Loaded {len(match_monitor.alert_conditions)} active alerts")
    
    # Test single monitoring cycle
    print("   Running monitoring cycle...")
    await match_monitor.monitor_live_matches()
    print("   ✅ Monitoring cycle completed")
    
    print("   ✅ Enhanced alert engine test completed")

async def test_integration():
    """Test integration of all advanced features"""
    print("   Testing Feature Integration...")
    
    # Create a comprehensive test match
    from app.data_service import MatchData
    
    integration_match = MatchData(
        external_id="99999",
        home_team="Integration Home",
        away_team="Integration Away",
        home_score=4,
        away_score=3,
        status="2H",
        elapsed_time=85,
        league="Integration League",
        start_time=datetime.now(),
        home_shots_on_target=8,
        away_shots_on_target=5,
        home_pressure=85,
        away_pressure=65,
        home_momentum=75,
        away_momentum=25,
        home_yellow_cards=3,
        away_yellow_cards=2
    )
    
    # Test complete analysis
    print("   Running complete analysis...")
    
    # 1. Pattern recognition
    patterns = pattern_recognition_service.analyze_match(integration_match, "99999")
    print(f"      🎯 Patterns detected: {len(patterns)}")
    
    # 2. Custom metrics
    custom_metrics = custom_metric_service.evaluate_user_metrics(1, integration_match, "Integration Home")
    print(f"      📊 Custom metrics evaluated: {len(custom_metrics)}")
    
    # 3. Alert evaluation
    await match_monitor.evaluate_match_alerts(99999, integration_match)
    print("      🚨 Alert evaluation completed")
    
    # 4. Advanced features analysis
    await match_monitor.analyze_advanced_features(99999, integration_match)
    print("      🔬 Advanced features analysis completed")
    
    print("   ✅ Integration test completed")

if __name__ == "__main__":
    print("🧪 TouchLine Advanced Features Test Suite")
    print("=" * 60)
    
    async def run_tests():
        try:
            await test_advanced_features()
            print("\n🎉 All advanced features tests passed!")
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(run_tests()) 