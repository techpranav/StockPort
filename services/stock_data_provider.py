from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd
from models.stock_data import (
    CompanyInfo,
    FinancialMetrics,
    TechnicalIndicators,
    TechnicalSignals,
    FinancialStatements,
    NewsItem,
    StockData
)

class StockDataProvider(ABC):
    """Abstract base class for stock data providers."""
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the provider."""
        pass
    
    @abstractmethod
    def fetch_stock_data(self, symbol: str) -> StockData:
        """Fetch all stock data and return in standardized format."""
        pass
    
    @abstractmethod
    def fetch_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical price data."""
        pass
    
    @abstractmethod
    def fetch_financials(self, symbol: str) -> Dict[str, Any]:
        """Fetch financial statements."""
        pass
    
    @abstractmethod
    def fetch_company_info(self, symbol: str) -> Dict[str, Any]:
        """Fetch company information."""
        pass
    
    @abstractmethod
    def fetch_news(self, symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch company news."""
        pass
    
    @abstractmethod
    def _normalize_company_info(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize company information from provider-specific format."""
        pass
    
    @abstractmethod
    def _normalize_financial_metrics(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize financial metrics from provider-specific format."""
        pass
    
    @abstractmethod
    def _normalize_technical_analysis(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize technical analysis from provider-specific format."""
        pass
    
    @abstractmethod
    def _normalize_financial_statements(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize financial statements from provider-specific format."""
        pass
    
    @abstractmethod
    def _normalize_news(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize news data from provider-specific format."""
        pass 