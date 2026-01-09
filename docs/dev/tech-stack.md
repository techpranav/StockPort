# Tech stack

## Runtime

- **Python**: primary language for backend services and analysis
- **Streamlit**: UI (“Trading OS”)
- **FastAPI**: REST API layer (commands/queries)
- **WebSockets**: real-time updates/events

## Data & analysis

- **pandas / NumPy / SciPy**: time-series processing and indicator math
- **Plotly**: charting
- **yfinance / NSE providers**: market data ingestion (provider-specific)

## Distributed / async

- **Redis**: event bus / pub-sub / coordination
- **Celery**: background tasks and parallelization

## Docs

- **MkDocs + Material**: developer docs (`mkdocs.yml`) and user docs (`mkdocs-user.yml`)

## Where versions live

See `requirements.txt` for pinned minimum versions.


