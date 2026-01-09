# FAQ (Data Providers)

## What providers are supported?

This depends on configuration, but Stockport is designed to support multiple providers (e.g., Yahoo Finance, NSE-specific providers).

## Why is provider health RED?

Common reasons:

- Rate limiting or blocking by the provider
- Network connectivity issues
- Invalid/partial data (failed validation)

## What should I do when provider health is RED?

- Stop live execution
- Switch provider (if configured)
- Reduce symbol universe and retry later


