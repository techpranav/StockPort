"""
Yahoo Finance Data Adapter

Adapter for normalizing Yahoo Finance data to standard format.
Yahoo Finance typically uses: Open, High, Low, Close, Volume, Adj Close
"""

from typing import Dict
import pandas as pd

from services.data_providers.adapters.data_adapter import DataAdapter
from utils.debug_utils import DebugUtils


class YahooFinanceAdapter(DataAdapter):
    """
    Adapter for Yahoo Finance data provider.
    
    Yahoo Finance uses standard column names:
    - Open, High, Low, Close, Volume, Adj Close
    """
    
    def __init__(self):
        """Initialize Yahoo Finance adapter."""
        super().__init__("yahoo_finance")
    
    def get_provider_name(self) -> str:
        """
        Get the provider name.
        
        Returns:
            Provider name string
        """
        return "yahoo_finance"
    
    def _get_column_mappings(self) -> Dict[str, str]:
        """
        Get mapping from Yahoo Finance column names to standard names.
        
        Returns:
            Dictionary mapping Yahoo Finance columns to standard columns
        """
        return {
            # Standard Yahoo Finance columns
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            'Adj Close': 'adj_close',
            # Alternative formats
            'AdjClose': 'adj_close',
            'Adj. Close': 'adj_close',
            # Date column
            'Date': 'date',
            # Index name (if Date is in index)
            'Datetime': 'date'
        }
    
    def normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize Yahoo Finance DataFrame.
        
        Yahoo Finance DataFrames typically have:
        - DatetimeIndex
        - Columns: Open, High, Low, Close, Volume, Adj Close
        
        Args:
            df: Raw Yahoo Finance DataFrame
            
        Returns:
            Normalized DataFrame
        """
        if df is None or df.empty:
            return pd.DataFrame()
        
        try:
            normalized = df.copy()
            
            # Apply column mappings
            column_mappings = self._get_column_mappings()
            rename_dict = {}
            for provider_col, standard_col in column_mappings.items():
                if provider_col in normalized.columns:
                    rename_dict[provider_col] = standard_col
            
            if rename_dict:
                normalized = normalized.rename(columns=rename_dict)
            
            # Yahoo Finance typically has DatetimeIndex, but ensure it's correct
            if not isinstance(normalized.index, pd.DatetimeIndex):
                try:
                    normalized.index = pd.to_datetime(normalized.index, errors='coerce')
                except Exception:
                    # If index conversion fails, try to use Date column
                    if 'date' in normalized.columns:
                        normalized = normalized.set_index('date')
                        normalized.index = pd.to_datetime(normalized.index, errors='coerce')
            
            # Ensure numeric columns are numeric
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'adj_close']
            for col in numeric_cols:
                if col in normalized.columns:
                    normalized[col] = pd.to_numeric(normalized[col], errors='coerce')
            
            # Validate required columns
            validation = self.schema.validate_dataframe_columns(normalized.columns.tolist())
            if not validation['valid']:
                missing = validation['missing']
                DebugUtils.warning(
                    f"Yahoo Finance data missing columns: {missing}. "
                    f"Available: {normalized.columns.tolist()}"
                )
                # Create missing columns with NaN
                for col in missing:
                    if col not in normalized.columns:
                        normalized[col] = pd.NA
            
            DebugUtils.debug(
                f"Normalized Yahoo Finance DataFrame: {len(normalized)} rows, "
                f"columns: {normalized.columns.tolist()}"
            )
            
            return normalized
            
        except Exception as e:
            DebugUtils.log_error(e, "Error normalizing Yahoo Finance DataFrame")
            raise

