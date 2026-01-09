# Adding a new data provider

This guide explains the expectations for integrating a new data provider.

## Goals

- Safe ingestion (validate shape, timestamps, missing candles)
- Clear failures (custom exceptions + logging)
- Health monitoring (GREEN/YELLOW/RED)
- Config-driven enable/disable (no hardcoded secrets)

## Checklist

1. Implement the provider in `services/data_providers/`
2. Add configuration options in `config/app_config.py` (load secrets from env)
3. Add validation and error handling (raise custom exceptions)
4. Add health reporting hooks (so UI can display status)
5. Add tests (mock external calls; no real API calls in unit tests)


