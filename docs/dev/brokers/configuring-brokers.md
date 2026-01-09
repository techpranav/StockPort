# Configuring brokers

This page describes how to configure brokers and broker APIs safely.

## Principles

- **Never commit secrets** (use `.env` / environment variables)
- **Prefer paper/manual mode** until validated end-to-end
- **Fail safe** (reject execution if configuration is incomplete)

## Typical configuration

- Broker selection (name/type)
- API credentials (env vars)
- Redirect URIs / OAuth setup (if required)
- Risk limits (so broker execution is gated)

## Related docs

- [Authentication setup](../AUTHENTICATION_SETUP.md)
- [Webhook setup guide](../WEBHOOK_SETUP_GUIDE.md) (if using webhooks for broker updates)


