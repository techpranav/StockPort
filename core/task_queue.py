"""
Task Queue System Module

This module provides a priority queue system for stock analysis tasks with
batch processing, progress persistence, and result aggregation.
"""

import json
import time
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from datetime import datetime
from queue import PriorityQueue, Queue
from threading import Lock
from enum import IntEnum

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException


class TaskPriority(IntEnum):
    """Task priority levels."""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    URGENT = 0


class TaskQueue:
    """
    Priority queue system for stock analysis tasks.
    
    Features:
    - Priority queue for urgent stocks
    - Batch processing with configurable batch sizes
    - Progress persistence (resume on restart)
    - Result aggregation and streaming
    
    Attributes:
        queue: Priority queue for tasks
        results: Dictionary of completed results
        progress_file: Path to progress persistence file
        lock: Thread lock for thread-safe operations
    """
    
    def __init__(
        self,
        progress_file: Optional[str] = None,
        batch_size: int = 10
    ):
        """
        Initialize task queue.
        
        Args:
            progress_file: Optional path to save/load progress
            batch_size: Default batch size for processing
        """
        self.queue: PriorityQueue = PriorityQueue()
        self.results: Dict[str, Dict[str, Any]] = {}
        self.completed: List[str] = []
        self.failed: List[str] = []
        self.batch_size = batch_size
        self.lock = Lock()
        
        # Progress persistence
        if progress_file:
            self.progress_file = Path(progress_file)
            self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            self.progress_file = None
        
        # Load existing progress if available
        self._load_progress()
        
        DebugUtils.info(f"Initialized TaskQueue with batch_size={batch_size}")
    
    def add_task(
        self,
        symbol: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a task to the queue.
        
        Args:
            symbol: Stock symbol to analyze
            priority: Task priority level
            metadata: Optional metadata for the task
        """
        if symbol in self.completed:
            DebugUtils.debug(f"Symbol {symbol} already completed, skipping")
            return
        
        task = {
            'symbol': symbol,
            'priority': priority,
            'metadata': metadata or {},
            'added_at': datetime.now().isoformat()
        }
        
        # PriorityQueue uses tuple (priority, insertion_order, item)
        # Lower priority number = higher priority
        with self.lock:
            self.queue.put((priority.value, time.time(), task))
        
        DebugUtils.debug(f"Added task for {symbol} with priority {priority.name}")
    
    def add_batch(
        self,
        symbols: List[str],
        priority: TaskPriority = TaskPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add multiple tasks to the queue.
        
        Args:
            symbols: List of stock symbols
            priority: Priority for all tasks
            metadata: Optional metadata for all tasks
        """
        for symbol in symbols:
            self.add_task(symbol, priority, metadata)
        
        DebugUtils.info(f"Added {len(symbols)} tasks to queue")
    
    def get_batch(self, size: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get a batch of tasks from the queue.
        
        Args:
            size: Batch size (defaults to self.batch_size)
            
        Returns:
            List of task dictionaries
        """
        batch_size = size or self.batch_size
        tasks = []
        
        with self.lock:
            for _ in range(min(batch_size, self.queue.qsize())):
                try:
                    _, _, task = self.queue.get_nowait()
                    tasks.append(task)
                except:
                    break
        
        if tasks:
            DebugUtils.debug(f"Retrieved batch of {len(tasks)} tasks from queue")
        
        return tasks
    
    def mark_completed(
        self,
        symbol: str,
        result: Dict[str, Any]
    ) -> None:
        """
        Mark a task as completed and store result.
        
        Args:
            symbol: Stock symbol
            result: Analysis result dictionary
        """
        with self.lock:
            self.results[symbol] = result
            if symbol not in self.completed:
                self.completed.append(symbol)
            
            # Remove from failed list if it was there
            if symbol in self.failed:
                self.failed.remove(symbol)
        
        self._save_progress()
        DebugUtils.debug(f"Marked {symbol} as completed")
    
    def mark_failed(
        self,
        symbol: str,
        error: str
    ) -> None:
        """
        Mark a task as failed.
        
        Args:
            symbol: Stock symbol
            error: Error message
        """
        with self.lock:
            if symbol not in self.failed:
                self.failed.append(symbol)
            
            self.results[symbol] = {
                'symbol': symbol,
                'status': 'error',
                'error': error,
                'analysis_date': datetime.now().isoformat()
            }
        
        self._save_progress()
        DebugUtils.warning(f"Marked {symbol} as failed: {error}")
    
    def get_results(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all completed results.
        
        Returns:
            Dictionary mapping symbol to result
        """
        with self.lock:
            return self.results.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get queue status.
        
        Returns:
            Dictionary with queue statistics
        """
        with self.lock:
            return {
                'queued': self.queue.qsize(),
                'completed': len(self.completed),
                'failed': len(self.failed),
                'total_processed': len(self.completed) + len(self.failed),
                'results_count': len(self.results)
            }
    
    def clear(self) -> None:
        """Clear the queue and results."""
        with self.lock:
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except:
                    break
            
            self.results.clear()
            self.completed.clear()
            self.failed.clear()
        
        if self.progress_file and self.progress_file.exists():
            self.progress_file.unlink()
        
        DebugUtils.info("Cleared task queue and results")
    
    def _save_progress(self) -> None:
        """Save progress to file."""
        if not self.progress_file:
            return
        
        try:
            progress_data = {
                'completed': self.completed,
                'failed': self.failed,
                'results': self.results,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2, default=str)
            
            DebugUtils.debug(f"Saved progress to {self.progress_file}")
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error saving progress to {self.progress_file}")
    
    def _load_progress(self) -> None:
        """Load progress from file."""
        if not self.progress_file or not self.progress_file.exists():
            return
        
        try:
            with open(self.progress_file, 'r') as f:
                progress_data = json.load(f)
            
            self.completed = progress_data.get('completed', [])
            self.failed = progress_data.get('failed', [])
            self.results = progress_data.get('results', {})
            
            DebugUtils.info(
                f"Loaded progress: {len(self.completed)} completed, "
                f"{len(self.failed)} failed"
            )
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error loading progress from {self.progress_file}")
            # Reset on error
            self.completed = []
            self.failed = []
            self.results = {}

