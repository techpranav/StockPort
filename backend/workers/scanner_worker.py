"""
Scanner Worker

Celery worker for market scanning tasks.
"""

from celery import Celery
from typing import List, Dict, Any

from utils.debug_utils import DebugUtils
from backend.scanners.market_scanner import MarketScanner
from backend.data.integrity.truth_layer import TruthLayer
from config.app_config import REDIS_HOST, REDIS_PORT, REDIS_DB

# Initialize Celery app
celery_app = Celery(
    'stockport_scanner',
    broker=f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
    backend=f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
)

# Celery configuration with rate limiting
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    # Rate limiting: max 10 tasks per second per worker
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Task rate limits (tasks per second)
    task_routes={
        'scanner.*': {
            'queue': 'scanner',
            'rate_limit': '10/s'  # 10 tasks per second
        }
    }
)


@celery_app.task(
    name='scanner.scan_market',
    rate_limit='10/s',  # Rate limit: 10 tasks per second
    bind=True  # Bind task to access self
)
def scan_market(self, symbols: List[str] = None) -> List[Dict[str, Any]]:
    """
    Scan market for opportunities.
    
    Args:
        symbols: List of symbols to scan (None = scan all)
        
    Returns:
        List of opportunity dictionaries
    """
    try:
        # Initialize scanner
        truth_layer = TruthLayer(None, None, None)  # Would be injected properly
        scanner = MarketScanner(truth_layer=truth_layer)
        
        # Scan
        opportunities = scanner.scan(symbols)
        
        # Convert to dictionaries
        return [opp.to_dict() for opp in opportunities]
    except Exception as e:
        DebugUtils.log_error(e, "Error in scanner worker")
        raise


@celery_app.task(
    name='scanner.scan_symbol',
    rate_limit='20/s',  # Rate limit: 20 tasks per second (single symbol scans)
    bind=True
)
def scan_symbol(self, symbol: str) -> Dict[str, Any]:
    """
    Scan a single symbol.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Opportunity dictionary or None
    """
    try:
        truth_layer = TruthLayer(None, None, None)
        scanner = MarketScanner(truth_layer=truth_layer)
        
        opportunity = scanner._scan_symbol(symbol)
        
        if opportunity:
            return opportunity.to_dict()
        return None
    except Exception as e:
        DebugUtils.log_error(e, f"Error scanning symbol {symbol}")
        raise

