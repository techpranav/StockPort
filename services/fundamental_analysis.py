import pandas as pd
import numpy as np
from typing import Dict, Any, List

class FundamentalAnalysisService:
    def __init__(self):
        """Initialize fundamental analysis service."""
        pass
    
    def calculate_financial_ratios(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key financial ratios."""
        ratios = {}
        
        # Get financial statements
        income_statement = data.get('yearly_income_statement', pd.DataFrame())
        balance_sheet = data.get('yearly_balance_sheet', pd.DataFrame())
        cashflow = data.get('yearly_cashflow', pd.DataFrame())
        
        if income_statement.empty or balance_sheet.empty:
            return ratios
        
        # Profitability Ratios
        ratios['profitability'] = self._calculate_profitability_ratios(income_statement, balance_sheet)
        
        # Liquidity Ratios
        ratios['liquidity'] = self._calculate_liquidity_ratios(balance_sheet)
        
        # Efficiency Ratios
        ratios['efficiency'] = self._calculate_efficiency_ratios(income_statement, balance_sheet)
        
        # Debt Ratios
        ratios['debt'] = self._calculate_debt_ratios(balance_sheet)
        
        # Market Ratios
        ratios['market'] = self._calculate_market_ratios(data.get('info', {}))
        
        return ratios
    
    def _calculate_profitability_ratios(self, income_statement: pd.DataFrame, balance_sheet: pd.DataFrame) -> Dict[str, float]:
        """Calculate profitability ratios."""
        ratios = {}
        
        try:
            # Return on Equity (ROE)
            net_income = income_statement.loc['Net Income'].iloc[0]
            total_equity = balance_sheet.loc['Total Stockholder Equity'].iloc[0]
            ratios['roe'] = (net_income / total_equity) * 100 if total_equity != 0 else 0
            
            # Return on Assets (ROA)
            total_assets = balance_sheet.loc['Total Assets'].iloc[0]
            ratios['roa'] = (net_income / total_assets) * 100 if total_assets != 0 else 0
            
            # Gross Profit Margin
            gross_profit = income_statement.loc['Gross Profit'].iloc[0]
            revenue = income_statement.loc['Total Revenue'].iloc[0]
            ratios['gross_margin'] = (gross_profit / revenue) * 100 if revenue != 0 else 0
            
            # Operating Margin
            operating_income = income_statement.loc['Operating Income'].iloc[0]
            ratios['operating_margin'] = (operating_income / revenue) * 100 if revenue != 0 else 0
            
            # Net Profit Margin
            ratios['net_margin'] = (net_income / revenue) * 100 if revenue != 0 else 0
            
        except Exception as e:
            print(f"Error calculating profitability ratios: {str(e)}")
        
        return ratios
    
    def _calculate_liquidity_ratios(self, balance_sheet: pd.DataFrame) -> Dict[str, float]:
        """Calculate liquidity ratios."""
        ratios = {}
        
        try:
            # Current Ratio
            current_assets = balance_sheet.loc['Total Current Assets'].iloc[0]
            current_liabilities = balance_sheet.loc['Total Current Liabilities'].iloc[0]
            ratios['current_ratio'] = current_assets / current_liabilities if current_liabilities != 0 else 0
            
            # Quick Ratio
            cash = balance_sheet.loc['Cash'].iloc[0]
            marketable_securities = balance_sheet.loc['Short Term Investments'].iloc[0]
            accounts_receivable = balance_sheet.loc['Net Receivables'].iloc[0]
            quick_assets = cash + marketable_securities + accounts_receivable
            ratios['quick_ratio'] = quick_assets / current_liabilities if current_liabilities != 0 else 0
            
            # Cash Ratio
            ratios['cash_ratio'] = cash / current_liabilities if current_liabilities != 0 else 0
            
        except Exception as e:
            print(f"Error calculating liquidity ratios: {str(e)}")
        
        return ratios
    
    def _calculate_efficiency_ratios(self, income_statement: pd.DataFrame, balance_sheet: pd.DataFrame) -> Dict[str, float]:
        """Calculate efficiency ratios."""
        ratios = {}
        
        try:
            # Asset Turnover
            revenue = income_statement.loc['Total Revenue'].iloc[0]
            total_assets = balance_sheet.loc['Total Assets'].iloc[0]
            ratios['asset_turnover'] = revenue / total_assets if total_assets != 0 else 0
            
            # Inventory Turnover
            cogs = income_statement.loc['Cost Of Revenue'].iloc[0]
            inventory = balance_sheet.loc['Inventory'].iloc[0]
            ratios['inventory_turnover'] = cogs / inventory if inventory != 0 else 0
            
            # Receivables Turnover
            accounts_receivable = balance_sheet.loc['Net Receivables'].iloc[0]
            ratios['receivables_turnover'] = revenue / accounts_receivable if accounts_receivable != 0 else 0
            
        except Exception as e:
            print(f"Error calculating efficiency ratios: {str(e)}")
        
        return ratios
    
    def _calculate_debt_ratios(self, balance_sheet: pd.DataFrame) -> Dict[str, float]:
        """Calculate debt ratios."""
        ratios = {}
        
        try:
            # Debt to Equity
            total_debt = balance_sheet.loc['Total Debt'].iloc[0]
            total_equity = balance_sheet.loc['Total Stockholder Equity'].iloc[0]
            ratios['debt_to_equity'] = total_debt / total_equity if total_equity != 0 else 0
            
            # Debt to Assets
            total_assets = balance_sheet.loc['Total Assets'].iloc[0]
            ratios['debt_to_assets'] = total_debt / total_assets if total_assets != 0 else 0
            
        except Exception as e:
            print(f"Error calculating debt ratios: {str(e)}")
        
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