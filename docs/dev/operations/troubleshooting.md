# Troubleshooting (Operations)

## Quick checks

1. Provider health is GREEN
2. Redis is running and reachable
3. API server starts cleanly
4. No repeated exceptions in logs

## Common issues

- **No data / empty charts**: provider blocked or returned invalid candles
- **No signals**: universe too small, filters too strict, or regime mismatch
- **Execution failures**: broker config/auth problem, risk gate blocks, or market closed


