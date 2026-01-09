# Insight Workspace

**Goal**: understand the current **market environment** and **algo readiness** at a glance.

## Hero: Algo Confidence

The hero element in Insight is the **Algo Confidence** gauge.

- **What it means**: an aggregate confidence score derived from strategy performance.
- **How to use it**:
  - High confidence → environment likely supports the current strategy mix.
  - Low confidence → treat signals as lower priority and be more selective.

## Supporting panels (secondary)

### Market Regime

Shows regime + key descriptors:

- **Regime**: bullish / bearish / neutral (or equivalent)
- **Volatility**: low / normal / high
- **Breadth**: bullish / bearish / neutral

Use this to sanity-check whether today is “trend day”, “chop”, or “risk-off”.

### System Health

Shows data-provider and execution health signals:

- **Provider tiles**: HEALTHY / WARNING / ERROR
- **Latency**: approximate provider latency
- **Drop rate**: approximate loss rate

This helps you quickly distinguish “market is quiet” from “data is degraded”.

## What to do next

- If confidence is strong → go to **Discover** to find candidates.
- If confidence is weak or health is degraded → treat Discover results cautiously and verify system health first.


