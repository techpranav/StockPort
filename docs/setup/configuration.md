# Configuration

Stockport configuration is primarily controlled via environment variables and configuration modules under `config/`.

## Key configuration areas

- **Backend API URL for UI**: `STOCKPORT_API_URL`
- **Enable/disable authentication**: used by UI developer mode
- **Worker limits / parallelism**: configured via `config/app_config.py` (if present in your branch)

## Secrets

Never commit API keys or broker credentials.

- Use `.env` (gitignored) or environment variables.


