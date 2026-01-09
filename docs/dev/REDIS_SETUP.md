# Redis Setup for Stockport

## Overview

Stockport requires Redis for the EventBus (pub/sub messaging). Redis is a **required dependency** for production use.

## Development Mode: Using fakeredis

For development when Redis server is not installed, you can use **fakeredis** (an in-memory Python mock of Redis).

### Enable fakeredis

Set the environment variable before starting the backend:

```powershell
# PowerShell
$env:USE_FAKEREDIS="true"
python start_backend.py
```

```bash
# Bash/Linux
export USE_FAKEREDIS=true
python start_backend.py
```

### Important Notes

- **fakeredis is for development only** - it's an in-memory mock, not a real Redis server
- **Data is not persisted** - all data is lost when the process ends
- **Not suitable for production** - use real Redis for production deployments
- **Pub/Sub limitations** - fakeredis has limited pub/sub support compared to real Redis

## Production: Installing Real Redis

### Windows

#### Option 1: Memurai (Recommended for Windows)
1. Download from: https://www.memurai.com/get-memurai
2. Install and start the service
3. Redis-compatible, runs as Windows service

#### Option 2: Redis for Windows
1. Download from: https://github.com/microsoftarchive/redis/releases
2. Extract and run `redis-server.exe`
3. Or use the provided `start_redis.ps1` script

#### Option 3: Docker
```powershell
docker run -d -p 6379:6379 --name redis redis
```

#### Option 4: WSL (Windows Subsystem for Linux)
```bash
wsl redis-server
```

### Linux

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis

# CentOS/RHEL
sudo yum install redis
sudo systemctl start redis
```

### macOS

```bash
brew install redis
brew services start redis
```

## Verifying Redis Installation

### Test Connection

```python
import redis
r = redis.Redis()
r.ping()  # Should return True
print("Redis connection successful!")
```

### Command Line

```bash
# Windows (if redis-cli is installed)
redis-cli ping
# Should return: PONG

# Linux/Mac
redis-cli ping
# Should return: PONG
```

## Configuration

Redis connection settings are configured in `config/app_config.py`:

- `REDIS_HOST`: Default `localhost`
- `REDIS_PORT`: Default `6379`
- `REDIS_DB`: Default `0`

You can override these via environment variables:

```powershell
$env:REDIS_HOST="localhost"
$env:REDIS_PORT="6379"
$env:REDIS_DB="0"
```

## Troubleshooting

### Connection Refused Error

**Error**: `ConnectionRefusedError: [WinError 10061] No connection could be made`

**Solutions**:
1. **Redis not running**: Start Redis server
2. **Wrong port**: Check `REDIS_PORT` environment variable
3. **Firewall blocking**: Allow port 6379 in Windows Firewall
4. **Use fakeredis for development**: Set `USE_FAKEREDIS=true`

### Redis Not Found

**Error**: `redis-server: command not found`

**Solutions**:
1. Install Redis (see installation options above)
2. Add Redis to PATH
3. Use Docker: `docker run -d -p 6379:6379 redis`
4. Use fakeredis for development: Set `USE_FAKEREDIS=true`

## Quick Start Script

Use the provided `start_redis.ps1` script:

```powershell
.\start_redis.ps1
```

This script will:
- Check for `redis-server` command
- Check for `memurai` command
- Start the appropriate Redis server
- Provide installation instructions if Redis is not found

## Production Checklist

- [ ] Real Redis server installed and running
- [ ] Redis configured to start on system boot
- [ ] Firewall rules allow Redis connections
- [ ] Redis password configured (if required)
- [ ] Redis persistence enabled (RDB or AOF)
- [ ] Monitoring and alerting configured
- [ ] Backup strategy in place

## Development Checklist

- [ ] fakeredis installed: `pip install fakeredis`
- [ ] `USE_FAKEREDIS=true` environment variable set
- [ ] Backend starts successfully with fakeredis
- [ ] All tests pass with fakeredis

