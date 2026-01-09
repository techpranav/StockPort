# Timing Awareness Integration

## Overview

Timing awareness has been integrated into the decision engine to ensure only fresh, valid signals are processed.

## Integration Points

### Decision Engine
- **Signal Expiry Check**: Rejects expired signals before capital/risk calculations
- **Stale Detection**: Rejects opportunities with significant price/volume changes
- **Early Rejection**: Saves computational resources by rejecting stale signals early

### Implementation

```python
# In decision_engine.py
# Check if signal is stale (timing awareness)
if self.expiry_manager.is_signal_stale(signal):
    # Reject with expiry information
    return TradingDecision(decision="REJECT", ...)

# Check if opportunity is stale
if self.stale_detector.is_opportunity_stale(opportunity, signal):
    # Reject with staleness reason
    return TradingDecision(decision="REJECT", ...)
```

## Expiry Rules

- **Intraday strategies**: 5 minutes
- **Swing strategies**: 1 hour
- **Position strategies**: 4 hours

## Staleness Indicators

1. **Time-based**: Signal age exceeds expiry time
2. **Price change**: >5% price movement from entry
3. **Volume drop**: >50% volume decrease

## Benefits

1. **Prevents stale trades**: Only fresh signals are executed
2. **Saves resources**: Early rejection saves computation
3. **Improves performance**: Better entry timing
4. **Reduces risk**: Avoids trades on outdated information

## Future Integration Points

### Execution Engine
- Final stale check before order placement
- Latency tracking for execution time

### Strategy Evaluator
- Track evaluation latency
- Reject opportunities that took too long to evaluate

### UI Components
- Display signal age and expiry status
- Show latency metrics
- Alert on stale signals

