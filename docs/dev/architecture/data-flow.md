# Data Flow

## UI → backend (read path)

The UI pulls data via `ui/services/api_client.py` and `ui/services/ui_data_service.py`.

Typical calls:

- `/status` → system running state
- `/market/state` → market regime snapshot
- `/data/health` → provider health snapshot
- `/opportunities` → opportunity feed (scanner output)
- `/orders` → order feed (execution output)
- `/positions` → open positions

## UI derivations

The UI computes derived metrics in `ui/services/metric_deriver.py`:

- **Algo confidence** from strategy performance
- **Signal stream** derived from opportunities
- **Execution quality** derived from orders

This keeps the backend stable while allowing the UI to evolve.

## Error handling

- API calls are wrapped with timeouts and safe fallbacks.
- Missing fields are treated defensively (e.g., absent risk metrics).


