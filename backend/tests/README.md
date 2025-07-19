# TouchLine Tests

This directory contains all test files for the TouchLine backend system.

## Test Files

### Core System Tests
- **`test_integration.py`** - Full system integration test
- **`test_alert_engine.py`** - Alert engine functionality test
- **`test_live_monitoring.py`** - Live match monitoring test

### API Tests
- **`test_api_fix.py`** - API-Football connectivity and data fetching test
- **`test_advanced_metrics.py`** - Advanced metrics calculation test

### Advanced Features Tests
- **`test_advanced_conditions.py`** - Advanced condition evaluator test
- **`test_advanced_monitoring.py`** - Advanced monitoring with complex conditions

## Running Tests

```bash
# Run all tests
cd backend
python -m pytest tests/

# Run specific test
python tests/test_advanced_conditions.py
python tests/test_live_monitoring.py
```

## Test Categories

### ✅ Integration Tests
- Full system workflow
- Component interaction
- End-to-end functionality

### ✅ Unit Tests
- Individual component testing
- API connectivity
- Data processing

### ✅ Feature Tests
- Advanced condition evaluation
- Multi-condition logic
- Real-time monitoring

## Test Data

Tests use:
- **Live API data** from API-Football
- **Sample data** when live matches unavailable
- **Mock data** for isolated component testing 