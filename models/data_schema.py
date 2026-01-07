"""
Data Schema Module

Defines the standard internal data structure and column names used throughout
the application. This ensures consistency across different data providers.
"""

from typing import Dict, List, Set
from config.constants.StringConstants import (
    COLUMN_OPEN,
    COLUMN_HIGH,
    COLUMN_LOW,
    COLUMN_CLOSE,
    COLUMN_VOLUME,
    COLUMN_ADJ_CLOSE
)


class StandardDataSchema:
    """
    Defines standard internal data structure and column names.
    
    This class provides a centralized definition of how data should be
    structured internally, regardless of the data provider source.
    All providers must map their data to this standard format.
    """
    
    # Standard column names (internal representation)
    COLUMNS: Dict[str, str] = {
        'OPEN': 'open',
        'HIGH': 'high',
        'LOW': 'low',
        'CLOSE': 'close',
        'VOLUME': 'volume',
        'ADJ_CLOSE': 'adj_close',
        'DATE': 'date',
        'TIMESTAMP': 'timestamp'
    }
    
    # Required columns for OHLCV data
    REQUIRED_COLUMNS: Set[str] = {
        'open',
        'high',
        'low',
        'close',
        'volume'
    }
    
    # Optional columns
    OPTIONAL_COLUMNS: Set[str] = {
        'adj_close',
        'date',
        'timestamp'
    }
    
    # Column aliases mapping (provider-specific to standard)
    COLUMN_ALIASES: Dict[str, str] = {
        # Common variations
        'Open': 'open',
        'OPEN': 'open',
        'o': 'open',
        'High': 'high',
        'HIGH': 'high',
        'h': 'high',
        'Low': 'low',
        'LOW': 'low',
        'l': 'low',
        'Close': 'close',
        'CLOSE': 'close',
        'c': 'close',
        'Volume': 'volume',
        'VOLUME': 'volume',
        'v': 'volume',
        'Adj Close': 'adj_close',
        'AdjClose': 'adj_close',
        'ADJ_CLOSE': 'adj_close',
        'Adj. Close': 'adj_close',
        'Date': 'date',
        'DATE': 'date',
        'Timestamp': 'timestamp',
        'TIMESTAMP': 'timestamp',
        'time': 'timestamp',
        'Time': 'timestamp'
    }
    
    @classmethod
    def get_standard_column_name(cls, column_name: str) -> str:
        """
        Get standard column name from any provider-specific column name.
        
        Args:
            column_name: Provider-specific column name
            
        Returns:
            Standard column name (lowercase, no spaces)
        """
        # First check exact match in aliases
        if column_name in cls.COLUMN_ALIASES:
            return cls.COLUMN_ALIASES[column_name]
        
        # Try case-insensitive match
        column_lower = column_name.lower().strip()
        for alias, standard in cls.COLUMN_ALIASES.items():
            if alias.lower() == column_lower:
                return standard
        
        # If no match found, normalize the name
        normalized = column_name.lower().strip().replace(' ', '_')
        return normalized
    
    @classmethod
    def validate_dataframe_columns(cls, columns: List[str]) -> Dict[str, bool]:
        """
        Validate that DataFrame has required columns.
        
        Args:
            columns: List of column names in DataFrame
            
        Returns:
            Dictionary with validation results:
            - 'valid': True if all required columns present
            - 'missing': List of missing required columns
            - 'has_optional': List of optional columns present
        """
        column_set = {cls.get_standard_column_name(col) for col in columns}
        
        missing = cls.REQUIRED_COLUMNS - column_set
        has_optional = cls.OPTIONAL_COLUMNS & column_set
        
        return {
            'valid': len(missing) == 0,
            'missing': list(missing),
            'has_optional': list(has_optional),
            'present': list(cls.REQUIRED_COLUMNS & column_set)
        }
    
    @classmethod
    def get_all_standard_columns(cls) -> List[str]:
        """
        Get list of all standard column names.
        
        Returns:
            List of standard column names
        """
        return list(cls.COLUMNS.values())
    
    @classmethod
    def get_required_columns(cls) -> List[str]:
        """
        Get list of required column names.
        
        Returns:
            List of required column names
        """
        return list(cls.REQUIRED_COLUMNS)
    
    @classmethod
    def get_optional_columns(cls) -> List[str]:
        """
        Get list of optional column names.
        
        Returns:
            List of optional column names
        """
        return list(cls.OPTIONAL_COLUMNS)

