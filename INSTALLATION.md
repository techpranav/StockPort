# Stockport v4 Installation Guide

## Prerequisites

- Python 3.8 or higher
- Redis (for event bus)
- PostgreSQL (optional, SQLite is default)

## Step-by-Step Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install NSEDownload (NSE Data Provider)

NSEDownload requires cloning from GitHub as it's not available on PyPI:

```bash
# Clone the repository
git clone https://github.com/rajatdiptabiswas/NSEDownload.git NSEDownload

# Install in editable mode
cd NSEDownload
pip install -e .
cd ..
```

### 3. Install Redis

**Windows:**
- Download from [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
- Or use Docker: `docker run -d -p 6379:6379 redis`

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis
```

### 4. Start Redis

```bash
# Windows
redis-server

# Linux/Mac
redis-server

# Or using Docker
docker run -d -p 6379:6379 redis
```

### 5. Verify Installation

```bash
# Test Python imports
python -c "import streamlit, fastapi, redis, pandas, numpy; print('All imports successful')"

# Test Redis connection
python -c "import redis; r = redis.Redis(); r.ping(); print('Redis connection successful')"
```

## Troubleshooting

### NSEDownload Installation Issues

If NSEDownload installation fails:
1. Ensure Git is installed
2. Check internet connection
3. Try cloning manually and then installing:
   ```bash
   git clone https://github.com/rajatdiptabiswas/NSEDownload.git
   cd NSEDownload
   pip install -e .
   ```

### Redis Connection Issues

If Redis connection fails:
1. Verify Redis is running: `redis-cli ping` (should return `PONG`)
2. Check Redis host/port in configuration
3. Ensure firewall allows Redis connections

### Missing Dependencies

If you encounter import errors:
1. Reinstall requirements: `pip install -r requirements.txt --upgrade`
2. Check Python version: `python --version` (should be 3.8+)
3. Verify virtual environment is activated (if using one)

## Next Steps

After installation:
1. [Start the Backend](../docs/setup/backend-startup.md)
2. [Start the UI](../docs/setup/ui-startup.md)
3. [Configure Settings](../docs/user/settings/overview.md)

