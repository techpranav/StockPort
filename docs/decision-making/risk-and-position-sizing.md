# Risk & position sizing

## Core idea

Risk management exists to ensure:

- No single trade can materially damage the portfolio
- Daily losses are capped
- Exposure is controlled (sector/symbol concentration)

## Typical inputs

- **Entry price**
- **Stop loss**
- **Risk per trade** (as % of capital)
- **Volatility** (wider stops require smaller size)

## How position sizing works

Position sizing aims to keep losses small and consistent.

In general:

1. Stockport uses your configured “risk per trade”
2. It sizes the trade so that if your stop-loss is hit, you lose about that amount
3. It also caps maximum position size so one trade can’t dominate your portfolio

## How risk limits are enforced

Before approving a trade, the risk engine checks:

- Kill-switch status
- Per-trade risk limit
- Daily loss limit
- Daily trade limit
- Position size limit
- Sector exposure limit
- Correlation checks

## Risk–reward gate

Even if risk checks pass, the decision engine rejects trades with:

- **Risk–reward < 1.5:1**

## Practical guidance

- For new users, start with small risk-per-trade and manual approval.
- If provider health is degraded, reduce size or stop trading.

## Learn more

If you are a developer, see the developer documentation pages for **Capital & Risk** and **Execution**.


