"""
Data Preprocessing Module

This module provides data normalization, cleaning, missing data interpolation,
and outlier detection for stock data.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException
from services.data_providers.adapters.adapter_factory import AdapterFactory
from config.constants.DataConstants import DEFAULT_PROVIDER


class DataPreprocessor:
    """
    Data preprocessor for stock data.
    
    Features:
    - Data normalization and cleaning
    - Missing data interpolation
    - Outlier detection and handling
    - Data validation checks
    """
    
    def __init__(self):
        """Initialize data preprocessor."""
        pass
    
    def preprocess_data(
        self,
        data: pd.DataFrame,
        fill_method: str = "forward",
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.DataFrame:
        """
        Preprocess stock data.
        
        Args:
            data: Raw DataFrame with OHLCV data (will be normalized)
            fill_method: Method for filling missing data (forward, backward, interpolate)
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            Cleaned and normalized DataFrame
        """
        try:
            if data.empty:
                raise DataProcessingException("Data cannot be empty")
            
            # Normalize data using adapter first
            adapter = AdapterFactory.get_adapter(provider_name)
            processed = adapter.normalize_dataframe(data)
            
            if processed.empty:
                raise DataProcessingException("Normalized data is empty")
            
            # Validate required columns using adapter
            if not adapter.validate_data(processed):
                validation = adapter.schema.validate_dataframe_columns(processed.columns.tolist())
                missing = validation.get('missing', [])
                raise DataProcessingException(
                    f"Missing required columns: {missing}"
                )
            
            # Handle missing values
            processed = self._handle_missing_values(processed, fill_method)
            
            # Detect and handle outliers
            processed = self._handle_outliers(processed, provider_name=provider_name)
            
            # Validate data integrity
            self._validate_data_integrity(processed, provider_name=provider_name)
            
            DebugUtils.debug(f"Preprocessed data: {len(processed)} rows")
            return processed
            
        except Exception as e:
            DebugUtils.log_error(e, "Error preprocessing data")
            raise DataProcessingException(f"Data preprocessing failed: {str(e)}") from e
    
    def _handle_missing_values(
        self,
        data: pd.DataFrame,
        fill_method: str
    ) -> pd.DataFrame:
        """Handle missing values in data."""
        if fill_method == "forward":
            data = data.fillna(method='ffill')
        elif fill_method == "backward":
            data = data.fillna(method='bfill')
        elif fill_method == "interpolate":
            data = data.interpolate(method='linear')
        else:
            # Default: forward fill then backward fill
            data = data.fillna(method='ffill').fillna(method='bfill')
        
        # Drop any remaining NaN rows
        data = data.dropna()
        
        return data
    
    def _handle_outliers(
        self,
        data: pd.DataFrame,
        threshold: float = 3.0,
        provider_name: str = DEFAULT_PROVIDER
    ) -> pd.DataFrame:
        """
        Detect and handle outliers using Z-score.
        
        Args:
            data: DataFrame to process (should be normalized)
            threshold: Z-score threshold (default: 3.0)
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            DataFrame with outliers handled
        """
        processed = data.copy()
        adapter = AdapterFactory.get_adapter(provider_name)
        
        # Calculate Z-scores for price columns using adapter
        price_column_types = ['OPEN', 'HIGH', 'LOW', 'CLOSE']
        
        for col_type in price_column_types:
            try:
                col = adapter.get_column(processed, col_type)
                z_scores = np.abs((col - col.mean()) / col.std())
                
                # Replace outliers with median
                outlier_mask = z_scores > threshold
                if outlier_mask.any():
                    median_value = col.median()
                    standard_col_name = adapter.schema.COLUMNS[col_type]
                    processed.loc[outlier_mask, standard_col_name] = median_value
                    DebugUtils.debug(f"Handled {outlier_mask.sum()} outliers in {standard_col_name}")
            except DataProcessingException:
                # Column not available, skip
                pass
        
        return processed
    
    def _validate_data_integrity(
        self,
        data: pd.DataFrame,
        provider_name: str = DEFAULT_PROVIDER
    ) -> None:
        """Validate data integrity (High >= Low, etc.)."""
        adapter = AdapterFactory.get_adapter(provider_name)
        
        try:
            high = adapter.get_column(data, 'HIGH')
            low = adapter.get_column(data, 'LOW')
            close = adapter.get_column(data, 'CLOSE')
            
            # High should be >= Low
            invalid_high_low = high < low
            if invalid_high_low.any():
                DebugUtils.warning(f"Found {invalid_high_low.sum()} rows where High < Low")
                # Fix by setting High = max(High, Low) and Low = min(High, Low)
                high_col = adapter.schema.COLUMNS['HIGH']
                low_col = adapter.schema.COLUMNS['LOW']
                data.loc[invalid_high_low, high_col] = data.loc[invalid_high_low, [high_col, low_col]].max(axis=1)
                data.loc[invalid_high_low, low_col] = data.loc[invalid_high_low, [high_col, low_col]].min(axis=1)
            
            # Close should be between Low and High
            invalid_close = (close < low) | (close > high)
            if invalid_close.any():
                DebugUtils.warning(f"Found {invalid_close.sum()} rows where Close outside High/Low range")
                # Clamp Close to High/Low range
                close_col = adapter.schema.COLUMNS['CLOSE']
                high_col = adapter.schema.COLUMNS['HIGH']
                low_col = adapter.schema.COLUMNS['LOW']
                data.loc[invalid_close, close_col] = data.loc[invalid_close, [high_col, low_col, close_col]].apply(
                    lambda x: np.clip(x[close_col], x[low_col], x[high_col]), axis=1
                )
            
            # Volume should be non-negative
            try:
                volume = adapter.get_column(data, 'VOLUME')
                negative_volume = volume < 0
                if negative_volume.any():
                    DebugUtils.warning(f"Found {negative_volume.sum()} rows with negative volume")
                    volume_col = adapter.schema.COLUMNS['VOLUME']
                    data.loc[negative_volume, volume_col] = 0
            except DataProcessingException:
                # Volume column not available, skip
                pass
        except DataProcessingException as e:
            DebugUtils.warning(f"Could not validate data integrity: {e}")

