# Getting Started - Developer Guide

This guide will help you set up your development environment for Stockport v4.

## Prerequisites

- Python 3.8 or higher
- Redis (for event bus)
- PostgreSQL (optional, SQLite is default)
- Git

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd stockport
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install NSEDownload (NSE Data Provider)

NSEDownload requires cloning from GitHub:

```bash
git clone https://github.com/rajatdiptabiswas/NSEDownload.git NSEDownload
cd NSEDownload
pip install -e .
cd ..
```

### 4. Start Redis

```bash
# Windows (if installed)
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
STOCKPORT_API_URL=http://localhost:8001
STOCKPORT_API_HOST=0.0.0.0
STOCKPORT_API_PORT=8001
REDIS_HOST=localhost
REDIS_PORT=6379
DATABASE_TYPE=sqlite
```

## Running the System

### Start Backend

```bash
# Option 1: Using module
python -m backend.api.rest_api

# Option 2: Using startup script
python start_backend.py
```

The backend will start on `http://localhost:8001`

### Start UI

```bash
streamlit run app.py
```

The UI will be available at `http://localhost:8501`

## Development Workflow

### Running Tests

```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# With coverage
pytest tests/ --cov=backend --cov=ui
```

### Code Quality

```bash
# Linting
pylint backend/ ui/

# Type checking
mypy backend/ ui/
```

## Next Steps

- [Architecture Overview](architecture/overview.md)
- [Backend Components](backend/core-components.md)
- [API Documentation](api/rest-api.md)

