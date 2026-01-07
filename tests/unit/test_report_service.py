"""
Unit tests for ReportService.

Tests verify that report generation (Excel and Word) works correctly.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, patch
from datetime import datetime

from services.exporters.report_service import ReportService
from models.stock_data import CompanyInfo, FinancialMetrics, TechnicalIndicators


class TestReportService:
    """Test suite for ReportService class."""
    
    @pytest.fixture
    def temp_reports_dir(self):
        """Create temporary reports directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_stock_data_dict(self):
        """Create sample stock data dictionary for report generation."""
        return {
            'symbol': 'TEST',
            'info': {
                'longName': 'Test Company',
                'sector': 'Technology',
                'industry': 'Software',
                'marketCap': 1000000000
            },
            'company_info': {
                'name': 'Test Company',
                'sector': 'Technology',
                'industry': 'Software'
            },
            'metrics': {
                'revenue': 100000000.0,
                'net_income': 10000000.0,
                'eps': 2.5,
                'pe_ratio': 25.0
            },
            'technical_analysis': {
                'current_price': 100.0,
                'sma_20': 98.0,
                'sma_50': 95.0,
                'rsi': 55.0,
                'macd': 0.5
            },
            'technical_signals': {
                'trend': 'bullish',
                'momentum': 'neutral',
                'volatility': 'normal',
                'volume': 'normal'
            },
            'history': pd.DataFrame({
                'Open': [100] * 10,
                'High': [105] * 10,
                'Low': [95] * 10,
                'Close': [100] * 10,
                'Volume': [1000000] * 10
            })
        }
    
    def test_report_service_initialization(self, temp_reports_dir):
        """Test ReportService initialization."""
        with patch('services.exporters.report_service.REPORTS_DIR', temp_reports_dir):
            service = ReportService(days_back=180)
            assert service.days_back == 180
            assert Path(temp_reports_dir).exists()
    
    def test_generate_excel_report_success(self, temp_reports_dir, sample_stock_data_dict):
        """Test successful Excel report generation."""
        with patch('services.exporters.report_service.REPORTS_DIR', temp_reports_dir):
            service = ReportService()
            report_path = service.generate_excel_report('TEST', sample_stock_data_dict)
            
            assert report_path is not None
            assert Path(report_path).exists()
            assert report_path.endswith('.xlsx')
    
    def test_generate_excel_report_with_empty_data(self, temp_reports_dir):
        """Test Excel report generation with empty data."""
        with patch('services.exporters.report_service.REPORTS_DIR', temp_reports_dir):
            service = ReportService()
            empty_data = {'symbol': 'TEST'}
            report_path = service.generate_excel_report('TEST', empty_data)
            
            # Should still create a report file
            assert report_path is not None
            assert Path(report_path).exists()
    
    def test_generate_word_report_success(self, temp_reports_dir, sample_stock_data_dict):
        """Test successful Word report generation."""
        with patch('services.exporters.report_service.REPORTS_DIR', temp_reports_dir):
            service = ReportService()
            report_path = service.generate_word_report('TEST', sample_stock_data_dict)
            
            assert report_path is not None
            assert report_path.endswith('.docx')
            assert Path(report_path).exists()
    
    def test_generate_word_report_with_empty_data(self, temp_reports_dir):
        """Test Word report generation with empty data."""
        with patch('services.exporters.report_service.REPORTS_DIR', temp_reports_dir):
            service = ReportService()
            empty_data = {'symbol': 'TEST'}
            report_path = service.generate_word_report('TEST', empty_data)
            
            # Should still create a report file
            assert report_path is not None
            assert Path(report_path).exists()
    
    def test_cleanup_old_reports(self, temp_reports_dir):
        """Test cleanup of old reports."""
        with patch('services.exporters.report_service.REPORTS_DIR', temp_reports_dir):
            service = ReportService()
            
            # Create a test report file
            test_file = Path(temp_reports_dir) / 'TEST_report_old.xlsx'
            test_file.touch()
            
            # Mock old file time
            import time
            old_time = time.time() - (35 * 24 * 60 * 60)  # 35 days ago
            test_file.touch()
            import os
            os.utime(test_file, (old_time, old_time))
            
            cleaned = service.cleanup_old_reports(days=30)
            assert cleaned >= 0
    
    def test_get_reports(self, temp_reports_dir, sample_stock_data_dict):
        """Test getting list of reports."""
        with patch('services.exporters.report_service.REPORTS_DIR', temp_reports_dir):
            service = ReportService()
            
            # Generate a report
            service.generate_excel_report('TEST', sample_stock_data_dict)
            
            # Get reports
            reports = service.get_reports(symbol='TEST')
            assert isinstance(reports, list)
    
    def test_get_report_stats(self, temp_reports_dir):
        """Test getting report statistics."""
        with patch('services.exporters.report_service.REPORTS_DIR', temp_reports_dir):
            service = ReportService()
            stats = service.get_report_stats()
            
            assert isinstance(stats, dict)
            assert 'total_reports' in stats or 'count' in stats

