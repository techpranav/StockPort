"""
Unit tests for ParallelStockAnalyzer.

Tests verify parallel processing functionality and error handling.
"""

import pytest
import time
from unittest.mock import Mock, patch

from core.parallel_analyzer import ParallelStockAnalyzer


class TestParallelStockAnalyzer:
    """Test suite for ParallelStockAnalyzer class."""
    
    @pytest.fixture
    def parallel_analyzer(self):
        """Create ParallelStockAnalyzer instance."""
        return ParallelStockAnalyzer(max_workers=2)
    
    def test_parallel_analyzer_initialization(self, parallel_analyzer):
        """Test ParallelStockAnalyzer initialization."""
        assert parallel_analyzer is not None
        assert parallel_analyzer.max_workers == 2
        assert parallel_analyzer.rate_limit_per_worker > 0
    
    def test_parallel_analyzer_default_workers(self):
        """Test default worker count calculation."""
        analyzer = ParallelStockAnalyzer(max_workers=None)
        assert analyzer.max_workers > 0
        assert analyzer.max_workers <= 50  # Should be capped
    
    def test_analyze_batch_success(self, parallel_analyzer):
        """Test successful batch analysis."""
        def mock_analysis_func(symbol: str):
            """Mock analysis function."""
            time.sleep(0.1)  # Simulate work
            return {
                'symbol': symbol,
                'status': 'success',
                'data': f'Analysis for {symbol}'
            }
        
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        results = parallel_analyzer.analyze_batch(
            symbols=symbols,
            analysis_func=mock_analysis_func
        )
        
        assert isinstance(results, dict)
        assert len(results) == len(symbols)
        assert 'AAPL' in results
        assert 'MSFT' in results
        assert 'GOOGL' in results
        assert results['AAPL']['status'] == 'success'
    
    def test_analyze_batch_with_failures(self, parallel_analyzer):
        """Test batch analysis with some failures."""
        def mock_analysis_func(symbol: str):
            """Mock analysis function with failures."""
            if symbol == 'INVALID':
                raise Exception("Analysis failed")
            return {
                'symbol': symbol,
                'status': 'success'
            }
        
        symbols = ['AAPL', 'INVALID', 'GOOGL']
        results = parallel_analyzer.analyze_batch(
            symbols=symbols,
            analysis_func=mock_analysis_func
        )
        
        assert isinstance(results, dict)
        # Should handle failures gracefully
        assert 'AAPL' in results
        assert 'GOOGL' in results
    
    def test_analyze_batch_progress_callback(self, parallel_analyzer):
        """Test progress callback functionality."""
        progress_updates = []
        
        def progress_callback(completed: int, total: int, current: str):
            """Progress callback."""
            progress_updates.append((completed, total, current))
        
        def mock_analysis_func(symbol: str):
            """Mock analysis function."""
            time.sleep(0.05)
            return {'symbol': symbol, 'status': 'success'}
        
        symbols = ['AAPL', 'MSFT']
        results = parallel_analyzer.analyze_batch(
            symbols=symbols,
            analysis_func=mock_analysis_func,
            progress_callback=progress_callback
        )
        
        # Progress callback should be called
        assert len(progress_updates) > 0
    
    def test_analyze_batch_empty_symbols(self, parallel_analyzer):
        """Test batch analysis with empty symbol list."""
        def mock_analysis_func(symbol: str):
            return {'symbol': symbol}
        
        results = parallel_analyzer.analyze_batch(
            symbols=[],
            analysis_func=mock_analysis_func
        )
        
        assert isinstance(results, dict)
        assert len(results) == 0
    
    def test_get_progress(self, parallel_analyzer):
        """Test progress tracking."""
        progress = parallel_analyzer.get_progress()
        
        assert isinstance(progress, dict)
        assert 'completed' in progress
        assert 'failed' in progress
        assert 'total' in progress
        assert progress['completed'] >= 0
        assert progress['failed'] >= 0
        assert progress['total'] >= 0

