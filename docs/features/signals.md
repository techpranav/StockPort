# Signals

## What is a signal?

A **signal** is a structured explanation that a strategy believes there is a potential trade setup. Signals are **not** orders. They are inputs into the decision system.

## What a signal contains (conceptually)

Every strategy signal includes:

- The underlying **opportunity** (symbol, price, volume, sector, indicators)
- A **score** (0–100) and **confidence** (0–1)
- A list of **conditions** evaluated (each with weight + score contribution)
- A proposed **entry**, **stop-loss**, and **take-profit**

## Signal fields (what they mean)

- **Strategy**: Which strategy produced the signal (e.g., breakout, trend following).
- **Score**: A numeric “quality” score based on indicators/pattern confirmations.
- **Confidence**: How reliable the setup is expected to be under current market conditions.
- **Freshness**: How recent the triggering event is.
- **Explainability**: The key facts used to justify the setup (e.g., “broke resistance”, “volume expansion”).

## How to use signals

1. Use **Discover** to find signals.
2. Use **Decide** to validate risk–reward (entry, stop, target).
3. Use **Execute** to place/track the order (manual or automated, depending on your mode).

## FAQ

See [General FAQ](../faq/general.md) and [Strategies FAQ](../faq/strategies.md).


