import pytest
import asyncio
from app.core import exceptions
from app.utils.validation import DataValidator
from app.utils.fallback import FallbackManager

# --- Custom Exception Tests ---
def test_sports_api_error():
    with pytest.raises(exceptions.SportsAPIError) as exc:
        raise exceptions.SportsAPIError(message="Internal Error", status_code=500, api_response={"error": "test"})
    assert "Internal Error" in str(exc.value)
    assert exc.value.status_code == 500

def test_alert_evaluation_error():
    with pytest.raises(exceptions.AlertEvaluationError) as exc:
        raise exceptions.AlertEvaluationError(alert_id=42, message="Invalid condition")
    assert exc.value.alert_id == 42

def test_validation_error():
    with pytest.raises(exceptions.ValidationError) as exc:
        raise exceptions.ValidationError(field="email", value="invalid", message="Invalid email")
    assert exc.value.field == "email"
    assert exc.value.value == "invalid"

def test_rate_limit_error():
    with pytest.raises(exceptions.RateLimitError) as exc:
        raise exceptions.RateLimitError(api_name="API-Football", retry_after=60)
    assert "API-Football" in str(exc.value)
    assert exc.value.retry_after == 60

# --- Validation Utility Tests ---
def test_validate_required_fields():
    data = {"a": 1, "b": 2}
    DataValidator.validate_required_fields(data, ["a", "b"])
    with pytest.raises(exceptions.ValidationError):
        DataValidator.validate_required_fields(data, ["a", "b", "c"])

def test_validate_string_field():
    assert DataValidator.validate_string_field("hello", "field") == "hello"
    with pytest.raises(exceptions.ValidationError):
        DataValidator.validate_string_field("", "field", min_length=1)
    with pytest.raises(exceptions.ValidationError):
        DataValidator.validate_string_field("a" * 101, "field", max_length=100)

def test_validate_integer_field():
    assert DataValidator.validate_integer_field(5, "field") == 5
    assert DataValidator.validate_integer_field("7", "field") == 7
    with pytest.raises(exceptions.ValidationError):
        DataValidator.validate_integer_field("abc", "field")
    with pytest.raises(exceptions.ValidationError):
        DataValidator.validate_integer_field(-1, "field", min_value=0)

def test_validate_float_field():
    assert DataValidator.validate_float_field(5.5, "field") == 5.5
    assert DataValidator.validate_float_field("7.2", "field") == 7.2
    with pytest.raises(exceptions.ValidationError):
        DataValidator.validate_float_field("abc", "field")

def test_validate_boolean_field():
    assert DataValidator.validate_boolean_field(True, "field") is True
    assert DataValidator.validate_boolean_field("true", "field") is True
    assert DataValidator.validate_boolean_field("false", "field") is False
    with pytest.raises(exceptions.ValidationError):
        DataValidator.validate_boolean_field("invalid", "field")

def test_validate_email():
    assert DataValidator.validate_email("test@example.com") == "test@example.com"
    with pytest.raises(exceptions.ValidationError):
        DataValidator.validate_email("invalid-email")

def test_validate_phone_number():
    assert DataValidator.validate_phone_number("1234567890") == "+11234567890"
    with pytest.raises(exceptions.ValidationError):
        DataValidator.validate_phone_number("123")

def test_validate_team_name():
    assert DataValidator.validate_team_name("Manchester United") == "Manchester United"
    with pytest.raises(exceptions.ValidationError):
        DataValidator.validate_team_name("")

def test_validate_player_name():
    assert DataValidator.validate_player_name("Lionel Messi") == "Lionel Messi"
    with pytest.raises(exceptions.ValidationError):
        DataValidator.validate_player_name("")

def test_validate_match_data():
    valid_data = {
        "fixture": {"id": 123},
        "teams": {"home": {"name": "Team A"}, "away": {"name": "Team B"}},
        "goals": {"home": 1, "away": 2},
        "league": {"name": "Premier League"}
    }
    result = DataValidator.validate_match_data(valid_data)
    assert result == valid_data

def test_validate_alert_condition():
    valid_condition = {
        "alert_type": "goals",
        "team": "Manchester United",
        "threshold": 2.5
    }
    result = DataValidator.validate_alert_condition(valid_condition)
    assert result["alert_type"] == "goals"

