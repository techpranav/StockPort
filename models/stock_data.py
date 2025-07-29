from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

@dataclass
class CompanyInfo:
    """Standardized company information."""
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None
    exchange: Optional[str] = None
    market_cap: Optional[float] = None
    employees: Optional[int] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

@dataclass
class FinancialMetrics:
    """Standardized financial metrics."""
    revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_income: Optional[float] = None
    net_income: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    total_equity: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    investing_cash_flow: Optional[float] = None
    financing_cash_flow: Optional[float] = None
    free_cash_flow: Optional[float] = None
    eps: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None

@dataclass
class TechnicalIndicators:
    """Standardized technical indicators."""
    current_price: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    volume: Optional[float] = None
    volume_sma: Optional[float] = None

@dataclass
class TechnicalSignals:
    """Standardized technical signals."""
    trend: Optional[str] = None
    momentum: Optional[str] = None
    volatility: Optional[str] = None
    volume: Optional[str] = None

@dataclass
class FinancialStatements:
    """Standardized financial statements."""
    yearly_income_statement: Optional[pd.DataFrame] = None
    quarterly_income_statement: Optional[pd.DataFrame] = None
    yearly_balance_sheet: Optional[pd.DataFrame] = None
    quarterly_balance_sheet: Optional[pd.DataFrame] = None
    yearly_cash_flow: Optional[pd.DataFrame] = None
    quarterly_cash_flow: Optional[pd.DataFrame] = None

@dataclass
class NewsItem:
    """Standardized news item."""
    title: str
    summary: Optional[str] = None
    url: Optional[str] = None
    published_date: Optional[datetime] = None
    source: Optional[str] = None

@dataclass
class StockData:
    """Standardized stock data structure."""
    symbol: str
    company_info: CompanyInfo
    metrics: FinancialMetrics
    technical_analysis: TechnicalIndicators
    technical_signals: TechnicalSignals
    financials: FinancialStatements
    news: List[NewsItem]
    raw_data: Dict[str, Any]  # Store original provider data for reference

    def to_dict(self) -> Dict[str, Any]:
        """Convert the stock data to a dictionary format."""
        return {
            'symbol': self.symbol,
            'info': self.company_info.__dict__,
            'metrics': self.metrics.__dict__,
            'technical_analysis': self.technical_analysis.__dict__,
            'technical_signals': self.technical_signals.__dict__,
            'financials': {
                'yearly_income_statement': self.financials.yearly_income_statement.to_dict() if self.financials.yearly_income_statement is not None else None,
                'quarterly_income_statement': self.financials.quarterly_income_statement.to_dict() if self.financials.quarterly_income_statement is not None else None,
                'yearly_balance_sheet': self.financials.yearly_balance_sheet.to_dict() if self.financials.yearly_balance_sheet is not None else None,
                'quarterly_balance_sheet': self.financials.quarterly_balance_sheet.to_dict() if self.financials.quarterly_balance_sheet is not None else None,
                'yearly_cash_flow': self.financials.yearly_cash_flow.to_dict() if self.financials.yearly_cash_flow is not None else None,
                'quarterly_cash_flow': self.financials.quarterly_cash_flow.to_dict() if self.financials.quarterly_cash_flow is not None else None,
            },
            'news': [news.__dict__ for news in self.news],
            'raw_data': self.raw_data
        } 