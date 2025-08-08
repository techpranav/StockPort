"""
Base Fetcher

Base class for all data fetching operations with retry logic and rate limiting.
"""

import time
import random
from typing import Callable, Any, Optional
from utils.debug_utils import DebugUtils
from config.settings import API_RATE_LIMIT_DELAY, API_MAX_RETRIES, API_REQUEST_DELAY

class BaseFetcher:
    """Base class for all data fetching operations."""
    
    def __init__(self):
        """Initialize the base fetcher."""
        self.consecutive_failures = 0
        self.last_request_time = 0
        self.rate_limit_delay = API_RATE_LIMIT_DELAY
        self.max_retries = API_MAX_RETRIES
        self.request_delay = API_REQUEST_DELAY
    
    def fetch_with_retry(self, symbol: str, fetch_function: Callable, *args, **kwargs) -> Any:
        """
        Execute a fetch function with retry logic and rate limiting.
        
        Args:
            symbol: Stock symbol being fetched
            fetch_function: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Any: Result from the fetch function
            
        Raises:
            Exception: If all retries are exhausted
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                # Rate limiting
                self._apply_rate_limiting()
                
                # Log the attempt
                DebugUtils.debug(f"Attempt {attempt}/{self.max_retries} for {symbol}")
                
                # Execute the function
                result = fetch_function(*args, **kwargs)
                
                # Reset consecutive failures on success
                self.consecutive_failures = 0
                
                return result
                
            except Exception as e:
                self.consecutive_failures += 1
                error_msg = str(e)
                
                DebugUtils.warning(f"Attempt {attempt} failed for {symbol}: {error_msg}")
                
                # Check if it's a rate limit error (including specific YFRateLimitError)
                is_rate_limit_error = (
                    "rate limit" in error_msg.lower() or 
                    "429" in error_msg or 
                    "YFRateLimitError" in str(type(e)) or
                    "Too Many Requests" in error_msg
                )
                
                if is_rate_limit_error:
                    self._handle_rate_limit_error(attempt)
                elif attempt < self.max_retries:
                    # Exponential backoff with jitter
                    delay = self._calculate_backoff_delay(attempt)
                    DebugUtils.debug(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    # Final attempt failed
                    DebugUtils.error(f"All {self.max_retries} attempts failed for {symbol}")
                    raise e
    
    def _apply_rate_limiting(self) -> None:
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.request_delay:
            sleep_time = self.request_delay - time_since_last_request
            DebugUtils.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _handle_rate_limit_error(self, attempt: int) -> None:
        """
        Handle rate limit errors with increasing delays.
        
        Args:
            attempt: Current attempt number
        """
        # Increase delay for rate limit errors
        base_delay = self.rate_limit_delay * (2 ** (attempt - 1))
        jitter = random.uniform(0.5, 1.5)
        delay = base_delay * jitter
        
        DebugUtils.warning(f"Rate limit hit. Waiting {delay:.2f} seconds before retry...")
        time.sleep(delay)
    
    def _calculate_backoff_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay with jitter.
        
        Args:
            attempt: Current attempt number
            
        Returns:
            float: Delay in seconds
        """
        base_delay = 2 ** attempt  # Exponential backoff
        jitter = random.uniform(0.5, 1.5)  # Add randomness
        return base_delay * jitter
    
    def reset_consecutive_failures(self) -> None:
        """Reset the consecutive failures counter."""
        self.consecutive_failures = 0
    
    def get_consecutive_failures(self) -> int:
        """Get the number of consecutive failures."""
        return self.consecutive_failures 