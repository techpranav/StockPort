from typing import Dict, Any, Optional, List
from pathlib import Path
import time
from datetime import datetime, timedelta

from services.yahoo_finance import YahooFinanceService
from services.ai_service import AIService
from services.report_service import ReportService
from utils.file_utils import FileUtils
from utils.drive_utils import DriveUtils
from core.config import (
    ENABLE_AI_FEATURES,
    ENABLE_GOOGLE_DRIVE,
    INPUT_DIR,
    OUTPUT_DIR,
    STOCK_FILE,
    COMPLETED_FILE,
    FAILED_FILE
)

class StockAnalyzer:
    def __init__(self, input_dir: str, output_dir: str, ai_mode: str = None, days_back: int = 365, delay_between_calls: int = 60):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.ai_mode = ai_mode
        self.days_back = days_back
        self.delay_between_calls = delay_between_calls
        
        # Initialize services
        self.yahoo_finance = YahooFinanceService()
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
            # Fetch and filter data
            stock_data = self.yahoo_finance.fetch_stock_data(symbol)
            filtered_data = self.yahoo_finance.filter_stock_data(stock_data)
            
            # Save filtered data
            self.file_utils.save_filtered_data(symbol, filtered_data, self.output_dir)
            
            # Generate reports
            word_report_path = self.report_service.generate_word_report(symbol, filtered_data)
            excel_report_path = self.report_service.generate_excel_report(symbol, filtered_data)
            
            # Upload to Google Drive if enabled
            if ENABLE_GOOGLE_DRIVE:
                self.drive_utils.upload_file(word_report_path)
                self.drive_utils.upload_file(excel_report_path)
            
            # Get AI summary if enabled
            summary = None
            if ENABLE_AI_FEATURES and self.ai_service:
                summary = self.ai_service.get_stock_summary(symbol, filtered_data)
            
            return {
                'symbol': symbol,
                'history': stock_data.get('history'),
                'info': stock_data.get('info'),
                'financials': stock_data.get('financials'),
                'filtered_data': filtered_data,
                'word_report_path': str(word_report_path),
                'excel_report_path': str(excel_report_path),
                'summary': summary,
                'metrics': filtered_data.get('metrics', {})
            }
            
        except Exception as e:
            raise Exception(f"Error processing {symbol}: {str(e)}")
    
    def process_multiple_stocks(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Process multiple stock symbols."""
        results = []
        for symbol in symbols:
            try:
                result = self.process_stock(symbol)
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
            return [line.strip() for line in f if line.strip()]
    
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