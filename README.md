# Stock Market Data Analysis Tool

A Python-based tool for fetching, analyzing, and exporting stock market data using Yahoo Finance API.

## Features

- Fetch historical stock data
- Calculate financial metrics and ratios
- Perform technical analysis
- Export data to Excel
- Rate limiting and retry logic
- Comprehensive error handling
- Debug logging system
- Optional Google Drive upload for reports

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd stock-market-analysis
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
stock-market-analysis/
├── config/
│   └── settings.py           # Global configuration settings
├── exceptions/
│   └── stock_data_exceptions.py  # Custom exceptions
├── models/
│   └── stock_data.py         # Data models
├── services/
│   ├── analysis/
│   │   ├── financial_analysis.py  # Financial calculations
│   │   └── technical_analysis.py  # Technical indicators
│   ├── yahoo_finance/
│   │   ├── data_exporter.py      # Data export functionality
│   │   └── yahoo_finance_service.py  # Main service
│   └── stock_service.py      # Stock service interface
├── utils/
│   └── debug_utils.py        # Debug logging utilities
├── requirements.txt          # Project dependencies
└── README.md                # This file
```

## Usage

### Basic Usage

```python
from services.stock_service import StockService
from services.yahoo_finance.yahoo_finance_service import YahooFinanceService
from utils.debug_utils import DebugUtils

# Enable debug mode
DebugUtils.set_debug_mode(True)

# Initialize services
yahoo_service = YahooFinanceService()
stock_service = StockService(yahoo_service)

# Fetch stock data
data = stock_service.fetch_stock_data("AAPL", export_financials=True)
```

### Advanced Usage

```python
from services.analysis.financial_analysis import FinancialAnalyzer
from services.analysis.technical_analysis import TechnicalAnalyzer
from services.yahoo_finance.data_exporter import DataExporter

# Calculate financial metrics
metrics = FinancialAnalyzer.calculate_metrics(data)

# Calculate technical indicators
indicators = TechnicalAnalyzer.calculate_indicators(data['history'])

# Export data
DataExporter.export_to_excel("AAPL", data['financials']['yearly'])
```

## Configuration

The application can be configured through the `config/settings.py` file and environment variables:

- API settings (rate limits, retries)
- File paths
- Logging settings
- Analysis parameters

### Google Drive (optional)

Follow the docs guide to enable Google Drive uploads:

- Docs: `docs/GOOGLE_DRIVE_SETUP.md`
- Summary of env vars:
  - `GOOGLE_DRIVE_USE_SERVICE_ACCOUNT` (true|false)
  - `GOOGLE_DRIVE_CREDENTIALS_FILE` (OAuth client JSON)
  - `GOOGLE_APPLICATION_CREDENTIALS` (Service Account JSON)
  - `GOOGLE_DRIVE_FOLDER_ID`
  - `GOOGLE_DRIVE_SCOPES` (default: `https://www.googleapis.com/auth/drive.file`)

## Error Handling

The application uses custom exceptions for better error handling:

- `StockDataException`: Base exception for stock data operations
- `RateLimitException`: Raised when API rate limit is exceeded
- `InvalidSymbolException`: Raised for invalid stock symbols
- `DataFetchException`: Raised for errors in fetching data
- `DataProcessingException`: Raised for errors in processing data
- `ExportException`: Raised for errors in exporting data

## Debug Mode

Debug mode can be enabled/disabled using `DebugUtils`:

```python
from utils.debug_utils import DebugUtils

# Enable debug mode
DebugUtils.set_debug_mode(True)

# Disable debug mode
DebugUtils.set_debug_mode(False)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 