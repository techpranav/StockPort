import traceback
from typing import Dict, Any, Optional, List
from pathlib import Path
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from services.yahoo_finance.yahoo_finance_service import YahooFinanceService
from services.ai_service import AIService
from services.stock_service import StockService
from services.report_service import ReportService
from utils.file_utils import FileUtils
from utils.drive_utils import DriveUtils
from core.config import (
    ENABLE_AI_FEATURES,
    ENABLE_GOOGLE_DRIVE,
    INPUT_DIR,
    OUTPUT_DIR
)
from constants.StringConstants import (
    STOCK_FILE,
    COMPLETED_FILE,
    FAILED_FILE
)
from models.stock_data import (
    StockData, CompanyInfo, FinancialMetrics, TechnicalIndicators,
    TechnicalSignals, FinancialStatements, NewsItem
)
from exceptions.stock_data_exceptions import DataAnalysisException
from utils.debug_utils import DebugUtils

class StockAnalyzer:
    def __init__(self, input_dir: str, output_dir: str, ai_mode: str = None, days_back: int = 365, delay_between_calls: int = 60):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.ai_mode = ai_mode
        self.days_back = days_back
        self.delay_between_calls = delay_between_calls
        
        # Initialize services
        self.stock_service = StockService()
        self.ai_service = AIService(ai_mode=ai_mode) if ai_mode else None
        self.report_service = ReportService()
        self.file_utils = FileUtils(input_dir=str(self.input_dir), output_dir=str(self.output_dir))
        self.drive_utils = DriveUtils() if ENABLE_GOOGLE_DRIVE else None
        
        # Create directories if they don't exist
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def process_stock(self, symbol: str) -> Dict[str, Any]:
        """Process a single stock symbol."""
        try:
            # Fetch standardized stock data
            stock_data = self.stock_service.fetch_stock_data(symbol)
            DebugUtils.info(f"Successfully fetched standardized data for {symbol}")
            
            # Convert StockData to dictionary format for legacy compatibility
            stock_dict = stock_data.to_dict()
            
            # Save filtered data (using legacy format for now)
            self.file_utils.save_filtered_data(symbol, stock_dict, self.output_dir)
            
            # Generate reports
            word_report_path = self.report_service.generate_word_report(symbol, stock_dict)
            excel_report_path = self.report_service.generate_excel_report(symbol, stock_dict)
            
            # Upload to Google Drive if enabled
            if ENABLE_GOOGLE_DRIVE:
                self.drive_utils.upload_file(word_report_path)
                self.drive_utils.upload_file(excel_report_path)
            
            # Get AI summary if enabled
            summary = None
            if ENABLE_AI_FEATURES and self.ai_service:
                summary = self.ai_service.get_stock_summary(symbol, stock_dict)

            # Return data in a format compatible with the UI
            return {
                'symbol': symbol,
                'status': 'success',
                'history': stock_data.raw_data.get('history', pd.DataFrame()),
                'company_info': stock_data.company_info.__dict__,
                'info': stock_data.raw_data.get('info', {}),
                'financials': stock_data.raw_data.get('financials', {}),
                'metrics': stock_data.metrics.__dict__,
                'technical_analysis': stock_data.technical_analysis.__dict__,
                'technical_signals': stock_data.technical_signals.__dict__,
                'filtered_data': stock_dict,
                'word_report_path': str(word_report_path),
                'excel_report_path': str(excel_report_path),
                'summary': summary,
                'stock_data_object': stock_data  # Include the full StockData object for future use
            }
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error processing {symbol}")
            return {
                'symbol': symbol,
                'status': 'error',
                'error': str(e),
                'history': pd.DataFrame(),
                'info': {},
                'financials': {},
                'metrics': {},
                'technical_analysis': {},
                'technical_signals': {},
                'filtered_data': {},
                'word_report_path': None,
                'excel_report_path': None,
                'summary': None
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