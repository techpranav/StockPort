"""
Async Data Fetcher Module

This module provides asynchronous data fetching capabilities with connection pooling,
retry logic, and request throttling for efficient parallel API calls.
"""

import asyncio
import aiohttp
import time
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime, timedelta
from collections import deque

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataFetchException, RateLimitException
from config.constants.NumericConstants import API_MAX_RETRIES, API_RATE_LIMIT_DELAY, TIMEOUT_SECONDS


class AsyncFetcher:
    """
    Asynchronous data fetcher with connection pooling and rate limiting.
    
    Features:
    - Connection pooling for efficient HTTP requests
    - Retry logic with exponential backoff
    - Request queuing and throttling
    - Batch processing support
    
    Attributes:
        session: aiohttp client session
        rate_limiter: Rate limiter for API calls
        semaphore: Semaphore for concurrent request limiting
    """
    
    def __init__(
        self,
        max_concurrent: int = 10,
        rate_limit: int = 100,
        rate_window: float = 60.0,
        timeout: int = TIMEOUT_SECONDS
    ):
        """
        Initialize async fetcher.
        
        Args:
            max_concurrent: Maximum concurrent requests
            rate_limit: Maximum requests per rate_window
            rate_window: Time window in seconds for rate limiting
            timeout: Request timeout in seconds
        """
        self.max_concurrent = max_concurrent
        self.rate_limit = rate_limit
        self.rate_window = rate_window
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.rate_limiter = RateLimiter(rate_limit, rate_window)
        
        DebugUtils.info(
            f"Initialized AsyncFetcher: max_concurrent={max_concurrent}, "
            f"rate_limit={rate_limit}/{rate_window}s"
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def fetch(
        self,
        url: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        retries: int = API_MAX_RETRIES
    ) -> Dict[str, Any]:
        """
        Fetch data from URL with retry logic.
        
        Args:
            url: URL to fetch
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            headers: HTTP headers
            retries: Number of retry attempts
            
        Returns:
            Response data as dictionary
            
        Raises:
            DataFetchException: If fetch fails after retries
        """
        if not self.session:
            raise DataFetchException("Session not initialized. Use async context manager.")
        
        last_exception = None
        
        for attempt in range(retries):
            try:
                # Rate limiting
                await self.rate_limiter.acquire()
                
                # Semaphore for concurrency control
                async with self.semaphore:
                    async with self.session.request(
                        method=method,
                        url=url,
                        params=params,
                        headers=headers
                    ) as response:
                        if response.status == 429:  # Rate limit
                            raise RateLimitException(f"Rate limit exceeded for {url}")
                        
                        response.raise_for_status()
                        data = await response.json()
                        
                        DebugUtils.debug(f"Successfully fetched {url} (attempt {attempt + 1})")
                        return data
                        
            except RateLimitException as e:
                wait_time = API_RATE_LIMIT_DELAY * (2 ** attempt)
                DebugUtils.warning(f"Rate limit hit for {url}, waiting {wait_time}s")
                await asyncio.sleep(wait_time)
                last_exception = e
                
            except aiohttp.ClientError as e:
                if attempt < retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    DebugUtils.warning(
                        f"Request failed for {url} (attempt {attempt + 1}/{retries}), "
                        f"retrying in {wait_time}s: {str(e)}"
                    )
                    await asyncio.sleep(wait_time)
                last_exception = e
                
            except Exception as e:
                DebugUtils.log_error(e, f"Unexpected error fetching {url}")
                last_exception = e
                break
        
        raise DataFetchException(
            f"Failed to fetch {url} after {retries} attempts: {str(last_exception)}"
        ) from last_exception
    
    async def fetch_batch(
        self,
        urls: List[str],
        method: str = "GET",
        params_list: Optional[List[Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch multiple URLs in parallel.
        
        Args:
            urls: List of URLs to fetch
            method: HTTP method
            params_list: Optional list of parameter dicts (one per URL)
            headers: HTTP headers
            
        Returns:
            List of response data dictionaries
        """
        if params_list is None:
            params_list = [None] * len(urls)
        
        tasks = [
            self.fetch(url, method, params, headers)
            for url, params in zip(urls, params_list)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Separate successful results from exceptions
        successful = []
        failed = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed.append((urls[i], result))
                DebugUtils.log_error(result, f"Failed to fetch {urls[i]}")
            else:
                successful.append(result)
        
        if failed:
            DebugUtils.warning(f"Failed to fetch {len(failed)}/{len(urls)} URLs")
        
        return successful
    
    async def fetch_with_callback(
        self,
        url: str,
        callback: Callable[[Dict[str, Any]], Awaitable[Any]],
        **fetch_kwargs
    ) -> Any:
        """
        Fetch data and process with async callback.
        
        Args:
            url: URL to fetch
            callback: Async callback function to process data
            **fetch_kwargs: Additional arguments for fetch()
            
        Returns:
            Result from callback function
        """
        data = await self.fetch(url, **fetch_kwargs)
        return await callback(data)


class RateLimiter:
    """
    Rate limiter for async operations.
    
    Tracks request timestamps and enforces rate limits.
    """
    
    def __init__(self, max_calls: int, period: float):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum calls allowed
            period: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls: deque = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """
        Acquire permission to make a request.
        
        Waits if necessary to respect rate limits.
        """
        async with self.lock:
            now = time.time()
            
            # Remove old calls outside the period
            while self.calls and now - self.calls[0] > self.period:
                self.calls.popleft()
            
            # If at limit, wait until oldest call expires
            if len(self.calls) >= self.max_calls:
                wait_time = self.period - (now - self.calls[0])
                if wait_time > 0:
                    DebugUtils.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    # Remove expired calls after waiting
                    now = time.time()
                    while self.calls and now - self.calls[0] > self.period:
                        self.calls.popleft()
            
            # Record this call
            self.calls.append(time.time())

