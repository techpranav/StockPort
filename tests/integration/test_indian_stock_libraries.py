"""
Test Indian Stock Libraries

This script tests different libraries for Indian stock data support.
Tests historical data, live data, data completeness, and stability.
"""

import pandas as pd
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from utils.debug_utils import DebugUtils

# Test results structure
class LibraryTestResult:
    """Results from testing a library."""
    def __init__(self, library_name: str):
        self.library_name = library_name
        self.historical_data_available = False
        self.live_data_available = False
        self.data_completeness = {}  # OHLCV availability
        self.stability_score = 0.0  # 0-100
        self.error_messages = []
        self.test_symbols = []
        self.recommended_for = []  # ['historical', 'live', 'both']
        self.rate_limits = {}
        self.data_format = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'library_name': self.library_name,
            'historical_data_available': self.historical_data_available,
            'live_data_available': self.live_data_available,
            'data_completeness': self.data_completeness,
            'stability_score': self.stability_score,
            'error_messages': self.error_messages,
            'test_symbols': self.test_symbols,
            'recommended_for': self.recommended_for,
            'rate_limits': self.rate_limits,
            'data_format': self.data_format
        }


class IndianStockLibraryTester:
    """Test different libraries for Indian stock data."""
    
    def __init__(self):
        """Initialize tester."""
        self.test_symbols = {
            'NSE': ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS'],
            'BSE': ['RELIANCE.BO', 'TCS.BO']
        }
        self.results: List[LibraryTestResult] = []
    
    def test_all_libraries(self) -> List[Dict[str, Any]]:
        """
        Test all available libraries for Indian stock support.
        
        Returns:
            List of test results
        """
        DebugUtils.info("Starting Indian stock library testing")
        
        # Test yfinance with .NS suffix
        self._test_yfinance()
        
        # Test other libraries if available
        self._test_nsepy()
        self._test_nsetools()
        self._test_investpy()
        self._test_pandas_datareader()
        
        # Return results
        return [r.to_dict() for r in self.results]
    
    def _test_yfinance(self) -> None:
        """Test yfinance library for Indian stocks."""
        result = LibraryTestResult('yfinance')
        result.test_symbols = self.test_symbols['NSE'][:2]  # Test first 2
        
        try:
            import yfinance as yf
            
            # Test historical data
            try:
                symbol = 'RELIANCE.NS'
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1mo', interval='1d')
                
                if not hist.empty:
                    result.historical_data_available = True
                    result.data_completeness = {
                        'Open': 'Open' in hist.columns,
                        'High': 'High' in hist.columns,
                        'Low': 'Low' in hist.columns,
                        'Close': 'Close' in hist.columns,
                        'Volume': 'Volume' in hist.columns
                    }
                    result.data_format = {
                        'index_type': str(type(hist.index)),
                        'columns': list(hist.columns),
                        'sample_rows': len(hist)
                    }
                    result.stability_score += 30
                    DebugUtils.info(f"yfinance: Historical data available for {symbol}")
                else:
                    result.error_messages.append("Historical data returned empty DataFrame")
            except Exception as e:
                result.error_messages.append(f"Historical data error: {str(e)}")
                DebugUtils.warning(f"yfinance historical data test failed: {e}")
            
            # Test live data (current price)
            try:
                symbol = 'RELIANCE.NS'
                ticker = yf.Ticker(symbol)
                info = ticker.info
                if 'currentPrice' in info or 'regularMarketPrice' in info:
                    result.live_data_available = True
                    result.stability_score += 20
                    DebugUtils.info(f"yfinance: Live data available for {symbol}")
            except Exception as e:
                result.error_messages.append(f"Live data error: {str(e)}")
                DebugUtils.warning(f"yfinance live data test failed: {e}")
            
            # Test intraday data
            try:
                symbol = 'RELIANCE.NS'
                ticker = yf.Ticker(symbol)
                intraday = ticker.history(period='5d', interval='1h')
                if not intraday.empty:
                    result.stability_score += 20
                    DebugUtils.info(f"yfinance: Intraday data available")
            except Exception as e:
                result.error_messages.append(f"Intraday data error: {str(e)}")
            
            # Determine recommendations
            if result.historical_data_available and result.live_data_available:
                result.recommended_for = ['both']
            elif result.historical_data_available:
                result.recommended_for = ['historical']
            elif result.live_data_available:
                result.recommended_for = ['live']
            
            result.stability_score = min(100, result.stability_score)
            
        except ImportError:
            result.error_messages.append("yfinance library not installed")
            DebugUtils.warning("yfinance not available")
        except Exception as e:
            result.error_messages.append(f"General error: {str(e)}")
            DebugUtils.log_error(e, "Error testing yfinance")
        
        self.results.append(result)
    
    def _test_nsepy(self) -> None:
        """Test nsepy library for NSE data."""
        result = LibraryTestResult('nsepy')
        
        try:
            from nsepy import get_history
            from datetime import date
            
            # Test historical data
            try:
                symbol = 'RELIANCE'
                end_date = date.today()
                start_date = end_date - timedelta(days=30)
                
                hist = get_history(
                    symbol=symbol,
                    start=start_date,
                    end=end_date
                )
                
                if not hist.empty:
                    result.historical_data_available = True
                    result.data_completeness = {
                        'Open': 'Open' in hist.columns,
                        'High': 'High' in hist.columns,
                        'Low': 'Low' in hist.columns,
                        'Close': 'Close' in hist.columns,
                        'Volume': 'Volume' in hist.columns
                    }
                    result.data_format = {
                        'index_type': str(type(hist.index)),
                        'columns': list(hist.columns),
                        'sample_rows': len(hist)
                    }
                    result.stability_score = 70
                    result.recommended_for = ['historical']
                    DebugUtils.info(f"nsepy: Historical data available for {symbol}")
                else:
                    result.error_messages.append("Historical data returned empty DataFrame")
            except Exception as e:
                result.error_messages.append(f"Historical data error: {str(e)}")
                DebugUtils.warning(f"nsepy historical data test failed: {e}")
        
        except ImportError:
            result.error_messages.append("nsepy library not installed")
            DebugUtils.warning("nsepy not available")
        except Exception as e:
            result.error_messages.append(f"General error: {str(e)}")
            DebugUtils.log_error(e, "Error testing nsepy")
        
        self.results.append(result)
    
    def _test_nsetools(self) -> None:
        """Test nsetools library for NSE data."""
        result = LibraryTestResult('nsetools')
        
        try:
            from nsetools import Nse
            
            # Test live data
            try:
                nse = Nse()
                quote = nse.get_quote('RELIANCE')
                
                if quote and 'lastPrice' in quote:
                    result.live_data_available = True
                    result.stability_score = 50
                    result.recommended_for = ['live']
                    DebugUtils.info("nsetools: Live data available")
                else:
                    result.error_messages.append("Live data returned empty or invalid")
            except Exception as e:
                result.error_messages.append(f"Live data error: {str(e)}")
                DebugUtils.warning(f"nsetools live data test failed: {e}")
        
        except ImportError:
            result.error_messages.append("nsetools library not installed")
            DebugUtils.warning("nsetools not available")
        except Exception as e:
            result.error_messages.append(f"General error: {str(e)}")
            DebugUtils.log_error(e, "Error testing nsetools")
        
        self.results.append(result)
    
    def _test_investpy(self) -> None:
        """Test investpy library for Indian stock data."""
        result = LibraryTestResult('investpy')
        
        try:
            import investpy
            
            # Test historical data
            try:
                hist = investpy.get_stock_historical_data(
                    stock='Reliance Industries',
                    country='india',
                    from_date='01/01/2024',
                    to_date=datetime.now().strftime('%d/%m/%Y')
                )
                
                if not hist.empty:
                    result.historical_data_available = True
                    result.data_completeness = {
                        'Open': 'Open' in hist.columns,
                        'High': 'High' in hist.columns,
                        'Low': 'Low' in hist.columns,
                        'Close': 'Close' in hist.columns,
                        'Volume': 'Volume' in hist.columns
                    }
                    result.stability_score = 60
                    result.recommended_for = ['historical']
                    DebugUtils.info("investpy: Historical data available")
                else:
                    result.error_messages.append("Historical data returned empty DataFrame")
            except Exception as e:
                result.error_messages.append(f"Historical data error: {str(e)}")
                DebugUtils.warning(f"investpy historical data test failed: {e}")
        
        except ImportError:
            result.error_messages.append("investpy library not installed")
            DebugUtils.warning("investpy not available")
        except Exception as e:
            result.error_messages.append(f"General error: {str(e)}")
            DebugUtils.log_error(e, "Error testing investpy")
        
        self.results.append(result)
    
    def _test_pandas_datareader(self) -> None:
        """Test pandas_datareader for Indian stock data."""
        result = LibraryTestResult('pandas_datareader')
        
        try:
            import pandas_datareader.data as web
            from datetime import datetime, timedelta
            
            # Test with yahoo (supports .NS suffix)
            try:
                symbol = 'RELIANCE.NS'
                end = datetime.now()
                start = end - timedelta(days=30)
                
                hist = web.DataReader(symbol, 'yahoo', start, end)
                
                if not hist.empty:
                    result.historical_data_available = True
                    result.data_completeness = {
                        'Open': 'Open' in hist.columns,
                        'High': 'High' in hist.columns,
                        'Low': 'Low' in hist.columns,
                        'Close': 'Close' in hist.columns,
                        'Volume': 'Volume' in hist.columns
                    }
                    result.stability_score = 40
                    result.recommended_for = ['historical']
                    DebugUtils.info("pandas_datareader: Historical data available")
            except Exception as e:
                result.error_messages.append(f"Historical data error: {str(e)}")
                DebugUtils.warning(f"pandas_datareader test failed: {e}")
        
        except ImportError:
            result.error_messages.append("pandas_datareader library not installed")
            DebugUtils.warning("pandas_datareader not available")
        except Exception as e:
            result.error_messages.append(f"General error: {str(e)}")
            DebugUtils.log_error(e, "Error testing pandas_datareader")
        
        self.results.append(result)
    
    def generate_report(self) -> str:
        """
        Generate a test report.
        
        Returns:
            Formatted report string
        """
        report = ["=" * 80]
        report.append("INDIAN STOCK LIBRARY TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        for result in self.results:
            report.append(f"Library: {result.library_name}")
            report.append("-" * 80)
            report.append(f"  Historical Data: {'✓' if result.historical_data_available else '✗'}")
            report.append(f"  Live Data: {'✓' if result.live_data_available else '✗'}")
            report.append(f"  Stability Score: {result.stability_score}/100")
            report.append(f"  Recommended For: {', '.join(result.recommended_for) if result.recommended_for else 'None'}")
            report.append(f"  Data Completeness: {result.data_completeness}")
            if result.error_messages:
                report.append(f"  Errors: {len(result.error_messages)}")
                for error in result.error_messages[:3]:  # Show first 3 errors
                    report.append(f"    - {error}")
            report.append("")
        
        # Recommendations
        report.append("=" * 80)
        report.append("RECOMMENDATIONS")
        report.append("=" * 80)
        
        best_historical = max(
            [r for r in self.results if r.historical_data_available],
            key=lambda x: x.stability_score,
            default=None
        )
        best_live = max(
            [r for r in self.results if r.live_data_available],
            key=lambda x: x.stability_score,
            default=None
        )
        
        if best_historical:
            report.append(f"Best for Historical Data: {best_historical.library_name} (Score: {best_historical.stability_score})")
        if best_live:
            report.append(f"Best for Live Data: {best_live.library_name} (Score: {best_live.stability_score})")
        
        report.append("=" * 80)
        
        return "\n".join(report)


def run_tests():
    """Run all library tests."""
    tester = IndianStockLibraryTester()
    results = tester.test_all_libraries()
    report = tester.generate_report()
    
    print(report)
    
    # Save report to file
    with open('indian_stock_library_test_report.txt', 'w') as f:
        f.write(report)
    
    DebugUtils.info("Test report saved to indian_stock_library_test_report.txt")
    
    return results


if __name__ == "__main__":
    run_tests()

