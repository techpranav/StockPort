# Stockport v4 Setup Guide

## Prerequisites

1. **Python 3.8+**
2. **PostgreSQL 12+**
3. **Redis 6+**
4. **Celery** (for distributed task processing)

## Installation Steps

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Database

**Option A: SQLite (Recommended for Personal Use - Default)**

SQLite is the default and requires no setup. Just run:
```bash
python database/init_db.py
```

This creates a SQLite database file at `data/stockport.db`.

**Option B: PostgreSQL (Optional)**

If you prefer PostgreSQL (already installed on your machine):

1. Create a database (if needed):
   ```sql
   CREATE DATABASE stockport;
   ```

2. Update `.env` file with PostgreSQL credentials:
   ```
   DATABASE_TYPE=postgresql
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=stockport
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=admin
   ```

3. Initialize database schema:
   ```bash
   python database/init_db.py --postgresql
   ```

**Note**: For personal use, SQLite is recommended as it's simpler and requires no separate server process.

### 3. Set Up Redis

1. Install Redis if not already installed
2. Start Redis server:
   ```bash
   redis-server
   ```

3. Update `.env` file with Redis configuration:
   ```
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   ```

### 4. Configure Celery Workers

1. Start Celery worker for scanners:
   ```bash
   celery -A backend.workers.scanner_worker worker --loglevel=info --queue=scanner
   ```

2. Start Celery worker for evaluators:
   ```bash
   celery -A backend.workers.evaluator_worker worker --loglevel=info --queue=evaluator
   ```

3. Start Celery worker for executors:
   ```bash
   celery -A backend.workers.executor_worker worker --loglevel=info --queue=executor
   ```

### 5. Load Strategies

1. Place strategy YAML files in `config/strategies/`
2. Strategies will be automatically loaded on startup

### 6. Start the System

1. Start the main trading engine:
   ```bash
   python -m backend.core.engine
   ```

2. Start the WebSocket server (for UI):
   ```bash
   python -m backend.api.websocket_server
   ```

3. Start the REST API:
   ```bash
   python -m backend.api.rest_api
   ```

4. Start the Streamlit UI:
   ```bash
   streamlit run ui/dashboard.py
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root with:

```env
# Database (SQLite is default, no config needed)
# To use PostgreSQL instead, uncomment and set:
# DATABASE_TYPE=postgresql
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DB=stockport
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=admin

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Trading Configuration
INITIAL_CAPITAL=100000.0
MAX_RISK_PER_TRADE=0.02
MAX_DAILY_LOSS=0.05
```

## Testing

### Paper Trading Mode

The system starts in paper trading mode by default. To enable:

1. Set trading mode to "paper" in configuration
2. Paper broker will simulate trades without real money

### Manual Mode

1. Set trading mode to "manual" in UI
2. System will generate signals but require manual approval

### Semi-Auto Mode

1. Set trading mode to "semi_auto" in UI
2. System will auto-execute up to daily capital limit

### Full Auto Mode

1. Set trading mode to "full_auto" in UI
2. System will fully automate trading (use with caution!)

## Monitoring

- **Dashboard**: `http://localhost:8501` (Streamlit)
- **REST API**: `http://localhost:8001`
- **WebSocket**: `ws://localhost:8000/ws`

## Troubleshooting

### Database Connection Issues

**SQLite (Default):**
- No setup needed, works out of the box
- Database file created automatically at `data/stockport.db`

**PostgreSQL (Optional):**
- Verify PostgreSQL is running: `pg_isready`
- Check credentials in `.env` file
- Ensure database exists: `CREATE DATABASE stockport;`
- If using default postgres user, password is "admin" (as you mentioned)

### Redis Connection Issues

- Verify Redis is running: `redis-cli ping`
- Check Redis configuration in `.env` file

### Celery Worker Issues

- Check Redis connection
- Verify worker queues match task routes
- Check logs for errors

## Next Steps

1. Review strategy definitions in `config/strategies/`
2. Customize risk limits in configuration
3. Test with paper trading first
4. Monitor performance and adjust strategies
5. Gradually increase automation level

