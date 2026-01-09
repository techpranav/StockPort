# Provider Health

## Why provider health matters

Stockport relies on market data providers. If a provider becomes slow, blocked, or returns incomplete candles, signals can become **stale** or **incorrect**. Provider health helps you decide whether to trust outputs.

## Health states (typical)

- **GREEN**: Data is timely and passes validation.
- **YELLOW**: Degraded (slow, partial failures, minor validation issues).
- **RED**: Unreliable or unavailable (do not trade based on it).

## What you should do

- If **RED**: pause scanning/execution and switch provider if available.
- If **YELLOW**: reduce automation and verify candles manually.

## FAQ

See [Data Providers FAQ](../faq/data-providers.md).


