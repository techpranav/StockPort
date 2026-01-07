"""
Alpha Vantage Data Adapter

Adapter for normalizing Alpha Vantage data to standard format.
Alpha Vantage uses different column naming conventions.
"""

from typing import Dict
import pandas as pd

from services.data_providers.adapters.data_adapter import DataAdapter
from utils.debug_utils import DebugUtils


class AlphaVantageAdapter(DataAdapter):
    """
    Adapter for Alpha Vantage data provider.
    
    Alpha Vantage API returns data with columns like:
    - open, high, low, close, volume (lowercase)
    - Or: 1. open, 2. high, 3. low, 4. close, 5. volume (numbered)
    """
    
    def __init__(self):
        """Initialize Alpha Vantage adapter."""
        super().__init__("alpha_vantage")
    
    def get_provider_name(self) -> str:
        """
        Get the provider name.
        
        Returns:
            Provider name string
        """
        return "alpha_vantage"
    
    def _get_column_mappings(self) -> Dict[str, str]:
        """
        Get mapping from Alpha Vantage column names to standard names.
        
        Alpha Vantage can return columns in different formats:
        - Lowercase: open, high, low, close, volume
        - Numbered: 1. open, 2. high, 3. low, 4. close, 5. volume
        - With spaces: Open, High, Low, Close, Volume
        
        Returns:
            Dictionary mapping Alpha Vantage columns to standard columns
        """
        return {
            # Standard lowercase format
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume',
            # Numbered format (from API response)
            '1. open': 'open',
            '2. high': 'high',
            '3. low': 'low',
            '4. close': 'close',
            '5. volume': 'volume',
            # Title case format
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            # Date/time columns
            'date': 'date',
            'Date': 'date',
            'timestamp': 'timestamp',
            'Timestamp': 'timestamp'
        }
    
    def normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize Alpha Vantage DataFrame.
        
        Alpha Vantage DataFrames may have:
        - Different index types
        - Numbered column names
        - Different date formats
        
        Args:
            df: Raw Alpha Vantage DataFrame
            
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
            
            # Alpha Vantage may have date in index or as column
            if not isinstance(normalized.index, pd.DatetimeIndex):
                # Try to convert index
                try:
                    normalized.index = pd.to_datetime(normalized.index, errors='coerce')
                except Exception:
                    # If index conversion fails, check for date column
                    if 'date' in normalized.columns:
                        normalized = normalized.set_index('date')
                        normalized.index = pd.to_datetime(normalized.index, errors='coerce')
                    elif 'timestamp' in normalized.columns:
                        normalized = normalized.set_index('timestamp')
                        normalized.index = pd.to_datetime(normalized.index, errors='coerce')
            
            # Ensure numeric columns are numeric
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                if col in normalized.columns:
                    normalized[col] = pd.to_numeric(normalized[col], errors='coerce')
            
            # Validate required columns
            validation = self.schema.validate_dataframe_columns(normalized.columns.tolist())
            if not validation['valid']:
                missing = validation['missing']
                DebugUtils.warning(
                    f"Alpha Vantage data missing columns: {missing}. "
                    f"Available: {normalized.columns.tolist()}"
                )
                # Create missing columns with NaN
                for col in missing:
                    if col not in normalized.columns:
                        normalized[col] = pd.NA
            
            DebugUtils.debug(
                f"Normalized Alpha Vantage DataFrame: {len(normalized)} rows, "
                f"columns: {normalized.columns.tolist()}"
            )
            
            return normalized
            
        except Exception as e:
            DebugUtils.log_error(e, "Error normalizing Alpha Vantage DataFrame")
            raise

