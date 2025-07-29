class StockDataException(Exception):
    """Base exception for stock data operations."""
    pass

class RateLimitException(StockDataException):
    """Exception raised when API rate limit is hit."""
    pass

class InvalidSymbolException(StockDataException):
    """Exception raised when an invalid stock symbol is provided."""
    pass

class DataFetchException(StockDataException):
    """Exception raised when there's an error fetching data."""
    pass

class DataProcessingException(StockDataException):
    """Exception raised when there's an error processing data."""
    pass

class ExportException(StockDataException):
    """Exception raised when there's an error exporting data."""
    pass

class DataAnalysisException(StockDataException):
    """Exception raised when there's an error during data analysis."""
    pass 