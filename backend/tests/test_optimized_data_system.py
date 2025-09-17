#!/usr/bin/env python3
"""
TouchLine Optimized Data System Test
Tests intelligent caching, API call optimization, and comprehensive data flow
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.data_service import data_service, MatchData
from app.database import get_db, engine
from app.models import Base, MatchCache
from app.sports_api import sports_api

load_dotenv()

async def test_optimized_data_system():
    print("🚀 Testing TouchLine Optimized Data System")
    print("=" * 60)
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Test 1: Intelligent Caching Strategy
    print("\n📋 Testing Intelligent Caching Strategy...")
    await test_intelligent_caching()
    
    # Test 2: API Call Optimization
    print("\n⚡ Testing API Call Optimization...")
    await test_api_call_optimization()
    
    # Test 3: Tiered Data Fetching
    print("\n🎯 Testing Tiered Data Fetching...")
    await test_tiered_data_fetching()
    
    # Test 4: Comprehensive Data Flow
    print("\n🔄 Testing Comprehensive Data Flow...")
    await test_comprehensive_data_flow()
    
    # Test 5: Performance Metrics
    print("\n📊 Testing Performance Metrics...")
    await test_performance_metrics()
    
    print("\n🎉 Optimized Data System Test Completed Successfully!")
    print("=" * 60)

async def test_intelligent_caching():
    """Test intelligent caching with different TTLs"""
    print("   Testing Cache TTL Strategy...")
    
    # Test different match statuses
    test_matches = [
        {
            "fixture": {"id": 12345, "status": {"short": "1H", "elapsed": 30}},
            "teams": {"home": {"name": "Live Home"}, "away": {"name": "Live Away"}},
            "goals": {"home": 1, "away": 0},
            "league": {"name": "Live League"}
        },
        {
            "fixture": {"id": 12346, "status": {"short": "FT", "elapsed": 90}},
            "teams": {"home": {"name": "Finished Home"}, "away": {"name": "Finished Away"}},
            "goals": {"home": 2, "away": 1},
            "league": {"name": "Finished League"}
        },
        {
            "fixture": {"id": 12347, "status": {"short": "NS", "elapsed": 0}},
            "teams": {"home": {"name": "Scheduled Home"}, "away": {"name": "Scheduled Away"}},
            "goals": {"home": 0, "away": 0},
            "league": {"name": "Scheduled League"}
        }
    ]
    
    for i, match in enumerate(test_matches):
        # Test cache TTL determination
        cache_ttl = data_service._get_cache_ttl_for_match(match, is_live=(i == 0))
        detail_level = data_service._get_detail_level_for_match(match, is_live=(i == 0))
        
        print(f"      Match {i+1}: TTL={cache_ttl}s, Detail={detail_level}")
        
        # Verify TTL logic
        if i == 0:  # Live match
            assert cache_ttl == data_service.live_cache_ttl, f"Live match should have {data_service.live_cache_ttl}s TTL"
            assert detail_level == "full", "Live match should have full detail level"
        elif i == 1:  # Finished match
            assert cache_ttl == data_service.basic_cache_ttl, f"Finished match should have {data_service.basic_cache_ttl}s TTL"
            assert detail_level == "detailed", "Finished match should have detailed level"
        else:  # Scheduled match
            assert cache_ttl == data_service.basic_cache_ttl * 2, f"Scheduled match should have {data_service.basic_cache_ttl * 2}s TTL"
            assert detail_level == "basic", "Scheduled match should have basic level"
    
    print("   ✅ Intelligent caching strategy working correctly")

async def test_api_call_optimization():
    """Test API call optimization and rate limiting"""
    print("   Testing API Call Optimization...")
    
    # Test batch processing
    test_matches = [
        {
            "fixture": {"id": 20001, "status": {"short": "1H", "elapsed": 15}},
            "teams": {"home": {"name": "Batch Home 1"}, "away": {"name": "Batch Away 1"}},
            "goals": {"home": 0, "away": 0},
            "league": {"name": "Batch League"}
        },
        {
            "fixture": {"id": 20002, "status": {"short": "1H", "elapsed": 20}},
            "teams": {"home": {"name": "Batch Home 2"}, "away": {"name": "Batch Away 2"}},
            "goals": {"home": 1, "away": 0},
            "league": {"name": "Batch League"}
        }
    ]
    
    start_time = time.time()
    
    # Process batch with optimization
    batch_data = await data_service._process_match_batch_optimized(test_matches, is_live=True)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"      Processed {len(batch_data)} matches in {processing_time:.2f}s")
    print(f"      Average time per match: {processing_time/len(batch_data):.2f}s")
    
    # Verify rate limiting is working
    assert processing_time >= len(test_matches) * data_service.request_delay, "Rate limiting should add delay"
    
    print("   ✅ API call optimization working correctly")

async def test_tiered_data_fetching():
    """Test tiered data fetching based on match status"""
    print("   Testing Tiered Data Fetching...")
    
    test_match = {
        "fixture": {"id": 30001, "status": {"short": "1H", "elapsed": 25}},
        "teams": {"home": {"name": "Tiered Home"}, "away": {"name": "Tiered Away"}},
        "goals": {"home": 1, "away": 1},
        "league": {"name": "Tiered League"}
    }
    
    # Test basic data fetching (minimal API calls)
    basic_data = await data_service._fetch_basic_match_data(test_match)
    assert "alert_metrics" in basic_data, "Basic data should include alert metrics"
    assert basic_data["alert_metrics"]["possession"]["home"] == 50, "Basic data should have default possession"
    
    # Test detailed data fetching (moderate API calls)
    detailed_data = await data_service._fetch_detailed_match_data(test_match)
    assert "detailed_stats" in detailed_data, "Detailed data should include stats"
    assert "events" in detailed_data, "Detailed data should include events"
    
    # Test enhanced data fetching (full API calls)
    enhanced_data = await data_service._fetch_enhanced_match_data(test_match)
    assert "lineups" in enhanced_data, "Enhanced data should include lineups"
    
    print("   ✅ Tiered data fetching working correctly")

async def test_comprehensive_data_flow():
    """Test comprehensive data flow from API to frontend"""
    print("   Testing Comprehensive Data Flow...")
    
    # Test live matches flow
    print("      Testing live matches flow...")
    live_matches = await data_service.get_live_matches_efficient()
    print(f"      Retrieved {len(live_matches)} live matches")
    
    if live_matches:
        match_data = live_matches[0]
        print(f"      Sample match: {match_data.home_team} vs {match_data.away_team}")
        print(f"      Score: {match_data.home_score}-{match_data.away_score}")
        print(f"      Status: {match_data.status} ({match_data.elapsed_time}')")
        print(f"      Possession: {match_data.home_possession}% - {match_data.away_possession}%")
        print(f"      Shots: {match_data.home_shots} - {match_data.away_shots}")
        print(f"      Cards: {match_data.home_yellow_cards} - {match_data.away_yellow_cards}")
    
    # Test today's matches flow
    print("      Testing today's matches flow...")
    today_matches = await data_service.get_todays_matches_efficient()
    print(f"      Retrieved {len(today_matches)} today's matches")
    
    # Verify data structure
    for match in live_matches[:3]:  # Check first 3 matches
        assert hasattr(match, 'external_id'), "Match should have external_id"
        assert hasattr(match, 'home_team'), "Match should have home_team"
        assert hasattr(match, 'away_team'), "Match should have away_team"
        assert hasattr(match, 'home_score'), "Match should have home_score"
        assert hasattr(match, 'away_score'), "Match should have away_score"
        assert hasattr(match, 'home_possession'), "Match should have home_possession"
        assert hasattr(match, 'away_possession'), "Match should have away_possession"
    
    print("   ✅ Comprehensive data flow working correctly")

async def test_performance_metrics():
    """Test performance metrics and optimization results"""
    print("   Testing Performance Metrics...")
    
    # Test cache efficiency
    db = next(get_db())
    try:
        cache_entries = db.query(MatchCache).all()
        print(f"      Cache entries: {len(cache_entries)}")
        
        # Check cache hit rate simulation
        cache_hits = 0
        cache_misses = 0
        
        for entry in cache_entries:
            if not entry.is_expired:
                cache_hits += 1
            else:
                cache_misses += 1
        
        if cache_entries:
            hit_rate = cache_hits / len(cache_entries) * 100
            print(f"      Cache hit rate: {hit_rate:.1f}%")
            print(f"      Cache hits: {cache_hits}, misses: {cache_misses}")
        
    finally:
        db.close()
    
    # Test API call reduction
    print("      API call optimization metrics:")
    print(f"      - Max concurrent requests: {data_service.max_concurrent_requests}")
    print(f"      - Request delay: {data_service.request_delay}s")
    print(f"      - Batch size: {data_service.batch_size}")
    print(f"      - Live cache TTL: {data_service.live_cache_ttl}s")
    print(f"      - Basic cache TTL: {data_service.basic_cache_ttl}s")
    
    print("   ✅ Performance metrics calculated successfully")

async def test_data_quality():
    """Test data quality and completeness"""
    print("   Testing Data Quality...")
    
    # Get sample matches
    live_matches = await data_service.get_live_matches_efficient()
    today_matches = await data_service.get_todays_matches_efficient()
    
    all_matches = live_matches + today_matches
    
    if all_matches:
        # Check data completeness
        complete_matches = 0
        for match in all_matches:
            if (match.home_team and match.away_team and 
                match.home_score is not None and match.away_score is not None):
                complete_matches += 1
        
        completeness_rate = complete_matches / len(all_matches) * 100
        print(f"      Data completeness: {completeness_rate:.1f}%")
        
        # Check data freshness
        current_time = datetime.utcnow()
        fresh_matches = 0
        for match in all_matches:
            if hasattr(match, 'start_time'):
                time_diff = (current_time - match.start_time).total_seconds()
                if time_diff < 86400:  # Within 24 hours
                    fresh_matches += 1
        
        freshness_rate = fresh_matches / len(all_matches) * 100
        print(f"      Data freshness: {freshness_rate:.1f}%")
    
    print("   ✅ Data quality verified")

if __name__ == "__main__":
    print("🧪 TouchLine Optimized Data System Test Suite")
    print("=" * 60)
    
    async def run_tests():
        try:
            await test_optimized_data_system()
            print("\n🎉 All optimized data system tests passed!")
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(run_tests()) 