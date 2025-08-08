from typing import Dict, Any
import pandas as pd
from utils.debug_utils import DebugUtils
from .base_analyzer import BaseAnalyzer

class FinancialRatiosAnalyzer(BaseAnalyzer):
    """Class for calculating financial ratios."""
    
    @staticmethod
    def calculate_ratios(financials: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """
        Calculate financial ratios from financial statements.
        
        Args:
            financials: Dictionary containing financial statements
            
        Returns:
            Dictionary containing financial ratios
        """
        ratios = {}
        
        try:
            # Get income statement and balance sheet
            income_stmt = financials.get('yearly', {}).get('income_statement', pd.DataFrame())
            balance_sheet = financials.get('yearly', {}).get('balance_sheet', pd.DataFrame())
            
            if income_stmt.empty or balance_sheet.empty:
                DebugUtils.warning("Missing financial statements for ratio calculation")
                return ratios
            
            # Profitability ratios
            ratios['profit_margin'] = FinancialRatiosAnalyzer._calculate_profit_margin(income_stmt)
            ratios['return_on_equity'] = FinancialRatiosAnalyzer._calculate_roe(income_stmt, balance_sheet)
            ratios['return_on_assets'] = FinancialRatiosAnalyzer._calculate_roa(income_stmt, balance_sheet)
            
            # Liquidity ratios
            ratios['current_ratio'] = FinancialRatiosAnalyzer._calculate_current_ratio(balance_sheet)
            ratios['quick_ratio'] = FinancialRatiosAnalyzer._calculate_quick_ratio(balance_sheet)
            
            # Efficiency ratios
            ratios['asset_turnover'] = FinancialRatiosAnalyzer._calculate_asset_turnover(income_stmt, balance_sheet)
            ratios['inventory_turnover'] = FinancialRatiosAnalyzer._calculate_inventory_turnover(income_stmt, balance_sheet)
            
            # Leverage ratios
            ratios['debt_to_equity'] = FinancialRatiosAnalyzer._calculate_debt_to_equity(balance_sheet)
            ratios['debt_to_assets'] = FinancialRatiosAnalyzer._calculate_debt_to_assets(balance_sheet)
            
        except Exception as e:
            DebugUtils.error(f"Error calculating financial ratios: {str(e)}")
        
        return ratios
    
    @staticmethod
    def _calculate_profit_margin(income_stmt: pd.DataFrame) -> float:
        """Calculate profit margin."""
        try:
            net_income = BaseAnalyzer._get_latest_value(income_stmt, 'Net Income')
            revenue = BaseAnalyzer._get_latest_value(income_stmt, 'Total Revenue')
            if net_income and revenue and revenue != 0:
                return (net_income / revenue) * 100
            return 0.0
        except Exception as e:
            DebugUtils.error(f"Error calculating profit margin: {str(e)}")
            return 0.0
    
    @staticmethod
    def _calculate_roe(income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame) -> float:
        """Calculate return on equity."""
        try:
            net_income = BaseAnalyzer._get_latest_value(income_stmt, 'Net Income')
            total_equity = BaseAnalyzer._get_latest_value(balance_sheet, 'Stockholders Equity')
            if net_income and total_equity and total_equity != 0:
                return (net_income / total_equity) * 100
            return 0.0
        except Exception as e:
            DebugUtils.error(f"Error calculating ROE: {str(e)}")
            return 0.0
    
    @staticmethod
    def _calculate_roa(income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame) -> float:
        """Calculate return on assets."""
        try:
            net_income = BaseAnalyzer._get_latest_value(income_stmt, 'Net Income')
            total_assets = BaseAnalyzer._get_latest_value(balance_sheet, 'Total Assets')
            if net_income and total_assets and total_assets != 0:
                return (net_income / total_assets) * 100
            return 0.0
        except Exception as e:
            DebugUtils.error(f"Error calculating ROA: {str(e)}")
            return 0.0
    
    @staticmethod
    def _calculate_current_ratio(balance_sheet: pd.DataFrame) -> float:
        """Calculate current ratio."""
        try:
            current_assets = BaseAnalyzer._get_latest_value(balance_sheet, 'Current Assets')
            current_liabilities = BaseAnalyzer._get_latest_value(balance_sheet, 'Total Current Liabilities')
            if current_assets and current_liabilities and current_liabilities != 0:
                return current_assets / current_liabilities
            return 0.0
        except Exception as e:
            DebugUtils.error(f"Error calculating current ratio: {str(e)}")
            return 0.0
    
    @staticmethod
    def _calculate_quick_ratio(balance_sheet: pd.DataFrame) -> float:
        """Calculate quick ratio."""
        try:
            current_assets = BaseAnalyzer._get_latest_value(balance_sheet, 'Current Assets')
            inventory = BaseAnalyzer._get_latest_value(balance_sheet, 'Inventory')
            current_liabilities = BaseAnalyzer._get_latest_value(balance_sheet, 'Total Current Liabilities')
            if current_assets and current_liabilities and current_liabilities != 0:
                return (current_assets - (inventory or 0)) / current_liabilities
            return 0.0
        except Exception as e:
            DebugUtils.error(f"Error calculating quick ratio: {str(e)}")
            return 0.0
    
    @staticmethod
    def _calculate_asset_turnover(income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame) -> float:
        """Calculate asset turnover."""
        try:
            revenue = BaseAnalyzer._get_latest_value(income_stmt, 'Total Revenue')
            total_assets = BaseAnalyzer._get_latest_value(balance_sheet, 'Total Assets')
            if revenue and total_assets and total_assets != 0:
                return revenue / total_assets
            return 0.0
        except Exception as e:
            DebugUtils.error(f"Error calculating asset turnover: {str(e)}")
            return 0.0
    
    @staticmethod
    def _calculate_inventory_turnover(income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame) -> float:
        """Calculate inventory turnover."""
        try:
            cogs = BaseAnalyzer._get_latest_value(income_stmt, 'Cost Of Revenue')
            inventory = BaseAnalyzer._get_latest_value(balance_sheet, 'Inventory')
            if cogs and inventory and inventory != 0:
                return cogs / inventory
            return 0.0
        except Exception as e:
            DebugUtils.error(f"Error calculating inventory turnover: {str(e)}")
            return 0.0
    
    @staticmethod
    def _calculate_debt_to_equity(balance_sheet: pd.DataFrame) -> float:
        """Calculate debt to equity ratio."""
        try:
            total_debt = BaseAnalyzer._get_latest_value(balance_sheet, 'Total Debt')
            total_equity = BaseAnalyzer._get_latest_value(balance_sheet, 'Stockholders Equity')
            if total_debt and total_equity and total_equity != 0:
                return total_debt / total_equity
            return 0.0
        except Exception as e:
            DebugUtils.error(f"Error calculating debt to equity ratio: {str(e)}")
            return 0.0
    
    @staticmethod
    def _calculate_debt_to_assets(balance_sheet: pd.DataFrame) -> float:
        """Calculate debt to assets ratio."""
        try:
            total_debt = BaseAnalyzer._get_latest_value(balance_sheet, 'Total Debt')
            total_assets = BaseAnalyzer._get_latest_value(balance_sheet, 'Total Assets')
            if total_debt and total_assets and total_assets != 0:
                return total_debt / total_assets
            return 0.0
        except Exception as e:
            DebugUtils.error(f"Error calculating debt to assets ratio: {str(e)}")
            return 0.0 