# Celery Workers Setup Guide

## Overview

Celery workers are used for distributed scanning tasks with rate limiting to prevent API overload.

## Configuration

### Rate Limits
- **Market scan**: 10 tasks/second
- **Single symbol scan**: 20 tasks/second

### Task Queues
- `scanner`: Scanner tasks
- `evaluator`: Strategy evaluation tasks (future)
- `executor`: Execution tasks (future)

## Starting Workers

### Development (Local)
```bash
# Start scanner worker
celery -A backend.workers.scanner_worker worker --loglevel=info --queue=scanner

# Start with multiple workers
celery -A backend.workers.scanner_worker worker --loglevel=info --queue=scanner --concurrency=4
```

### Production
```bash
# Start as daemon
celery -A backend.workers.scanner_worker worker \
    --loglevel=info \
    --queue=scanner \
    --concurrency=4 \
    --max-tasks-per-child=1000 \
    --detach
```

## Monitoring

### Check worker status
```bash
celery -A backend.workers.scanner_worker inspect active
celery -A backend.workers.scanner_worker inspect stats
```

### View task results
```bash
celery -A backend.workers.scanner_worker result <task_id>
```

## Rate Limiting

Rate limiting is enforced at two levels:

1. **Celery task rate limits**: Configured per task type
2. **API rate limits**: Handled by data providers

### Adjusting Rate Limits

Edit `backend/workers/scanner_worker.py`:
```python
@celery_app.task(
    name='scanner.scan_market',
    rate_limit='10/s',  # Change this value
    bind=True
)
```

## Requirements

- Redis running (for broker and result backend)
- Python packages: `celery`, `redis`

## Troubleshooting

### Worker not starting
- Check Redis connection: `redis-cli ping`
- Verify Redis host/port in `config/app_config.py`

### Tasks not executing
- Check worker logs
- Verify task is in correct queue
- Check rate limits aren't too restrictive

### High latency
- Increase worker concurrency
- Adjust rate limits
- Check Redis performance

