# Decision engine

## Purpose

The decision engine converts a `StrategySignal` into a `TradingDecision` by applying:

- Timing sanity checks (signal expiry + staleness detection)
- Position sizing (risk-based sizing)
- Risk limits (per-trade, daily, sector, correlation, kill-switch)
- A risk–reward gate

## Key files

- Decision engine: `backend/core/decision_engine.py`
- Position sizing: `backend/capital/position_sizer.py`
- Risk engine: `backend/risk/risk_engine.py`
- Timing:
  - `backend/timing/signal_expiry.py`
  - `backend/timing/stale_detector.py`

## Decision flow (as implemented)

1. Reject if the signal is expired (`SignalExpiryManager.is_signal_stale()`).
2. Reject if the opportunity is stale (`StaleDetector.is_opportunity_stale()`).
3. Compute position size from entry/stop and available capital.
4. Compute:
   - risk amount
   - risk percent (of total capital)
   - reward amount (from take-profit)
   - risk–reward ratio
5. Apply risk checks via `RiskEngine.check_risk()`.
6. Reject if risk–reward is below **1.5:1**.
7. Otherwise approve and emit a `TradingDecision( निर्णय = APPROVE )`.

## Outputs

The decision includes a human-readable `reasoning` string explaining why it was approved/rejected.


