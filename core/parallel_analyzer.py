"""
Parallel Stock Analyzer Module

This module provides parallel processing capabilities for analyzing multiple stocks
simultaneously using thread pools for I/O-bound operations and process pools for
CPU-bound calculations.
"""

import os
import time
from typing import Dict, Any, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, Future
from threading import Lock, Semaphore
from datetime import datetime
import multiprocessing as mp

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataAnalysisException
from config.app_config import MAX_CONCURRENT_ANALYSES
from config.constants.NumericConstants import API_RATE_LIMIT_DELAY, API_REQUEST_DELAY


class ParallelStockAnalyzer:
    """
    Parallel stock analyzer for processing multiple stocks concurrently.
    
    Uses thread pools for I/O-bound operations (API calls) and process pools
    for CPU-bound operations (calculations). Includes rate limiting, error
    isolation, and progress tracking.
    
    Attributes:
        max_workers: Maximum number of concurrent workers
        rate_limiter: Rate limiter to respect API limits
        progress_lock: Thread lock for progress tracking
    """
    
    def __init__(
        self,
        max_workers: Optional[int] = None,
        rate_limit_per_worker: int = 10,
        rate_limit_window: float = 60.0
    ):
        """
        Initialize parallel stock analyzer.
        
        Args:
            max_workers: Maximum number of concurrent workers.
                        If None, uses min(MAX_CONCURRENT_ANALYSES, CPU count * 2)
            rate_limit_per_worker: Maximum API calls per worker per window
            rate_limit_window: Time window in seconds for rate limiting
        """
        # Determine optimal worker count
        if max_workers is None:
            cpu_count = mp.cpu_count()
            self.max_workers = min(
                MAX_CONCURRENT_ANALYSES,
                cpu_count * 2,
                20  # Cap at 20 to avoid overwhelming APIs
            )
        else:
            self.max_workers = max(1, min(max_workers, 50))  # Cap at 50
        
        self.rate_limit_per_worker = rate_limit_per_worker
        self.rate_limit_window = rate_limit_window
        
        # Thread-safe progress tracking
        self.progress_lock = Lock()
        self._completed_count = 0
        self._failed_count = 0
        self._total_count = 0
        
        # Rate limiting semaphore
        self.rate_limiter = Semaphore(self.max_workers)
        
        DebugUtils.info(
            f"Initialized ParallelStockAnalyzer with {self.max_workers} workers, "
            f"rate_limit={rate_limit_per_worker}/{rate_limit_window}s"
        )
    
    def analyze_batch(
        self,
        symbols: List[str],
        analysis_func: Callable[[str], Dict[str, Any]],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze multiple stocks in parallel.
        
        Args:
            symbols: List of stock symbols to analyze
            analysis_func: Function to analyze a single stock (takes symbol, returns result dict)
            progress_callback: Optional callback for progress updates (completed, total, current_symbol)
            
        Returns:
            Dictionary mapping symbol to analysis result
            
        Example:
            >>> analyzer = ParallelStockAnalyzer(max_workers=10)
            >>> results = analyzer.analyze_batch(
            ...     ['AAPL', 'MSFT'],
            ...     lambda s: stock_analyzer.process_stock(s)
            ... )
        """
        if not symbols:
            DebugUtils.warning("No symbols provided for batch analysis")
            return {}
        
        self._total_count = len(symbols)
        self._completed_count = 0
        self._failed_count = 0
        
        results: Dict[str, Dict[str, Any]] = {}
        failed_symbols: List[str] = []
        
        DebugUtils.info(f"Starting parallel analysis of {len(symbols)} stocks with {self.max_workers} workers")
        
        start_time = time.time()
        
        # Use ThreadPoolExecutor for I/O-bound operations (API calls)
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_symbol: Dict[Future, str] = {
                executor.submit(self._analyze_with_rate_limit, analysis_func, symbol): symbol
                for symbol in symbols
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    result = future.result(timeout=300)  # 5 minute timeout per stock
                    
                    if result.get('status') == 'success':
                        results[symbol] = result
                        with self.progress_lock:
                            self._completed_count += 1
                    else:
                        failed_symbols.append(symbol)
                        results[symbol] = result
                        with self.progress_lock:
                            self._failed_count += 1
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback(
                            self._completed_count + self._failed_count,
                            self._total_count,
                            symbol
                        )
                    
                    DebugUtils.debug(f"Completed analysis for {symbol}: {result.get('status', 'unknown')}")
                    
                except Exception as e:
                    failed_symbols.append(symbol)
                    error_result = {
                        'symbol': symbol,
                        'status': 'error',
                        'error': str(e),
                        'analysis_date': datetime.now().isoformat()
                    }
                    results[symbol] = error_result
                    
                    with self.progress_lock:
                        self._failed_count += 1
                    
                    DebugUtils.log_error(e, f"Error analyzing {symbol} in parallel batch")
        
        elapsed_time = time.time() - start_time
        
        DebugUtils.info(
            f"Parallel analysis completed: {self._completed_count} successful, "
            f"{self._failed_count} failed, {elapsed_time:.2f}s elapsed "
            f"({len(symbols)/elapsed_time:.2f} stocks/sec)"
        )
        
        return results
    
    def _analyze_with_rate_limit(
        self,
        analysis_func: Callable[[str], Dict[str, Any]],
        symbol: str
    ) -> Dict[str, Any]:
        """
        Execute analysis function with rate limiting.
        
        Args:
            analysis_func: Function to execute
            symbol: Stock symbol to analyze
            
        Returns:
            Analysis result dictionary
        """
        # Acquire semaphore for rate limiting
        with self.rate_limiter:
            try:
                # Small delay to prevent API hammering
                time.sleep(API_REQUEST_DELAY)
                
                # Execute analysis
                result = analysis_func(symbol)
                return result
                
            except Exception as e:
                DebugUtils.log_error(e, f"Error in rate-limited analysis for {symbol}")
                return {
                    'symbol': symbol,
                    'status': 'error',
                    'error': str(e),
                    'analysis_date': datetime.now().isoformat()
                }
    
    def calculate_indicators_parallel(
        self,
        data_list: List[Any],
        calculation_func: Callable[[Any], Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate indicators in parallel for multiple stocks (CPU-bound).
        
        Args:
            data_list: List of data objects to process
            calculation_func: Function to calculate indicators (takes data, returns dict)
            
        Returns:
            List of calculation results
        """
        if not data_list:
            return []
        
        # Use ProcessPoolExecutor for CPU-bound operations
        cpu_count = mp.cpu_count()
        max_workers = min(cpu_count, len(data_list), 8)  # Cap at 8 processes
        
        DebugUtils.info(f"Calculating indicators in parallel with {max_workers} processes")
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(calculation_func, data_list))
        
        DebugUtils.info(f"Completed parallel indicator calculations for {len(results)} items")
        return results
    
    def get_progress(self) -> Dict[str, int]:
        """
        Get current progress statistics.
        
        Returns:
            Dictionary with completed, failed, and total counts
        """
        with self.progress_lock:
            return {
                'completed': self._completed_count,
                'failed': self._failed_count,
                'total': self._total_count,
                'remaining': self._total_count - self._completed_count - self._failed_count
            }
    
    def reset_progress(self) -> None:
        """Reset progress counters."""
        with self.progress_lock:
            self._completed_count = 0
            self._failed_count = 0
            self._total_count = 0

