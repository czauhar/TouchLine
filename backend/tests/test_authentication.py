#!/usr/bin/env python3
"""
TouchLine Authentication Test Suite
Tests the complete authentication flow and user management
"""

import pytest
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

class TestAuthentication:
    """Test authentication endpoints and user management"""
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        user_data = {
            "email": f"testuser_{datetime.now().timestamp()}@example.com",
            "password": "password123",
            "username": f"testuser_{datetime.now().timestamp()}",
            "phone_number": "+1234567890"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["username"] == user_data["username"]
        
        return data["access_token"], user_data["email"], user_data["password"]
    
    def test_user_login(self):
        """Test user login endpoint"""
        # First register a user
        token, email, password = self.test_user_registration()
        
        # Then test login
        login_data = {
            "email": email,
            "password": password
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == email
        
        return data["access_token"]
    
    def test_authenticated_endpoints(self):
        """Test that authenticated endpoints work with valid token"""
        token = self.test_user_login()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test alerts endpoint
        response = requests.get(f"{BASE_URL}/api/alerts", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "alerts" in data
        assert isinstance(data["alerts"], list)
        
        # Test user profile endpoint
        response = requests.get(f"{BASE_URL}/api/user/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "email" in data
        assert "username" in data
    
    def test_unauthenticated_access(self):
        """Test that protected endpoints reject unauthenticated requests"""
        # Test alerts endpoint without token
        response = requests.get(f"{BASE_URL}/api/alerts")
        assert response.status_code == 401
        
        # Test with invalid token
        headers = {
            "Authorization": "Bearer invalid_token",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{BASE_URL}/api/alerts", headers=headers)
        assert response.status_code == 401
    
    def test_duplicate_registration(self):
        """Test that duplicate email registration is rejected"""
        user_data = {
            "email": f"duplicate_{datetime.now().timestamp()}@example.com",
            "password": "password123",
            "username": f"duplicate_{datetime.now().timestamp()}",
            "phone_number": "+1234567890"
        }
        
        # First registration should succeed
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Second registration with same email should fail
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        assert response.status_code == 401

class TestSystemHealth:
    """Test system health and status endpoints"""
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "unhealthy", "degraded"]
    
    def test_status_endpoint(self):
        """Test system status endpoint"""
        response = requests.get(f"{BASE_URL}/api/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "backend" in data
        assert "database" in data
        assert "sports_api" in data
        assert "alert_engine" in data

class TestAPIEndpoints:
    """Test various API endpoints"""
    
    def test_matches_endpoints(self):
        """Test matches endpoints"""
        # Test live matches
        response = requests.get(f"{BASE_URL}/api/matches/live")
        assert response.status_code == 200
        
        data = response.json()
        assert "matches" in data
        assert isinstance(data["matches"], list)
        
        # Test today's matches
        response = requests.get(f"{BASE_URL}/api/matches/today")
        assert response.status_code == 200
        
        data = response.json()
        assert "matches" in data
        assert isinstance(data["matches"], list)
    
    def test_alert_templates(self):
        """Test alert templates endpoint"""
        response = requests.get(f"{BASE_URL}/api/alerts/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert "templates" in data
        assert isinstance(data["templates"], list)

def run_tests():
    """Run all tests and report results"""
    print("🧪 Running TouchLine Authentication Tests\n")
    
    test_classes = [TestAuthentication, TestSystemHealth, TestAPIEndpoints]
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"📋 Testing {test_class.__name__}...")
        test_instance = test_class()
        
        for method_name in dir(test_instance):
            if method_name.startswith('test_'):
                total_tests += 1
                try:
                    method = getattr(test_instance, method_name)
                    method()
                    print(f"  ✅ {method_name}")
                    passed_tests += 1
                except Exception as e:
                    print(f"  ❌ {method_name}: {str(e)}")
        
        print()
    
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Authentication system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the authentication system.")
        return False

if __name__ == "__main__":
    run_tests() 