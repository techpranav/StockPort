"""
Stock Analyzer Core Module

This module provides the core functionality for analyzing stock data.
It coordinates between different services to fetch, analyze, and export stock data.
"""

import traceback
from typing import Dict, Any, Optional, List
from pathlib import Path
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from services.stock_service import StockService
from services.exporters.report_service import ReportService
from utils.file_utils import FileUtils
from utils.google_drive_utils import GoogleDriveManager
from utils.debug_utils import DebugUtils

from config.constants.StringConstants import (
    STOCK_FILE,
    COMPLETED_FILE,
    FAILED_FILE,
    TEMP_STOCKS_FILE
)
from models.stock_data import (
    StockData, CompanyInfo, FinancialMetrics, TechnicalIndicators,
    TechnicalSignals, FinancialStatements, NewsItem
)
from exceptions.stock_data_exceptions import DataAnalysisException

from config.settings import ENABLE_GOOGLE_DRIVE

class StockAnalyzer:
    def __init__(self, input_dir: str, output_dir: str, ai_mode: str = None, days_back: int = 365, delay_between_calls: int = 60):
        """Initialize the stock analyzer."""
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.ai_mode = ai_mode
        self.days_back = days_back
        self.delay_between_calls = delay_between_calls
        
        # Create directories if they don't exist
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize services with days_back parameter
        self.stock_service = StockService(days_back=days_back)
        self.report_service = ReportService(days_back=days_back)
        self.file_utils = FileUtils(str(self.input_dir), str(self.output_dir))
        
        # Initialize Google Drive if enabled
        if ENABLE_GOOGLE_DRIVE:
            self.drive_utils = GoogleDriveManager()
        
        DebugUtils.info(f"Initialized StockAnalyzer with days_back={days_back}, delay_between_calls={delay_between_calls}")
    
    def process_stock(self, symbol: str) -> Dict[str, Any]:
        """Process a single stock symbol."""
        try:
            DebugUtils.info(f"Processing stock: {symbol} with {self.days_back} days of historical data")
            
            # Fetch standardized stock data
            stock_data = self.stock_service.fetch_stock_data(symbol)
            DebugUtils.info(f"Successfully fetched standardized data for {symbol}")
            
            # Convert StockData to dictionary format for legacy compatibility
            stock_dict = stock_data.to_dict()
            
            # Save filtered data (using legacy format for now)
            self.file_utils.save_filtered_data(symbol, stock_dict, self.output_dir)
            
            # Generate reports with days_back information
            word_report_path = self.report_service.generate_word_report(symbol, stock_dict, days_back=self.days_back)
            excel_report_path = self.report_service.generate_excel_report(symbol, stock_dict, days_back=self.days_back)
            
            # Upload to Google Drive if enabled
            if ENABLE_GOOGLE_DRIVE:
                self.drive_utils.upload_file(word_report_path)
                self.drive_utils.upload_file(excel_report_path)
            
            # Return comprehensive result
            result = {
                'symbol': symbol,
                'status': 'success',
                'word_report_path': word_report_path,
                'excel_report_path': excel_report_path,
                'analysis_date': datetime.now().isoformat(),
                'days_back': self.days_back,
                'data_summary': {
                    'has_history': not stock_dict.get('history', pd.DataFrame()).empty,
                    'has_financials': bool(stock_dict.get('financials')),
                    'has_company_info': bool(stock_dict.get('info')),
                    'has_news': bool(stock_dict.get('news'))
                },
                **stock_dict,  # Include all stock data
                'stock_data_object': stock_data  # Include the full StockData object for future use
            }
            
            DebugUtils.info(f"Successfully processed stock: {symbol}")
            return result
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error processing stock: {symbol}")
            return {
                'symbol': symbol,
                'status': 'error',
                'error': str(e),
                'analysis_date': datetime.now().isoformat(),
                'days_back': self.days_back
            }
    
    def process_multiple_stocks(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Process multiple stock symbols."""
        results = []
        for symbol in symbols:
            try:
                result = self.process_stock(symbol.decode().strip())
                results.append(result)
                time.sleep(self.delay_between_calls)
            except Exception as e:
                print(f"Error processing {symbol}: {str(e)}")
        return results
    
    def read_stock_symbols(self) -> List[str]:
        """Read stock symbols from the stock file."""
        stock_file = self.input_dir / STOCK_FILE
        if not stock_file.exists():
            return []
        
        with open(stock_file, 'r') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    
    def update_stock_symbols(self, symbols: List[str]) -> None:
        """Update the stock symbols file."""
        stock_file = self.input_dir / STOCK_FILE
        with open(stock_file, 'w') as f:
            f.write('\n'.join(symbols))
    
    def append_completed_symbol(self, symbol: str) -> None:
        """Append a completed symbol to the completed file."""
        completed_file = self.input_dir / COMPLETED_FILE
        with open(completed_file, 'a') as f:
            f.write(f"{symbol}\n")
    
    def append_failed_symbol(self, symbol: str) -> None:
        """Append a failed symbol to the failed file."""
        failed_file = self.input_dir / FAILED_FILE
        with open(failed_file, 'a') as f:
            f.write(f"{symbol}\n")
    
    def cleanup_old_reports(self, days: int = 30) -> None:
        """Clean up reports older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        for report_file in self.output_dir.glob("*.docx"):
            if report_file.stat().st_mtime < cutoff_date.timestamp():
                report_file.unlink()
        for report_file in self.output_dir.glob("*.xlsx"):
            if report_file.stat().st_mtime < cutoff_date.timestamp():
                report_file.unlink() 