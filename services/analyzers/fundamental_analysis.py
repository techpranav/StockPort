import traceback

import pandas as pd
import numpy as np
from typing import Dict, Any, List

from utils.debug_utils import DebugUtils
from config.constants import *


class FundamentalAnalysisService:
    def __init__(self):
        """Initialize fundamental analysis service."""
        pass
    
    def _safe_get_financial_value(self, df: pd.DataFrame, key: str, alternatives: List[str] = None) -> float:
        """Safely get a financial value from a DataFrame, trying alternative keys if the primary key is not found."""
        if df.empty:
            DebugUtils.debug(f"DataFrame is empty for key '{key}'")
            return 0.0
        # Try the primary key first
        if key in df.index:
            try:
                value = df.loc[key].iloc[0]
                result = float(value) if pd.notna(value) else 0.0
                return result
            except (IndexError, ValueError, TypeError) as e:
                DebugUtils.error(f"Error extracting value for key '{key}': {e}")
                print(f"❌ Error extracting '{key}': {e}")
        
        # Try alternative keys
        if alternatives:
            DebugUtils.debug(f"Primary key '{key}' not found, trying alternatives: {alternatives}")
            print(f"🔍 Key '{key}' not found, trying alternatives: {alternatives}")
            for alt_key in alternatives:
                if alt_key in df.index:
                    try:
                        value = df.loc[alt_key].iloc[0]
                        result = float(value) if pd.notna(value) else 0.0
                        DebugUtils.debug(f"Found alternative key '{alt_key}' with value: {result}")
                        print(f"✅ Found alternative '{alt_key}' = {result}")
                        return result
                    except (IndexError, ValueError, TypeError) as e:
                        DebugUtils.error(f"Error extracting value for alternative key '{alt_key}': {e}")
                        print(f"❌ Error with alternative '{alt_key}': {e}")
                        continue
        
        # Show available keys for debugging
        available_keys = list(df.index) # Show first 20 keys
        DebugUtils.error(f"❌ Financial key '{key}' not found in DataFrame. Available keys: {available_keys}")
        print(f"❌  Key '{key}' NOT FOUND. Available keys : {available_keys}")
        return 0.0
    
    def calculate_financial_ratios(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Calculate key financial ratios."""
        ratios = {}
        financials = data.get('financials', {})
        
        print(f"\n🔍 STARTING FINANCIAL RATIOS CALCULATION")
        print(f"📊 Data keys available: {list(data.keys())}")
        print(f"💰 Financials keys: {list(financials.keys()) if financials else 'No financials'}")
        
        DebugUtils.debug(f"Calculating financial ratios with data keys: {list(data.keys())}")
        DebugUtils.debug(f"Financials keys: {list(financials.keys()) if financials else 'No financials'}")
        
        # Get financial statements using the actual structure from StockData.to_dict()
        print(f"🔍 Financials keys: {list(financials.keys())}")
        income_statement = financials.get('yearly_income_statement', pd.DataFrame())
        balance_sheet = financials.get('yearly_balance_sheet', pd.DataFrame())
        cash_flow = financials.get('yearly_cash_flow', pd.DataFrame())

        DebugUtils.debug(f"Income statement shape: {income_statement.shape if not income_statement.empty else 'Empty'}")
        DebugUtils.debug(f"Balance sheet shape: {balance_sheet.shape if not balance_sheet.empty else 'Empty'}")
        
        if income_statement.empty or balance_sheet.empty:
            DebugUtils.warning("Missing financial statements for ratio calculation")
            DebugUtils.debug(f"Income statement empty: {income_statement.empty}, Balance sheet empty: {balance_sheet.empty}")
            DebugUtils.debug(f"Available financials keys: {list(financials.keys())}")
            return ratios
        
        DebugUtils.info(f"Calculating financial ratios with {len(income_statement)} income statement rows and {len(balance_sheet)} balance sheet rows")
        
        # Profitability Ratios
        ratios['profitability'] = self._calculate_profitability_ratios(income_statement, balance_sheet)
        DebugUtils.debug(f"Profitability ratios calculated: {ratios['profitability']}")
        
        # Liquidity Ratios
        ratios['liquidity'] = self._calculate_liquidity_ratios(balance_sheet)
        DebugUtils.debug(f"Liquidity ratios calculated: {ratios['liquidity']}")
        
        # Efficiency Ratios
        ratios['efficiency'] = self._calculate_efficiency_ratios(income_statement, balance_sheet)
        DebugUtils.debug(f"Efficiency ratios calculated: {ratios['efficiency']}")
        
        # Debt Ratios
        ratios['debt'] = self._calculate_debt_ratios(balance_sheet)
        DebugUtils.debug(f"Debt ratios calculated: {ratios['debt']}")
        
        # Market Ratios
        ratios['market'] = self._calculate_market_ratios(data.get('info', {}))
        DebugUtils.debug(f"Market ratios calculated: {ratios['market']}")
        
        # Print comprehensive summary
        DebugUtils.info("=== FINANCIAL RATIOS SUMMARY ===")
        print("\n" + "="*50)
        print("🔍 FINANCIAL RATIOS DEBUG SUMMARY")
        print("="*50)
        
        for category, category_ratios in ratios.items():
            DebugUtils.info(f"{category.upper()} RATIOS:")
            print(f"\n📊 {category.upper()} RATIOS:")
            if isinstance(category_ratios, dict):
                for ratio_name, ratio_value in category_ratios.items():
                    DebugUtils.info(f"  {ratio_name}: {ratio_value}")
                    print(f"   {ratio_name}: {ratio_value}")
            else:
                DebugUtils.info(f"  {category}: {category_ratios}")
                print(f"   {category}: {category_ratios}")
        
        DebugUtils.info("=== END RATIOS SUMMARY ===")
        print("="*50)
        print("🔍 END RATIOS SUMMARY")
        print("="*50 + "\n")
        
        # Flatten ratios for UI compatibility
        flattened_ratios = {}
        for category, category_ratios in ratios.items():
            if isinstance(category_ratios, dict):
                flattened_ratios.update(category_ratios)
            else:
                flattened_ratios[category] = category_ratios
        
        print(f"🔄 FLATTENED RATIOS FOR UI: {flattened_ratios}")
        
        return flattened_ratios
    
    def _calculate_profitability_ratios(self, income_statement: pd.DataFrame, balance_sheet: pd.DataFrame) -> Dict[str, float]:
        """Calculate profitability ratios."""
        ratios = {}
        
        DebugUtils.debug(f"Calculating profitability ratios with income statement shape: {income_statement.shape}, balance sheet shape: {balance_sheet.shape}")
        
        try:
            # Return on Equity (ROE)
            net_income = self._safe_get_financial_value(
                income_statement, 
                STR_NET_INCOME
            )
            total_equity = self._safe_get_financial_value(
                balance_sheet, 
                STR_TOTAL_STOCKHOLDER_EQUITY
            )
            DebugUtils.debug(f"ROE calculation: net_income={net_income}, total_equity={total_equity}")
            ratios['roe'] = (net_income / total_equity) * 100 if total_equity != 0 else 0
            
            # Return on Assets (ROA)
            total_assets = self._safe_get_financial_value(
                balance_sheet, 
                STR_TOTAL_ASSETS
            )
            DebugUtils.debug(f"ROA calculation: net_income={net_income}, total_assets={total_assets}")
            ratios['roa'] = (net_income / total_assets) * 100 if total_assets != 0 else 0
            
            # Gross Profit Margin
            gross_profit = self._safe_get_financial_value(
                income_statement, 
                STR_GROSS_PROFIT
            )
            revenue = self._safe_get_financial_value(
                income_statement,
                STR_TOTAL_ASSETS
            )
            DebugUtils.debug(f"Gross margin calculation: gross_profit={gross_profit}, revenue={revenue}")
            ratios['gross_margin'] = (gross_profit / revenue) * 100 if revenue != 0 else 0
            
            # Operating Margin
            operating_income = self._safe_get_financial_value(
                income_statement, 
                STR_OPERATING_INCOME
            )
            DebugUtils.debug(f"Operating margin calculation: operating_income={operating_income}, revenue={revenue}")
            ratios['operating_margin'] = (operating_income / revenue) * 100 if revenue != 0 else 0
            
            # Net Profit Margin
            DebugUtils.debug(f"Net margin calculation: net_income={net_income}, revenue={revenue}")
            ratios['net_margin'] = (net_income / revenue) * 100 if revenue != 0 else 0
            
            DebugUtils.debug(f"Profitability ratios calculated: {ratios}")
            
        except Exception as e:
            DebugUtils.log_error(e, "Error calculating profitability ratios")
        
        return ratios
    
    def _calculate_liquidity_ratios(self, balance_sheet: pd.DataFrame) -> Dict[str, float]:
        """Calculate liquidity ratios."""
        ratios = {}
        
        DebugUtils.debug(f"Calculating liquidity ratios with balance sheet shape: {balance_sheet.shape}")
        
        try:
            # Current Ratio
            current_assets = self._safe_get_financial_value(
                balance_sheet, 
                STR_CURRENT_ASSETS
            )
            current_liabilities = self._safe_get_financial_value(
                balance_sheet, 
                STR_TOTAL_CURRENT_LIABILITIES
            )
            DebugUtils.debug(f"Current ratio calculation: current_assets={current_assets}, current_liabilities={current_liabilities}")
            ratios['current_ratio'] = current_assets / current_liabilities if current_liabilities != 0 else 0
            
            # Quick Ratio
            cash = self._safe_get_financial_value(
                balance_sheet, 
                'Cash'
            )
            marketable_securities = self._safe_get_financial_value(
                balance_sheet, 
                STR_SHORT_TERM_INVESTMENTS
            )
            accounts_receivable = self._safe_get_financial_value(
                balance_sheet, 
                STR_NET_RECEIVABLES
            )
            quick_assets = cash + marketable_securities + accounts_receivable
            DebugUtils.debug(f"Quick ratio calculation: cash={cash}, securities={marketable_securities}, receivables={accounts_receivable}, quick_assets={quick_assets}")
            ratios['quick_ratio'] = quick_assets / current_liabilities if current_liabilities != 0 else 0
            
            # Cash Ratio
            DebugUtils.debug(f"Cash ratio calculation: cash={cash}, current_liabilities={current_liabilities}")
            ratios['cash_ratio'] = cash / current_liabilities if current_liabilities != 0 else 0
            
            DebugUtils.debug(f"Liquidity ratios calculated: {ratios}")
            
        except Exception as e:
            DebugUtils.log_error(e, "Error calculating liquidity ratios")
        
        return ratios
    
    def _calculate_efficiency_ratios(self, income_statement: pd.DataFrame, balance_sheet: pd.DataFrame) -> Dict[str, float]:
        """Calculate efficiency ratios."""
        ratios = {}
        
        try:
            # Asset Turnover
            revenue = self._safe_get_financial_value(income_statement, STR_TOTAL_REVENUE)
            total_assets = self._safe_get_financial_value(balance_sheet, STR_TOTAL_ASSETS)
            ratios['asset_turnover'] = revenue / total_assets if total_assets != 0 else 0
            
            # Inventory Turnover
            cogs = self._safe_get_financial_value(income_statement,STR_COST_OF_REVENUE)
            inventory = self._safe_get_financial_value(balance_sheet, STR_INVENTORY)
            ratios['inventory_turnover'] = cogs / inventory if inventory != 0 else 0
            
            # Receivables Turnover
            accounts_receivable = self._safe_get_financial_value(balance_sheet, STR_NET_RECEIVABLES)
            ratios['receivables_turnover'] = revenue / accounts_receivable if accounts_receivable != 0 else 0
            
        except Exception as e:
            print(f"Error calculating efficiency ratios: {str(e)}")
        
        return ratios
    
    def _calculate_debt_ratios(self, balance_sheet: pd.DataFrame) -> Dict[str, float]:
        """Calculate debt ratios."""
        ratios = {}
        
        try:
            # Debt to Equity
            total_debt = self._safe_get_financial_value(
                balance_sheet, 
                STR_TOTAL_DEBT
            )
            total_equity = self._safe_get_financial_value(
                balance_sheet, 
                STR_TOTAL_STOCKHOLDER_EQUITY
            )
            ratios['debt_to_equity'] = total_debt / total_equity if total_equity != 0 else 0
            
            # Debt to Assets
            total_assets = self._safe_get_financial_value(
                balance_sheet, 
                STR_TOTAL_ASSETS
            )
            ratios['debt_to_assets'] = total_debt / total_assets if total_assets != 0 else 0
            
        except Exception as e:
            DebugUtils.log_error(e, "Error calculating debt ratios")
        
        return ratios
    
    def _calculate_market_ratios(self, info: Dict[str, Any]) -> Dict[str, float]:
        """Calculate market ratios."""
        ratios = {}
        
        try:
            # Price to Earnings (P/E)
            ratios['pe_ratio'] = info.get('forwardPE', 0)
            
            # Price to Book (P/B)
            ratios['pb_ratio'] = info.get('priceToBook', 0)
            
            # Price to Sales (P/S)
            ratios['ps_ratio'] = info.get('priceToSalesTrailing12Months', 0)
            
            # Dividend Yield
            ratios['dividend_yield'] = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
            
        except Exception as e:
            print(f"Error calculating market ratios: {str(e)}")
        
        return ratios
    
    def get_fundamental_signals(self, ratios: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fundamental analysis signals."""
        signals = {
            'profitability': self._analyze_profitability(ratios.get('profitability', {})),
            'liquidity': self._analyze_liquidity(ratios.get('liquidity', {})),
            'efficiency': self._analyze_efficiency(ratios.get('efficiency', {})),
            'debt': self._analyze_debt(ratios.get('debt', {})),
            'valuation': self._analyze_valuation(ratios.get('market', {}))
        }
        return signals
    
    def _analyze_profitability(self, ratios: Dict[str, float]) -> str:
        """Analyze profitability ratios."""
        if ratios.get('roe', 0) > 15 and ratios.get('roa', 0) > 10:
            return "Strong Profitability"
        elif ratios.get('roe', 0) > 10 and ratios.get('roa', 0) > 5:
            return "Moderate Profitability"
        return "Weak Profitability"
    
    def _analyze_liquidity(self, ratios: Dict[str, float]) -> str:
        """Analyze liquidity ratios."""
        if ratios.get('current_ratio', 0) > 2 and ratios.get('quick_ratio', 0) > 1:
            return "Strong Liquidity"
        elif ratios.get('current_ratio', 0) > 1.5 and ratios.get('quick_ratio', 0) > 0.75:
            return "Moderate Liquidity"
        return "Weak Liquidity"
    
    def _analyze_efficiency(self, ratios: Dict[str, float]) -> str:
        """Analyze efficiency ratios."""
        if ratios.get('asset_turnover', 0) > 1 and ratios.get('inventory_turnover', 0) > 5:
            return "High Efficiency"
        elif ratios.get('asset_turnover', 0) > 0.5 and ratios.get('inventory_turnover', 0) > 3:
            return "Moderate Efficiency"
        return "Low Efficiency"
    
    def _analyze_debt(self, ratios: Dict[str, float]) -> str:
        """Analyze debt ratios."""
        if ratios.get('debt_to_equity', 0) < 0.5 and ratios.get('debt_to_assets', 0) < 0.3:
            return "Low Debt"
        elif ratios.get('debt_to_equity', 0) < 1 and ratios.get('debt_to_assets', 0) < 0.5:
            return "Moderate Debt"
        return "High Debt"
    
    def _analyze_valuation(self, ratios: Dict[str, float]) -> str:
        """Analyze valuation ratios."""
        if ratios.get('pe_ratio', 0) < 15 and ratios.get('pb_ratio', 0) < 2:
            return "Potentially Undervalued"
        elif ratios.get('pe_ratio', 0) < 25 and ratios.get('pb_ratio', 0) < 3:
            return "Fairly Valued"
        return "Potentially Overvalued" 