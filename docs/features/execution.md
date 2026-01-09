# Execution

## What execution means in Stockport

Execution is the stage where a **decision** becomes an **order** and the system monitors the full order lifecycle.

## Typical flow

1. A signal is generated (strategy).
2. Risk/capital gates approve or reject (decision system).
3. An order is created and routed to the configured broker.
4. The UI shows status changes: submitted → partial fill → filled / rejected / cancelled.

## Modes (recommended progression)

- **Manual**: You approve every trade.
- **Paper**: No real capital, but the system simulates execution.
- **Live**: Real broker orders (only after you trust providers, risk limits, and strategy behavior).

## FAQ

See [Execution FAQ](../faq/execution.md).


