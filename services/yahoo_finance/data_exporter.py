from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
import os
from datetime import datetime
from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import ExportException
from config.settings import Settings

# Type aliases
FinancialData = Dict[str, pd.DataFrame]
ExportResult = Dict[str, Any]

class DataExporter:
    """Class for exporting stock data to various formats."""
    
    @staticmethod
    def export_to_excel(
        symbol: str,
        data: FinancialData,
        filename: Optional[str] = None
    ) -> str:
        """
        Export stock data to Excel file.
        
        Args:
            symbol: Stock symbol
            data: Dictionary containing financial data
            filename: Optional custom filename
            
        Returns:
            Path to the exported file
            
        Raises:
            ExportException: If there's an error exporting the data
        """
        try:
            # Create export directory if it doesn't exist
            os.makedirs(Settings.EXPORT_DIR, exist_ok=True)
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{symbol}_financials_{timestamp}.xlsx"
            
            filepath = os.path.join(Settings.EXPORT_DIR, filename)
            
            # Create Excel writer
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Export each financial statement
                for statement_name, statement_data in data.items():
                    if not statement_data.empty:
                        statement_data.to_excel(writer, sheet_name=statement_name)
            
            DebugUtils.info(f"Successfully exported data to {filepath}")
            return filepath
            
        except Exception as e:
            raise ExportException(f"Error exporting data to Excel: {str(e)}")
    
    @staticmethod
    def export_filtered_financials(
        symbol: str,
        data: FinancialData,
        export: bool = False
    ) -> ExportResult:
        """
        Export filtered financial data based on specified criteria.
        
        Args:
            symbol: Stock symbol
            data: Dictionary containing financial data
            export: Whether to export the filtered data to Excel
            
        Returns:
            Dictionary containing filtered financial data
        """
        filtered_data: ExportResult = {
            'income_statement': pd.DataFrame(),
            'balance_sheet': pd.DataFrame(),
            'cashflow': pd.DataFrame()
        }
        
        try:
            # Filter income statement
            if 'income_statement' in data:
                income_stmt = data['income_statement']
                filtered_data['income_statement'] = income_stmt[
                    income_stmt.index.isin([
                        'Total Revenue',
                        'Gross Profit',
                        'Operating Income',
                        'Net Income',
                        'Earnings Per Share'
                    ])
                ]
            
            # Filter balance sheet
            if 'balance_sheet' in data:
                balance_sheet = data['balance_sheet']
                filtered_data['balance_sheet'] = balance_sheet[
                    balance_sheet.index.isin([
                        'Total Assets',
                        'Current Assets',
                        'Total Liabilities',
                        'Total Current Liabilities',
                        'Stockholders Equity'
                    ])
                ]
            
            # Filter cash flow
            if 'cashflow' in data:
                cashflow = data['cashflow']
                filtered_data['cashflow'] = cashflow[
                    cashflow.index.isin([
                        'Operating Cash Flow',
                        'Investing Cash Flow',
                        'Financing Cash Flow',
                        'Free Cash Flow'
                    ])
                ]
            
            # Export if requested
            if export:
                DataExporter.export_to_excel(symbol, filtered_data)
            
            return filtered_data
            
        except Exception as e:
            DebugUtils.error(f"Error filtering financial data: {str(e)}")
            return filtered_data
    
    @staticmethod
    def export_technical_analysis(
        symbol: str,
        data: pd.DataFrame,
        indicators: Dict[str, pd.Series]
    ) -> str:
        """
        Export technical analysis data to Excel.
        
        Args:
            symbol: Stock symbol
            data: DataFrame containing price data
            indicators: Dictionary containing technical indicators
            
        Returns:
            Path to the exported file
        """
        try:
            # Create export directory if it doesn't exist
            os.makedirs(Settings.EXPORT_DIR, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{symbol}_technical_analysis_{timestamp}.xlsx"
            filepath = os.path.join(Settings.EXPORT_DIR, filename)
            
            # Create Excel writer
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Export price data
                data.to_excel(writer, sheet_name='Price Data')
                
                # Export indicators
                for indicator_name, indicator_data in indicators.items():
                    indicator_data.to_excel(writer, sheet_name=indicator_name)
            
            DebugUtils.info(f"Successfully exported technical analysis to {filepath}")
            return filepath
            
        except Exception as e:
            DebugUtils.error(f"Error exporting technical analysis: {str(e)}")
            return "" 