def test_sanitize_html():
    dirty_html = "<script>alert('xss')</script>Hello <b>World</b>"
    clean = DataValidator.sanitize_html(dirty_html)
    assert "<script>" not in clean
    assert "Hello" in clean

# --- Fallback Mechanism Tests ---
class DummyAPI:
    def __init__(self, fail_times=1):
        self.calls = 0
        self.fail_times = fail_times
    async def get_match_data(self, match_id):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise exceptions.SportsAPIError(message="Service Unavailable", status_code=503)
        return {"match_id": match_id, "status": "ok"}

@pytest.mark.asyncio
async def test_get_match_data_with_fallback():
    fallback_manager = FallbackManager()
    dummy_api = DummyAPI(fail_times=2)
    
    # Mock the retry method to use our dummy API
    async def mock_retry(func, *args, **kwargs):
        return await func(*args, **kwargs)
    
    fallback_manager._retry_api_call = mock_retry
    
    # Mock cache methods as async functions
    async def mock_get_cache(match_id):
        return None
    
    fallback_manager._get_from_cache = mock_get_cache
    fallback_manager._create_fallback_match_data = lambda match_id: {"match_id": match_id, "status": "fallback"}
    
    # Should fallback to minimal data after failures
    result = await fallback_manager.get_match_data_with_fallback(123, dummy_api.get_match_data)
    assert result["status"] == "fallback"

def test_create_fallback_match_data():
    fallback_manager = FallbackManager()
    result = fallback_manager._create_fallback_match_data(123)
    assert result["fixture"]["id"] == 123
    assert result["is_fallback"] is True

@pytest.mark.asyncio
async def test_validate_and_repair_match_data():
    fallback_manager = FallbackManager()
    
    # Valid data
    data = {
        "fixture": {"id": 1},
        "teams": {"home": {"name": "A"}, "away": {"name": "B"}},
        "goals": {"home": 1, "away": 2},
        "league": {"name": "Test League"}
    }
    repaired = await fallback_manager.validate_and_repair_match_data(data)
    assert repaired["fixture"]["id"] == 1
    
    # Missing fields
    incomplete = {"fixture": {"id": 2}}
    repaired = await fallback_manager.validate_and_repair_match_data(incomplete)
    assert "teams" in repaired
    assert "goals" in repaired
    assert "league" in repaired

@pytest.mark.asyncio
async def test_get_player_stats_with_fallback():
    fallback_manager = FallbackManager()
    
    # Mock the extraction method to return valid data
    def mock_extract(player_id, events):
        return {
            "player_id": player_id,
            "player_name": "Test Player",
            "goals": 2,
            "assists": 1
        }
    
    fallback_manager._extract_player_stats_from_events = mock_extract
    
    # Test successful extraction - need to provide events that will trigger extraction
    match_data_with_events = {"events": [{"player": {"id": 456}, "type": "Goal"}]}
    result = await fallback_manager.get_player_stats_with_fallback(456, match_data_with_events)
    assert result["player_id"] == 456
    assert result["player_name"] == "Test Player"
    
    # Test fallback when extraction fails - provide empty events
    fallback_manager._extract_player_stats_from_events = lambda player_id, events: None
    result = await fallback_manager.get_player_stats_with_fallback(456, {"events": []})
    assert result["player_id"] == 456
    assert result["player_name"] == "Unknown Player"
    assert result["is_fallback"] is True

# --- Integration Test: API Failure to Fallback ---
@pytest.mark.asyncio
async def test_api_failure_to_fallback():
    fallback_manager = FallbackManager()
    
    async def always_fail(*args, **kwargs):
        raise exceptions.SportsAPIError(message="API Down", status_code=500)
    
    fallback_manager._retry_api_call = always_fail
    
    # Mock cache methods as async functions
    async def mock_get_cache(match_id):
        return None
    
    fallback_manager._get_from_cache = mock_get_cache
    fallback_manager._create_fallback_match_data = lambda match_id: {"match_id": match_id, "status": "fallback"}
    
    result = await fallback_manager.get_match_data_with_fallback(999, lambda x: None)
    assert result["status"] == "fallback" 