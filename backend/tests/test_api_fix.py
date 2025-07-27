#!/usr/bin/env python3
"""
Test script to debug API-Football connection
"""

import pytest
import asyncio
import httpx
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

@pytest.mark.asyncio
async def test_api_connection():
    """Test different API endpoints to debug the connection"""
    api_key = os.getenv("API_FOOTBALL_KEY")
    base_url = "https://v3.football.api-sports.io"
    headers = {
        "x-apisports-key": api_key
    }
    
    print(f"🔑 API Key: {api_key[:10]}..." if api_key else "❌ No API key found")
    print(f"🌐 Base URL: {base_url}")
    
    async with httpx.AsyncClient() as client:
        # Test 1: Status endpoint
        print("\n📊 Test 1: API Status...")
        try:
            response = await client.get(f"{base_url}/status", headers=headers)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Status: {data}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Connection error: {e}")
        
        # Test 2: Leagues endpoint
        print("\n🏆 Test 2: Get Leagues...")
        try:
            response = await client.get(f"{base_url}/leagues", headers=headers, params={"country": "England"})
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                leagues = data.get("response", [])
                print(f"✅ Found {len(leagues)} leagues")
                if leagues:
                    print(f"   Sample: {leagues[0].get('league', {}).get('name', 'Unknown')}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Connection error: {e}")
        
        # Test 3: Fixtures with different parameters
        print("\n⚽ Test 3: Get Fixtures...")
        
        # Try different date ranges
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        dates_to_try = [
            today.strftime("%Y-%m-%d"),
            yesterday.strftime("%Y-%m-%d"),
            tomorrow.strftime("%Y-%m-%d")
        ]
        
        for date in dates_to_try:
            print(f"\n   Trying date: {date}")
            try:
                response = await client.get(
                    f"{base_url}/fixtures",
                    headers=headers,
                    params={"date": date}
                )
                print(f"   Status Code: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    fixtures = data.get("response", [])
                    print(f"   ✅ Found {len(fixtures)} fixtures")
                    if fixtures:
                        fixture = fixtures[0]
                        home = fixture.get("teams", {}).get("home", {}).get("name", "Unknown")
                        away = fixture.get("teams", {}).get("away", {}).get("name", "Unknown")
                        print(f"   Sample: {home} vs {away}")
                        break
                else:
                    print(f"   ❌ Error: {response.text[:200]}...")
            except Exception as e:
                print(f"   ❌ Connection error: {e}")
        
        # Test 4: Live matches
        print("\n🔥 Test 4: Live Matches...")
        try:
            response = await client.get(f"{base_url}/fixtures", headers=headers, params={"live": "all"})
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                live_matches = data.get("response", [])
                print(f"✅ Found {len(live_matches)} live matches")
                if live_matches:
                    match = live_matches[0]
                    home = match.get("teams", {}).get("home", {}).get("name", "Unknown")
                    away = match.get("teams", {}).get("away", {}).get("name", "Unknown")
                    print(f"   Sample: {home} vs {away}")
            else:
                print(f"❌ Error: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_connection()) 