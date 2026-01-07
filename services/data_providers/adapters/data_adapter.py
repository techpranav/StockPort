"""
Data Adapter Base Class

Abstract base class for data adapters that normalize provider-specific
data formats to the standard internal format.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np

from models.data_schema import StandardDataSchema
from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException


class DataAdapter(ABC):
    """
    Abstract base class for data adapters.
    
    Adapters are responsible for:
    1. Normalizing provider-specific column names to standard names
    2. Validating data structure
    3. Providing safe access to standardized columns
    4. Handling missing or invalid data gracefully
    """
    
    def __init__(self, provider_name: str):
        """
        Initialize the data adapter.
        
        Args:
            provider_name: Name of the data provider (e.g., 'yahoo_finance')
        """
        self.provider_name = provider_name
        self.schema = StandardDataSchema()
        DebugUtils.debug(f"Initialized {provider_name} data adapter")
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of the provider this adapter handles.
        
        Returns:
            Provider name string
        """
        pass
    
    def normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert provider-specific DataFrame to standard format.
        
        This method:
        1. Renames columns to standard names
        2. Validates required columns are present
        3. Ensures data types are correct
        4. Handles missing columns gracefully
        
        Args:
            df: Raw DataFrame from provider
            
        Returns:
            Normalized DataFrame with standard column names
            
        Raises:
            DataProcessingException: If required columns are missing
        """
        if df is None or df.empty:
            DebugUtils.warning("Empty DataFrame provided for normalization")
            return pd.DataFrame()
        
        try:
            # Create a copy to avoid modifying original
            normalized = df.copy()
            
            # Get provider-specific column mappings
            column_mappings = self._get_column_mappings()
            
            # Rename columns to standard names
            rename_dict = {}
            for provider_col, standard_col in column_mappings.items():
                if provider_col in normalized.columns:
                    rename_dict[provider_col] = standard_col
            
            if rename_dict:
                normalized = normalized.rename(columns=rename_dict)
            
            # Validate required columns
            validation = self.schema.validate_dataframe_columns(normalized.columns.tolist())
            if not validation['valid']:
                missing = validation['missing']
                DebugUtils.warning(
                    f"Missing required columns: {missing}. "
                    f"Available columns: {normalized.columns.tolist()}"
                )
                # Try to create missing columns with NaN values
                for col in missing:
                    normalized[col] = np.nan
            
            # Ensure data types are correct
            normalized = self._normalize_data_types(normalized)
            
            # Ensure date index is properly set
            if normalized.index.dtype == 'object' or not isinstance(normalized.index, pd.DatetimeIndex):
                normalized = self._normalize_index(normalized)
            
            DebugUtils.debug(
                f"Normalized DataFrame: {len(normalized)} rows, "
                f"columns: {normalized.columns.tolist()}"
            )
            
            return normalized
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error normalizing DataFrame from {self.provider_name}")
            raise DataProcessingException(
                f"Failed to normalize DataFrame from {self.provider_name}: {str(e)}"
            ) from e
    
    @abstractmethod
    def _get_column_mappings(self) -> Dict[str, str]:
        """
        Get mapping from provider-specific column names to standard names.
        
        Returns:
            Dictionary mapping provider columns to standard columns
        """
        pass
    
    def get_column(self, df: pd.DataFrame, column_type: str) -> pd.Series:
        """
        Get standardized column from DataFrame.
        
        Args:
            df: DataFrame (should be normalized, but will normalize if needed)
            column_type: Standard column type ('OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'ADJ_CLOSE')
            
        Returns:
            Series containing the column data
            
        Raises:
            DataProcessingException: If column is not available
        """
        if df is None or df.empty:
            raise DataProcessingException("DataFrame is empty or None")
        
        # Normalize if needed
        if not self._is_normalized(df):
            df = self.normalize_dataframe(df)
        
        # Get standard column name
        standard_name = self.schema.COLUMNS.get(column_type.upper())
        if not standard_name:
            raise DataProcessingException(
                f"Invalid column type: {column_type}. "
                f"Valid types: {list(self.schema.COLUMNS.keys())}"
            )
        
        if standard_name not in df.columns:
            raise DataProcessingException(
                f"Column '{standard_name}' not found in DataFrame. "
                f"Available columns: {df.columns.tolist()}"
            )
        
        return df[standard_name]
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate DataFrame has required columns.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if valid, False otherwise
        """
        if df is None or df.empty:
            return False
        
        # Normalize first to check against standard columns
        try:
            normalized = self.normalize_dataframe(df)
            validation = self.schema.validate_dataframe_columns(normalized.columns.tolist())
            return validation['valid']
        except Exception as e:
            DebugUtils.log_error(e, "Error validating DataFrame")
            return False
    
    def _is_normalized(self, df: pd.DataFrame) -> bool:
        """
        Check if DataFrame is already normalized.
        
        Args:
            df: DataFrame to check
            
        Returns:
            True if normalized, False otherwise
        """
        if df is None or df.empty:
            return False
        
        # Check if standard column names are present
        standard_cols = set(self.schema.get_required_columns())
        df_cols = set(df.columns.str.lower())
        
        # At least some standard columns should be present
        return len(standard_cols & df_cols) >= 3
    
    def _normalize_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize data types of columns.
        
        Args:
            df: DataFrame to normalize
            
        Returns:
            DataFrame with normalized data types
        """
        normalized = df.copy()
        
        # Ensure numeric columns are numeric
        numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'adj_close']
        for col in numeric_cols:
            if col in normalized.columns:
                normalized[col] = pd.to_numeric(normalized[col], errors='coerce')
        
        return normalized
    
    def _normalize_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize DataFrame index to DatetimeIndex.
        
        Args:
            df: DataFrame to normalize
            
        Returns:
            DataFrame with DatetimeIndex
        """
        normalized = df.copy()
        
        # Try to convert index to datetime
        try:
            if not isinstance(normalized.index, pd.DatetimeIndex):
                # If index is not datetime, try to parse it
                if 'date' in normalized.columns:
                    normalized = normalized.set_index('date')
                elif 'timestamp' in normalized.columns:
                    normalized = normalized.set_index('timestamp')
                
                # Convert to datetime
                normalized.index = pd.to_datetime(normalized.index, errors='coerce')
        except Exception as e:
            DebugUtils.warning(f"Could not normalize index to datetime: {e}")
        
        return normalized
    
    def get_ohlcv_data(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Get all OHLCV data as a dictionary.
        
        Args:
            df: DataFrame (will be normalized if needed)
            
        Returns:
            Dictionary with keys: 'open', 'high', 'low', 'close', 'volume'
        """
        if df is None or df.empty:
            return {}
        
        # Normalize if needed
        if not self._is_normalized(df):
            df = self.normalize_dataframe(df)
        
        result = {}
        for col_type in ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']:
            try:
                result[col_type.lower()] = self.get_column(df, col_type)
            except DataProcessingException:
                # Column not available, skip it
                pass
        
        return result

