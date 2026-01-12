from typing import Dict, Any, Optional
import pandas as pd
from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataAnalysisException

class BaseAnalyzer:
    """Base class for financial analysis."""
    
    @staticmethod
    def _get_latest_value(df: pd.DataFrame, column: str) -> Optional[float]:
        """
        Get the latest value from a DataFrame column.
        
        Args:
            df: DataFrame containing the data
            column: Column name to get value from
            
        Returns:
            Latest value or None if not found
        """
        try:
            if not df.empty and column in df.columns:
                return float(df[column].iloc[-1])
            return None
        except Exception as e:
            DebugUtils.error(f"Error getting latest value for {column}: {str(e)}")
            return None
    
    @staticmethod
    def _calculate_growth_rate(current: float, previous: float) -> float:
        """
        Calculate growth rate between two values.
        
        Args:
            current: Current value
            previous: Previous value
            
        Returns:
            Growth rate as a percentage
        """
        try:
            if previous == 0:
                return 0.0
            return ((current - previous) / abs(previous)) * 100
        except Exception as e:
            DebugUtils.error(f"Error calculating growth rate: {str(e)}")
            return 0.0
    
    @staticmethod
    def _validate_data(data: Dict[str, Any], required_keys: list) -> None:
        """
        Validate that required data is present.
        
        Args:
            data: Dictionary containing the data
            required_keys: List of required keys
            
        Raises:
            DataAnalysisException: If required data is missing
        """
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise DataAnalysisException(f"Missing required data: {', '.join(missing_keys)}") 