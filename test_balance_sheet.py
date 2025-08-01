#!/usr/bin/env python3
"""
Test script to debug balance sheet data fetching and display.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.stock_service import StockService
from utils.debug_utils import DebugUtils

def test_balance_sheet(symbol="AAPL"):
    """Test balance sheet fetching for a specific symbol."""
    print(f"Testing balance sheet data for {symbol}")
    print("="*50)
    
    try:
        # Initialize stock service
        stock_service = StockService()
        
        # Fetch stock data
        print(f"Fetching stock data for {symbol}...")
        stock_data = stock_service.fetch_stock_data(symbol)
        
        print(f"\nStock data fetched successfully!")
        print(f"Symbol: {stock_data.symbol}")
        print(f"Company: {stock_data.company_info.name}")
        
        # Convert to dict to see the balance sheet structure
        stock_dict = stock_data.to_dict()
        
        print(f"\nFinancials structure:")
        if 'financials' in stock_dict:
            financials = stock_dict['financials']
            for period in ['yearly', 'quarterly']:
                if period in financials:
                    print(f"  {period}:")
                    for statement in ['income_statement', 'balance_sheet', 'cashflow']:
                        if statement in financials[period]:
                            df = financials[period][statement]
                            if hasattr(df, 'shape'):
                                print(f"    {statement}: {df.shape} - Empty: {df.empty}")
                            else:
                                print(f"    {statement}: {type(df)}")
        
        return stock_data
        
    except Exception as e:
        print(f"Error testing balance sheet for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Test with AAPL by default, or use command line argument
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    test_balance_sheet(symbol) 