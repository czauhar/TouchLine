#!/usr/bin/env python3
"""
Test script for Error Handling and Fallback Mechanisms
Tests validation, error handling, and fallback mechanisms
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json

from app.core.exceptions import (
    SportsAPIError, AlertEvaluationError, PlayerDataError, MatchDataError,
    WebSocketError, DatabaseError, ValidationError, ConfigurationError,
    RateLimitError, CacheError
)
from app.utils.validation import DataValidator
from app.utils.fallback import FallbackManager


class TestCustomExceptions:
    """Test custom exception classes"""

    def test_sports_api_error(self):
        """Test SportsAPIError with context"""
        error = SportsAPIError("API rate limit exceeded", operation="get_matches", status_code=429)
        assert str(error) == "Sports API Error: API rate limit exceeded"
        assert error.operation == "get_matches"
        assert error.status_code == 429

    def test_alert_evaluation_error(self):
        """Test AlertEvaluationError with alert context"""
        error = AlertEvaluationError("Invalid condition", alert_id=123, condition="goals > 5")
        assert str(error) == "Alert Evaluation Error: Invalid condition"
        assert error.alert_id == 123
        assert error.condition == "goals > 5"

    def test_player_data_error(self):
        """Test PlayerDataError with player context"""
        error = PlayerDataError("Player not found", player_id=456, player_name="John Doe")
        assert str(error) == "Player Data Error: Player not found"
        assert error.player_id == 456
        assert error.player_name == "John Doe"

    def test_validation_error(self):
        """Test ValidationError with field context"""
        error = ValidationError("Invalid email format", field="email", value="invalid-email")
        assert str(error) == "Validation Error: Invalid email format"
        assert error.field == "email"
        assert error.value == "invalid-email"

    def test_rate_limit_error(self):
        """Test RateLimitError with retry information"""
        error = RateLimitError("Too many requests", retry_after=60, endpoint="/matches")
        assert str(error) == "Rate Limit Error: Too many requests"
        assert error.retry_after == 60
        assert error.endpoint == "/matches"


class TestDataValidator:
    """Test validation utility methods"""

    def test_validate_required_fields(self):
        """Test required field validation"""
        data = {"name": "John", "email": "john@example.com"}
        required = ["name", "email"]
        
        # Should not raise exception
        DataValidator.validate_required_fields(data, required)
        
        # Should raise ValidationError for missing field
        with pytest.raises(ValidationError) as exc_info:
            DataValidator.validate_required_fields(data, ["name", "email", "phone"])
        assert "phone" in str(exc_info.value)

    def test_validate_string_field(self):
        """Test string field validation"""
        # Valid string
        DataValidator.validate_string_field("John Doe", "name", min_length=1, max_length=50)
        
        # Invalid: too short
        with pytest.raises(ValidationError) as exc_info:
            DataValidator.validate_string_field("", "name", min_length=1)
        assert "name" in str(exc_info.value)
        
        # Invalid: too long
        with pytest.raises(ValidationError) as exc_info:
            DataValidator.validate_string_field("A" * 101, "description", max_length=100)
        assert "description" in str(exc_info.value)

    def test_validate_integer_field(self):
        """Test integer field validation"""
        # Valid integer
        DataValidator.validate_integer_field(25, "age", min_value=0, max_value=120)
        
        # Invalid: below minimum
        with pytest.raises(ValidationError) as exc_info:
            DataValidator.validate_integer_field(-1, "age", min_value=0)
        assert "age" in str(exc_info.value)
        
        # Invalid: above maximum
        with pytest.raises(ValidationError) as exc_info:
            DataValidator.validate_integer_field(150, "age", max_value=120)
        assert "age" in str(exc_info.value)

    def test_validate_email(self):
        """Test email validation"""
        # Valid emails
        DataValidator.validate_email("john@example.com")
        DataValidator.validate_email("user.name+tag@domain.co.uk")
        
        # Invalid emails
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user.domain.com",
            ""
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                DataValidator.validate_email(email)

    def test_validate_phone_number(self):
        """Test phone number validation"""
        # Valid phone numbers
        assert DataValidator.validate_phone_number("1234567890") == "+11234567890"
        assert DataValidator.validate_phone_number("+1234567890") == "+1234567890"
        
        # Invalid phone numbers
        invalid_phones = ["123", "12345678901234567890", ""]
        
        for phone in invalid_phones:
            with pytest.raises(ValidationError):
                DataValidator.validate_phone_number(phone)

    def test_validate_team_name(self):
        """Test team name validation"""
        # Valid team names
        DataValidator.validate_team_name("Manchester United")
        DataValidator.validate_team_name("Real Madrid")
        
        # Invalid team names
        invalid_names = ["", "A", "A" * 101]
        
        for name in invalid_names:
            with pytest.raises(ValidationError):
                DataValidator.validate_team_name(name)

    def test_validate_player_name(self):
        """Test player name validation"""
        # Valid player names
        DataValidator.validate_player_name("Lionel Messi")
        DataValidator.validate_player_name("Cristiano Ronaldo")
        
        # Invalid player names
        invalid_names = ["", "A", "A" * 101]
        
        for name in invalid_names:
            with pytest.raises(ValidationError):
                DataValidator.validate_player_name(name)

    def test_validate_match_data(self):
        """Test match data validation"""
        # Valid match data
        valid_match = {
            "fixture": {"id": 123},
            "teams": {
                "home": {"name": "Manchester United"},
                "away": {"name": "Liverpool"}
            },
            "goals": {"home": 2, "away": 1},
            "league": {"name": "Premier League"}
        }
        DataValidator.validate_match_data(valid_match)
    
        # Invalid match data
        invalid_match = {
            "fixture": {"id": "not_an_integer"},
            "teams": {
                "home": {"name": ""},
                "away": {"name": "Liverpool"}
            },
            "goals": {"home": -1, "away": 1},
            "league": {"name": "Premier League"}
        }
    
        with pytest.raises(ValidationError) as exc_info:
            DataValidator.validate_match_data(invalid_match)
        assert "fixture.id" in str(exc_info.value)

    def test_validate_alert_condition(self):
        """Test alert condition validation"""
        # Valid condition
        valid_condition = {
            "alert_type": "goals",
            "team": "Manchester United",
            "threshold": 2.5
        }
        DataValidator.validate_alert_condition(valid_condition)
    
        # Invalid condition
        invalid_condition = {
            "alert_type": "invalid_type",
            "team": "Manchester United",
            "threshold": -10
        }
    
        with pytest.raises(ValidationError) as exc_info:
            DataValidator.validate_alert_condition(invalid_condition)
        assert "alert_type" in str(exc_info.value)

    def test_sanitize_html(self):
        """Test HTML sanitization"""
        dirty_html = "<script>alert('xss')</script><b>Hello</b> World"
        clean = DataValidator.sanitize_html(dirty_html)
        
        assert "<script>" not in clean
        assert "Hello" in clean
        assert "<b>" in clean  # Safe HTML should remain

    def test_validate_date_range(self):
        """Test date range validation"""
        # Valid date range
        start_date = "2023-01-01T00:00:00Z"
        end_date = "2023-01-02T00:00:00Z"
        
        result = DataValidator.validate_date_range(start_date, end_date)
        assert result == (start_date, end_date)
        
        # Invalid date range (end before start)
        with pytest.raises(ValidationError):
            DataValidator.validate_date_range(end_date, start_date)
        
        # Invalid date range (too long)
        long_end = "2023-02-01T00:00:00Z"
        with pytest.raises(ValidationError):
            DataValidator.validate_date_range(start_date, long_end, max_days=30)


class TestFallbackManager:
    """Test fallback mechanism functionality"""

    @pytest.fixture
    def fallback_manager(self):
        """Create a FallbackManager instance for testing"""
        return FallbackManager()

    @pytest.fixture
    def mock_api_client(self):
        """Mock API client for testing"""
        return Mock()

    @pytest.mark.asyncio
    async def test_retry_api_call_success(self, fallback_manager, mock_api_client):
        """Test successful API call with retries"""
        async def mock_get_match(match_id, **kwargs):
            return {"match_id": 123, "status": "live"}
        
        mock_api_client.get_match = mock_get_match
        
        result = await fallback_manager._retry_api_call(
            mock_api_client.get_match, 
            123  # match_id as positional argument
        )
        
        assert result == {"match_id": 123, "status": "live"}

    @pytest.mark.asyncio
    async def test_retry_api_call_failure(self, fallback_manager, mock_api_client):
        """Test API call failure with retries"""
        call_count = 0
        
        async def mock_get_match_fail(match_id, **kwargs):
            nonlocal call_count
            call_count += 1
            raise SportsAPIError("API Error")
        
        mock_api_client.get_match = mock_get_match_fail
        
        with pytest.raises(SportsAPIError):
            await fallback_manager._retry_api_call(
                mock_api_client.get_match,
                123  # match_id as positional argument
            )
        
        # Should have been called 3 times (initial + 2 retries)
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_api_call_partial_success(self, fallback_manager, mock_api_client):
        """Test API call that succeeds after some failures"""
        call_count = 0
        
        async def mock_get_match_partial(match_id, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise SportsAPIError("API Error")
            elif call_count == 2:
                raise SportsAPIError("API Error")
            else:
                return {"match_id": 123, "status": "live"}
        
        mock_api_client.get_match = mock_get_match_partial
        
        result = await fallback_manager._retry_api_call(
            mock_api_client.get_match,
            123  # match_id as positional argument
        )
        
        assert result == {"match_id": 123, "status": "live"}
        assert call_count == 3

    def test_get_from_cache(self, fallback_manager):
        """Test cache retrieval"""
        # Mock cache data
        cache_data = {
            "match_id": 123,
            "home_team": "Manchester United",
            "away_team": "Liverpool",
            "timestamp": datetime.now().isoformat()
        }
        
        # Test cache hit
        with patch('app.utils.fallback.get_db') as mock_get_db:
            mock_db = Mock()
            mock_cache_entry = Mock()
            mock_cache_entry.match_data = cache_data
            mock_cache_entry.is_expired = False
            mock_db.query.return_value.filter.return_value.first.return_value = mock_cache_entry
            mock_get_db.return_value = iter([mock_db])
            
            result = asyncio.run(fallback_manager._get_from_cache(123))
            assert result == cache_data
        
        # Test cache miss
        with patch('app.utils.fallback.get_db') as mock_get_db:
            mock_db = Mock()
            mock_db.query.return_value.filter.return_value.first.return_value = None
            mock_get_db.return_value = iter([mock_db])
            
            result = asyncio.run(fallback_manager._get_from_cache(123))
            assert result is None

    def test_update_cache(self, fallback_manager):
        """Test cache update"""
        match_data = {
            "match_id": 123,
            "home_team": "Manchester United",
            "away_team": "Liverpool",
            "timestamp": datetime.now().isoformat()
        }
        
        with patch('app.utils.fallback.get_db') as mock_get_db:
            mock_db = Mock()
            mock_cache_entry = Mock()
            mock_db.query.return_value.filter.return_value.first.return_value = mock_cache_entry
            mock_get_db.return_value = iter([mock_db])
            
            asyncio.run(fallback_manager._update_cache(123, match_data))
            mock_db.commit.assert_called_once()

    def test_create_fallback_match_data(self, fallback_manager):
        """Test fallback match data creation"""
        match_id = 123
        
        result = fallback_manager._create_fallback_match_data(match_id)
        
        assert result["fixture"]["id"] == match_id
        assert result["status"] == "unknown"
        assert result["home_score"] == 0
        assert result["away_score"] == 0
        assert "timestamp" in result
        assert result["is_fallback"] is True

    @patch('app.utils.fallback.FallbackManager._retry_api_call')
    @patch('app.utils.fallback.FallbackManager._get_from_cache')
    @patch('app.utils.fallback.FallbackManager._update_cache')
    def test_get_match_data_with_fallback_success(self, mock_update_cache, mock_get_cache, mock_retry, fallback_manager, mock_api_client):
        """Test successful match data retrieval with fallback"""
        match_data = {
            "match_id": 123,
            "home_team": "Manchester United",
            "away_team": "Liverpool",
            "home_score": 2,
            "away_score": 1,
            "status": "live"
        }
        
        mock_retry.return_value = match_data
        mock_get_cache.return_value = None
        
        result = fallback_manager.get_match_data_with_fallback(mock_api_client.get_match, 123)
        
        assert result == match_data
        mock_retry.assert_called_once()
        mock_update_cache.assert_called_once_with(123, match_data)

    @patch('app.utils.fallback.FallbackManager._retry_api_call')
    @patch('app.utils.fallback.FallbackManager._get_from_cache')
    @patch('app.utils.fallback.FallbackManager._update_cache')
    def test_get_match_data_with_fallback_cache_fallback(self, mock_update_cache, mock_get_cache, mock_retry, fallback_manager, mock_api_client):
        """Test match data retrieval falling back to cache"""
        cache_data = {
            "match_id": 123,
            "home_team": "Manchester United",
            "away_team": "Liverpool",
            "home_score": 1,
            "away_score": 1,
            "status": "live",
            "cached_at": datetime.now().isoformat()
        }
        
        mock_retry.side_effect = SportsAPIError("API Error")
        mock_get_cache.return_value = cache_data
        
        result = fallback_manager.get_match_data_with_fallback(mock_api_client.get_match, 123)
        
        assert result == cache_data
        assert result["is_cached"] is True

    @patch('app.utils.fallback.FallbackManager._retry_api_call')
    @patch('app.utils.fallback.FallbackManager._get_from_cache')
    def test_get_match_data_with_fallback_minimal_data(self, mock_get_cache, mock_retry, fallback_manager, mock_api_client):
        """Test match data retrieval falling back to minimal data"""
        mock_retry.side_effect = SportsAPIError("API Error")
        mock_get_cache.return_value = None
        
        result = fallback_manager.get_match_data_with_fallback(mock_api_client.get_match, 123)
        
        assert result["match_id"] == 123
        assert result["status"] == "unknown"
        assert result["is_fallback"] is True

    def test_validate_and_repair_match_data(self, fallback_manager):
        """Test match data validation and repair"""
        # Valid match data
        valid_data = {
            "fixture": {"id": 123},
            "teams": {
                "home": {"name": "Manchester United"},
                "away": {"name": "Liverpool"}
            },
            "goals": {"home": 2, "away": 1},
            "league": {"name": "Premier League"}
        }
        
        result = fallback_manager.validate_and_repair_match_data(valid_data)
        assert result == valid_data
        
        # Invalid match data that can be repaired
        invalid_data = {
            "fixture": {"id": "123"},  # String instead of int
            "teams": {
                "home": {"name": ""},  # Empty string
                "away": {"name": "Liverpool"}
            },
            "goals": {"home": -1, "away": 1},  # Negative score
            "league": {"name": "Premier League"}
        }
        
        result = fallback_manager.validate_and_repair_match_data(invalid_data)
        
        assert result["fixture"]["id"] == 123  # Converted to int
        assert result["teams"]["home"]["name"] == "Unknown Team"  # Default value
        assert result["goals"]["home"] == 0  # Fixed negative score

    def test_get_player_stats_with_fallback(self, fallback_manager):
        """Test player stats retrieval with fallback"""
        # Mock player data
        player_data = {
            "player_id": 456,
            "player_name": "Lionel Messi",
            "team": "Barcelona",
            "goals": 2,
            "assists": 1,
            "minutes": 90
        }
        
        with patch.object(fallback_manager, '_extract_player_stats_from_events', return_value=player_data):
            result = fallback_manager.get_player_stats_with_fallback([], 456)
            assert result == player_data
        
        # Test fallback when extraction fails
        with patch.object(fallback_manager, '_extract_player_stats_from_events', return_value=None):
            result = fallback_manager.get_player_stats_with_fallback([], 456)
            assert result["player_id"] == 456
            assert result["player_name"] == "Unknown Player"
            assert result["is_fallback"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 