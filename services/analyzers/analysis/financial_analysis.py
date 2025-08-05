from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
import numpy as np
from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException
from config.constants import *
from .financial_ratios_analyzer import FinancialRatiosAnalyzer
from .growth_analyzer import GrowthAnalyzer
from .returns_analyzer import ReturnsAnalyzer

# Type aliases
FinancialMetrics = Dict[str, Union[float, str, Dict[str, float]]]
FinancialRatios = Dict[str, float]
GrowthMetrics = Dict[str, float]
ReturnMetrics = Dict[str, float]

class FinancialAnalyzer:
    """Class for financial analysis."""
    
    @staticmethod
    def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate all financial metrics.
        
        Args:
            data: Dictionary containing stock data
            
        Returns:
            Dictionary containing all financial metrics
        """
        metrics = {}
        
        try:
            # Calculate financial ratios
            metrics['ratios'] = FinancialRatiosAnalyzer.calculate_ratios(data.get('financials', {}))
            
            # Analyze growth
            metrics['growth'] = GrowthAnalyzer.analyze_growth(data)
            
            # Calculate returns
            metrics['returns'] = ReturnsAnalyzer.calculate_returns(data)
            
        except Exception as e:
            DebugUtils.error(f"Error calculating financial metrics: {str(e)}")
        
        return metrics
    
    @staticmethod
    def _calculate_financial_ratios(financials: Dict[str, pd.DataFrame]) -> FinancialRatios:
        """
        Calculate financial ratios from financial statements.
        
        Args:
            financials: Dictionary containing financial statements
            
        Returns:
            Dictionary containing calculated financial ratios
        """
        ratios: FinancialRatios = {}
        
        try:
            # Get income statement and balance sheet
            income_stmt = financials.get('yearly', {}).get('income_statement', pd.DataFrame())
            balance_sheet = financials.get('yearly', {}).get('balance_sheet', pd.DataFrame())
            
            if not income_stmt.empty and not balance_sheet.empty:
                # Get most recent year's data
                latest_year = income_stmt.columns[0]
                
                # Calculate ratios
                revenue = income_stmt.loc['Total Revenue', latest_year]
                net_income = income_stmt.loc['Net Income', latest_year]
                total_assets = balance_sheet.loc['Total Assets', latest_year]
                current_assets = balance_sheet.loc['Total Current Assets', latest_year]
                current_liabilities = balance_sheet.loc['Total Current Liabilities', latest_year]
                
                # Profit margin
                ratios['profit_margin'] = (net_income / revenue) if revenue != 0 else 0
                
                # Current ratio
                ratios['current_ratio'] = (current_assets / current_liabilities) if current_liabilities != 0 else 0
                
                # Return on assets
                ratios['roa'] = (net_income / total_assets) if total_assets != 0 else 0
            
            return ratios
            
        except Exception as e:
            DebugUtils.error(f"Error calculating financial ratios: {str(e)}")
            return {}
    
    @staticmethod
    def analyze_growth(data: Dict[str, Any]) -> GrowthMetrics:
        """
        Analyze growth metrics from historical data.
        
        Args:
            data: Dictionary containing stock data including history
            
        Returns:
            Dictionary containing growth metrics
        """
        growth_metrics: GrowthMetrics = {}
        
        try:
            if 'history' in data and not data['history'].empty:
                # Calculate price growth
                prices = data['history']['Close']
                if len(prices) > 1:
                    growth_metrics['price_growth'] = ((prices.iloc[-1] / prices.iloc[0]) - 1) * 100
            
            return growth_metrics
            
        except Exception as e:
            DebugUtils.error(f"Error analyzing growth: {str(e)}")
            return {}
    
    @staticmethod
    def calculate_returns(data: Dict[str, Any]) -> ReturnMetrics:
        """
        Calculate return metrics from historical data.
        
        Args:
            data: Dictionary containing stock data including history
            
        Returns:
            Dictionary containing return metrics
        """
        return_metrics: ReturnMetrics = {}
        
        try:
            if 'history' in data and not data['history'].empty:
                # Calculate daily returns
                prices = data['history']['Close']
                daily_returns = prices.pct_change().dropna()
                
                # Calculate metrics
                return_metrics['daily_return_mean'] = daily_returns.mean() * 100
                return_metrics['daily_return_std'] = daily_returns.std() * 100
                
                # Calculate Sharpe ratio (assuming risk-free rate of 0)
                if return_metrics['daily_return_std'] != 0:
                    return_metrics['sharpe_ratio'] = (return_metrics['daily_return_mean'] / return_metrics['daily_return_std']) * np.sqrt(252)
            
            return return_metrics
            
        except Exception as e:
            DebugUtils.error(f"Error calculating returns: {str(e)}")
            return {} 