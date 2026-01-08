# Stockport v4 - Test Suite

## Overview

Comprehensive test suite for Stockport v4 trading system with unit tests, integration tests, and coverage reporting.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_runner.py           # Test runner script
├── unit/                    # Unit tests
│   ├── test_data_integrity.py
│   ├── test_market_state.py
│   ├── test_capital_manager.py
│   ├── test_risk_engine.py
│   └── test_position_sizer.py
└── integration/             # Integration tests
    ├── test_end_to_end_flow.py
    ├── test_disaster_recovery.py
    ├── test_duplicate_prevention.py
    └── test_audit_logging.py
```

## Running Tests

### All Tests
```bash
pytest tests/
```

### Unit Tests Only
```bash
pytest tests/unit/
```

### Integration Tests Only
```bash
pytest tests/integration/
```

### With Coverage
```bash
pytest tests/ --cov=backend --cov=ui --cov=models --cov-report=html
```

### Using Makefile
```bash
make test              # Run all tests
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-coverage     # With coverage report
make test-all          # Full coverage with threshold
```

### Using Test Runner
```bash
python tests/test_runner.py                    # All tests
python tests/test_runner.py --unit-only        # Unit tests
python tests/test_runner.py --integration-only # Integration tests
python tests/test_runner.py --no-coverage      # Skip coverage
```

## Test Markers

Tests are marked with pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.requires_redis` - Requires Redis
- `@pytest.mark.requires_db` - Requires database
- `@pytest.mark.requires_broker` - Requires broker connection

### Run Tests by Marker
```bash
pytest -m unit              # Unit tests only
pytest -m integration        # Integration tests only
pytest -m "not slow"         # Skip slow tests
```

## Coverage

Coverage reports are generated in multiple formats:

- **HTML**: `htmlcov/index.html` - Interactive HTML report
- **Terminal**: Console output with missing lines
- **XML**: `coverage.xml` - For CI/CD integration

### Coverage Threshold

Minimum coverage threshold: **70%**

Tests will fail if coverage falls below this threshold.

## Fixtures

Shared fixtures are defined in `conftest.py`:

- `capital_manager` - Capital manager instance
- `position_sizer` - Position sizer instance
- `risk_engine` - Risk engine instance
- `portfolio_manager` - Portfolio manager instance
- `market_state_engine` - Market state engine instance
- `strategy_registry` - Strategy registry instance
- `paper_broker` - Paper broker instance
- `order_manager` - Order manager instance
- `performance_tracker` - Performance tracker instance
- `health_monitor` - Health monitor instance
- `truth_layer` - Truth layer instance
- `audit_logger` - Audit logger instance
- `market_scanner` - Market scanner instance
- `strategy_evaluator` - Strategy evaluator instance
- `decision_engine` - Decision engine instance
- `execution_engine` - Execution engine instance
- `complete_system` - Complete system with all components
- `sample_opportunity` - Sample opportunity for testing
- `sample_signal` - Sample strategy signal for testing

## CI/CD

Tests run automatically on:

- Push to main/develop branches
- Pull requests
- Daily schedule (2 AM UTC)

See `.github/workflows/tests.yml` for CI configuration.

## Writing Tests

### Unit Test Example
```python
def test_capital_allocation(capital_manager):
    """Test capital allocation."""
    capital_manager.allocate_capital(5000.0, "order_1")
    assert capital_manager.get_reserved_capital() == 5000.0
```

### Integration Test Example
```python
def test_complete_flow(complete_system):
    """Test complete flow."""
    scanner = complete_system['scanner']
    opportunities = scanner.scan(symbols=["AAPL"])
    # ... test flow
```

## Best Practices

1. **Use fixtures** - Leverage shared fixtures from `conftest.py`
2. **Test isolation** - Each test should be independent
3. **Clear names** - Test names should describe what they test
4. **Assertions** - Use specific assertions, not just `assert True`
5. **Coverage** - Aim for high coverage but focus on critical paths
6. **Documentation** - Add docstrings to test functions

## Troubleshooting

### Tests Failing
- Check test output for specific errors
- Verify fixtures are properly initialized
- Ensure dependencies are installed

### Coverage Low
- Run `pytest --cov-report=term-missing` to see missing lines
- Focus on critical business logic first
- Add tests for edge cases

### Slow Tests
- Mark slow tests with `@pytest.mark.slow`
- Run with `pytest -m "not slow"` to skip
- Consider parallel execution for large suites
