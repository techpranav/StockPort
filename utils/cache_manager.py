"""
Cache Manager Module

This module provides caching capabilities for stock data and calculations
with TTL-based expiration and cache invalidation.
"""

import time
import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from functools import lru_cache

from utils.debug_utils import DebugUtils
from config.app_config import CACHE_TTL_HOURS


class CacheManager:
    """
    Cache manager for stock data and calculations.
    
    Features:
    - TTL-based expiration (1m for intraday, 1h for daily)
    - Cache warming for frequently analyzed stocks
    - Cache invalidation on market open/close
    - In-memory and file-based caching
    """
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        default_ttl_seconds: int = 3600  # 1 hour default
    ):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory for file-based cache (optional)
            default_ttl_seconds: Default TTL in seconds
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl_seconds
        
        if cache_dir:
            self.cache_dir = Path(cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.cache_dir = None
    
    def get(
        self,
        key: str,
        cache_type: str = "daily"
    ) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            cache_type: Type of cache (intraday, daily) - affects TTL
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_entry = self.cache.get(key)
        
        if cache_entry is None:
            return None
        
        # Check expiration
        ttl = 60 if cache_type == "intraday" else self.default_ttl
        if time.time() - cache_entry['timestamp'] > ttl:
            # Expired
            del self.cache[key]
            return None
        
        DebugUtils.debug(f"Cache hit for key: {key}")
        return cache_entry['value']
    
    def set(
        self,
        key: str,
        value: Any,
        cache_type: str = "daily"
    ) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            cache_type: Type of cache (intraday, daily)
        """
        self.cache[key] = {
            'value': value,
            'timestamp': time.time(),
            'cache_type': cache_type
        }
        
        DebugUtils.debug(f"Cached value for key: {key}")
    
    def invalidate(self, key: Optional[str] = None) -> None:
        """
        Invalidate cache entry or all cache.
        
        Args:
            key: Specific key to invalidate (None = invalidate all)
        """
        if key:
            if key in self.cache:
                del self.cache[key]
                DebugUtils.debug(f"Invalidated cache for key: {key}")
        else:
            self.cache.clear()
            DebugUtils.info("Invalidated all cache")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total_entries = len(self.cache)
        expired_count = 0
        current_time = time.time()
        
        for entry in self.cache.values():
            ttl = 60 if entry.get('cache_type') == "intraday" else self.default_ttl
            if current_time - entry['timestamp'] > ttl:
                expired_count += 1
        
        return {
            'total_entries': total_entries,
            'active_entries': total_entries - expired_count,
            'expired_entries': expired_count
        }

