# Stock Analysis Tool

A comprehensive stock analysis tool that provides technical, fundamental, and portfolio analysis for stocks using multiple data providers.

## Features

- Multi-provider support (Yahoo Finance, Alpha Vantage, etc.)
- Technical Analysis
  - Moving Averages (SMA)
  - RSI
  - MACD
  - Bollinger Bands
  - Volume Analysis
- Fundamental Analysis
  - Financial Statements
  - Key Metrics
  - Growth Analysis
- Portfolio Analysis
  - Risk Metrics
  - Return Analysis
  - Market Metrics
- Report Generation
  - Excel Reports
  - Word Reports
  - Customizable Templates

## Project Structure

```
stockport/
├── app/
│   ├── main.py              # Main Streamlit application
│   └── run_app.py           # Application runner
├── constants/
│   └── Constants.py         # Global constants and configurations
├── models/
│   └── stock_data.py        # Data models and structures
├── services/
│   ├── stock_data_provider.py    # Provider interface
│   ├── stock_data_factory.py     # Provider factory
│   ├── yahoo_finance.py          # Yahoo Finance provider
│   └── report_service.py         # Report generation service
├── docs/
│   ├── README.md            # This file
│   ├── architecture.md      # System architecture
│   ├── providers.md         # Data provider documentation
│   ├── models.md            # Data model documentation
│   └── services.md          # Service documentation
└── requirements.txt         # Project dependencies
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/stockport.git
cd stockport
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

## Usage

1. Start the Streamlit application:
```bash
python app/run_app.py
```

2. Access the web interface at `http://localhost:8501`

3. Upload a file containing stock symbols (one per line) or enter symbols manually

4. View and download analysis reports

## Configuration

The application can be configured through the following files:

- `constants/Constants.py`: Global constants and configurations
- `app/config.py`: Application-specific settings
- Environment variables for API keys and other sensitive data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 