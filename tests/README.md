# Test Suite Documentation

## Overview

This test suite provides comprehensive automated testing for the Stock Analysis Application, ensuring that all critical calculations, data processing, and backend endpoints work correctly.

## Test Structure

```
tests/
├── conftest.py                    # Pytest configuration and shared fixtures
├── unit/                          # Unit tests for individual components
│   ├── test_technical_analysis.py    # Technical indicator calculations
│   ├── test_stock_service.py         # Stock service functionality
│   ├── test_indicators.py             # Individual indicator tests
│   └── test_signal_generation.py      # Signal generation tests
└── integration/                    # Integration tests
    ├── test_webhook_endpoints.py      # Webhook endpoint tests
    └── test_stock_analyzer.py         # End-to-end analyzer tests
```

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Suite
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v
```

### Run with Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/unit/test_technical_analysis.py -v
```

## Test Coverage

### Unit Tests (32 tests)

#### Technical Analysis Tests (`test_technical_analysis.py`)
- ✅ Indicator calculation with valid data
- ✅ Empty DataFrame handling
- ✅ Insufficient data handling
- ✅ None data handling
- ✅ SMA calculation accuracy
- ✅ RSI calculation accuracy and range validation
- ✅ RSI overbought/oversold detection
- ✅ MACD calculation accuracy
- ✅ Signal generation structure and format
- ✅ Trend analysis (bullish, bearish, neutral)

#### Stock Service Tests (`test_stock_service.py`)
- ✅ Service initialization
- ✅ Custom days_back configuration
- ✅ Stock data fetching (success and failure)
- ✅ Provider name retrieval
- ✅ Days back setting/getting

#### Indicator Tests (`test_indicators.py`)
- ✅ RSI basic calculation
- ✅ ATR (Average True Range) calculation
- ✅ Volume SMA calculation
- ✅ OBV (On-Balance Volume) calculation
- ✅ ROC (Rate of Change) calculation
- ✅ Momentum calculation

#### Signal Generation Tests (`test_signal_generation.py`)
- ✅ Signal structure validation
- ✅ Buy signal on MA crossover
- ✅ Sell signal on MA crossover
- ✅ Signal format validation
- ✅ Trend analysis integration

### Integration Tests (16 tests)

#### Webhook Endpoint Tests (`test_webhook_endpoints.py`)
- ✅ Health check endpoint
- ✅ Razorpay webhook (empty payload, valid payload, processing failure)
- ✅ Stripe webhook (not configured, valid payload)
- ✅ PayPal webhook (not configured, valid payload)
- ✅ Error handling

#### Stock Analyzer Tests (`test_stock_analyzer.py`)
- ✅ Analyzer initialization
- ✅ Stock processing (success and failure)
- ✅ Stock symbols file operations
- ✅ Completed/failed symbol tracking

## Critical Calculations Verified

### Technical Indicators
1. **SMA (Simple Moving Average)**: Verified against manual calculations
2. **RSI (Relative Strength Index)**: 
   - Values in valid range (0-100)
   - Matches standard RSI formula
   - Overbought (>70) and oversold (<30) detection
3. **MACD (Moving Average Convergence Divergence)**:
   - MACD line calculation
   - Signal line calculation
   - Histogram = MACD - Signal (verified)

### Signal Generation
- Moving average crossover detection
- Buy/sell signal format validation
- Trend direction and strength analysis

### Data Validation
- Empty data handling
- Insufficient data handling
- Invalid input handling
- Data type validation

## Test Fixtures

### `sample_price_data`
Generates realistic OHLCV price data with 100 days of history for testing.

### `sample_stock_data`
Creates a complete StockData object with:
- Company information
- Financial metrics
- Technical indicators
- Historical price data

### `mock_stock_service`
Mock StockService for isolated testing.

### `mock_webhook_payload`
Sample webhook payload for testing payment gateway integrations.

## Best Practices

1. **Isolation**: Each test is independent and doesn't rely on other tests
2. **Mocking**: External dependencies (APIs, services) are mocked
3. **Validation**: Critical calculations are verified against expected formulas
4. **Error Handling**: Tests verify proper error handling for edge cases
5. **Coverage**: Tests cover both success and failure scenarios

## Continuous Integration

These tests should be run:
- Before committing code
- In CI/CD pipeline
- After major refactoring
- When adding new features

## Adding New Tests

When adding new functionality:

1. **Unit Tests**: Add to appropriate `test_*.py` file in `tests/unit/`
2. **Integration Tests**: Add to appropriate file in `tests/integration/`
3. **Fixtures**: Add shared fixtures to `conftest.py`
4. **Documentation**: Update this README with new test coverage

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test
```python
def test_calculate_rsi_with_valid_data(sample_price_data):
    """Test RSI calculation with valid price data."""
    indicators = TechnicalAnalyzer.calculate_indicators(sample_price_data)
    
    assert 'rsi' in indicators
    rsi = indicators['rsi'].dropna()
    assert (rsi >= 0).all()
    assert (rsi <= 100).all()
```

## Test Results Summary

**Current Status**: ✅ All 48 tests passing

- Unit Tests: 32 passing
- Integration Tests: 16 passing
- Coverage: Critical calculations and endpoints verified

