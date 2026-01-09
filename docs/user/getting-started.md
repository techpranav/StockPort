# Getting Started with Stockport

Welcome to Stockport v4! This guide will help you get started with the system.

## Prerequisites

- Python 3.8 or higher
- Redis (for event bus)
- PostgreSQL (optional, SQLite is default)

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install NSEDownload (if needed):
   ```bash
   git clone https://github.com/your-org/NSEDownload.git
   cd NSEDownload
   pip install -e .
   ```

3. Start Redis:
   ```bash
   redis-server
   ```

## Starting the System

### Start Backend

```bash
python -m backend.api.rest_api
# or
python start_backend.py
```

The backend will start on `http://localhost:8001`

### Start UI

```bash
streamlit run app.py
```

The UI will be available at `http://localhost:8501`

## First Steps

1. **Open Insight**: confirm market context + system health
2. **Open Discover**: scan the Opportunity Radar
3. **Pick a candidate**: expand a signal card for quick context
4. **Move to Decide**: validate risk–reward for one candidate
5. **Execute/Review**: monitor execution and later review outcomes

## Next Steps

- [Workspaces Overview](workspaces/overview.md)
- [Daily Workflow](guides/daily-workflow.md)

