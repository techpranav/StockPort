"""
Integration tests for StockAnalyzer core functionality.

Tests verify end-to-end stock analysis workflow.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil

from core.stock_analyzer import StockAnalyzer
from models.stock_data import (
    StockData, CompanyInfo, FinancialMetrics, TechnicalIndicators,
    TechnicalSignals, FinancialStatements, NewsItem
)
import pandas as pd


class TestStockAnalyzer:
    """Test suite for StockAnalyzer class."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        input_dir = tempfile.mkdtemp()
        output_dir = tempfile.mkdtemp()
        yield input_dir, output_dir
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_stock_data(self):
        """Create sample stock data for testing."""
        from models.stock_data import TechnicalSignals, FinancialStatements, NewsItem
        
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        history = pd.DataFrame({
            'Open': [100] * 100,
            'High': [105] * 100,
            'Low': [95] * 100,
            'Close': [100] * 100,
            'Volume': [1000000] * 100
        }, index=dates)
        
        company_info = CompanyInfo(
            symbol="TEST",
            name="Test Company",
            sector="Technology"
        )
        
        financial_metrics = FinancialMetrics(
            revenue=100000000.0,
            net_income=10000000.0
        )
        
        technical_indicators = TechnicalIndicators(
            current_price=100.0
        )
        
        technical_signals = TechnicalSignals()
        financial_statements = FinancialStatements()
        
        return StockData(
            symbol="TEST",
            company_info=company_info,
            info={},
            metrics=financial_metrics,
            technical_analysis=technical_indicators,
            technical_signals=technical_signals,
            financials=financial_statements,
            news=[],
            raw_data={'history': history}
        )
    
    def test_stock_analyzer_initialization(self, temp_dirs):
        """Test StockAnalyzer initialization."""
        input_dir, output_dir = temp_dirs
        analyzer = StockAnalyzer(input_dir, output_dir, days_back=180)
        
        assert analyzer.input_dir == Path(input_dir)
        assert analyzer.output_dir == Path(output_dir)
        assert analyzer.days_back == 180
        assert analyzer.delay_between_calls == 60
    
    def test_process_stock_success(self, temp_dirs, sample_stock_data):
        """Test successful stock processing."""
        input_dir, output_dir = temp_dirs
        
        with patch('core.stock_analyzer.StockService') as mock_service_class:
            mock_service = Mock()
            mock_service.fetch_stock_data.return_value = sample_stock_data
            mock_service_class.return_value = mock_service
            
            with patch('core.stock_analyzer.ReportService') as mock_report_class:
                mock_report = Mock()
                mock_report.generate_word_report.return_value = None
                mock_report.generate_excel_report.return_value = None
                mock_report_class.return_value = mock_report
                
                analyzer = StockAnalyzer(input_dir, output_dir)
                result = analyzer.process_stock("TEST")
                
                assert result['symbol'] == "TEST"
                assert result['status'] == 'success'
                assert 'analysis_date' in result
                assert 'days_back' in result
    
    def test_process_stock_failure(self, temp_dirs):
        """Test stock processing failure handling."""
        input_dir, output_dir = temp_dirs
        
        with patch('core.stock_analyzer.StockService') as mock_service_class:
            mock_service = Mock()
            mock_service.fetch_stock_data.side_effect = Exception("API Error")
            mock_service_class.return_value = mock_service
            
            analyzer = StockAnalyzer(input_dir, output_dir)
            result = analyzer.process_stock("INVALID")
            
            assert result['symbol'] == "INVALID"
            assert result['status'] == 'error'
            assert 'error' in result
    
    def test_read_stock_symbols(self, temp_dirs):
        """Test reading stock symbols from file."""
        input_dir, output_dir = temp_dirs
        
        # Create stock file
        stock_file = Path(input_dir) / "stocks.txt"
        stock_file.write_text("AAPL\nMSFT\nGOOGL\n")
        
        analyzer = StockAnalyzer(input_dir, output_dir)
        symbols = analyzer.read_stock_symbols()
        
        assert len(symbols) == 3
        assert "AAPL" in symbols
        assert "MSFT" in symbols
        assert "GOOGL" in symbols
    
    def test_read_stock_symbols_empty_file(self, temp_dirs):
        """Test reading stock symbols from empty file."""
        input_dir, output_dir = temp_dirs
        
        analyzer = StockAnalyzer(input_dir, output_dir)
        symbols = analyzer.read_stock_symbols()
        
        assert symbols == []
    
    def test_update_stock_symbols(self, temp_dirs):
        """Test updating stock symbols file."""
        input_dir, output_dir = temp_dirs
        
        analyzer = StockAnalyzer(input_dir, output_dir)
        analyzer.update_stock_symbols(["AAPL", "MSFT", "GOOGL"])
        
        symbols = analyzer.read_stock_symbols()
        assert len(symbols) == 3
        assert "AAPL" in symbols
    
    def test_append_completed_symbol(self, temp_dirs):
        """Test appending completed symbol."""
        input_dir, output_dir = temp_dirs
        
        analyzer = StockAnalyzer(input_dir, output_dir)
        analyzer.append_completed_symbol("AAPL")
        
        completed_file = Path(input_dir) / "completed.txt"
        assert completed_file.exists()
        content = completed_file.read_text()
        assert "AAPL" in content
    
    def test_append_failed_symbol(self, temp_dirs):
        """Test appending failed symbol."""
        input_dir, output_dir = temp_dirs
        
        analyzer = StockAnalyzer(input_dir, output_dir)
        analyzer.append_failed_symbol("INVALID")
        
        failed_file = Path(input_dir) / "failed.txt"
        assert failed_file.exists()
        content = failed_file.read_text()
        assert "INVALID" in content

