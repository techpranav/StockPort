"""
Celery Configuration

Centralized Celery configuration.
"""

from config.app_config import REDIS_HOST, REDIS_PORT, REDIS_DB

# Celery configuration
CELERY_CONFIG = {
    'broker_url': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
    'result_backend': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
    'task_track_started': True,
    'task_time_limit': 300,  # 5 minutes
    'task_soft_time_limit': 240,  # 4 minutes
    'worker_prefetch_multiplier': 1,
    'worker_max_tasks_per_child': 1000,
    'task_routes': {
        'scanner.*': {'queue': 'scanner'},
        'evaluator.*': {'queue': 'evaluator'},
        'executor.*': {'queue': 'executor'}
    }
}

