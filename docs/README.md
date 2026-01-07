# Stock Analysis Tool

A comprehensive stock analysis tool that provides technical, fundamental, and portfolio analysis for stocks using multiple data providers.

## Features

### Core Analysis
- **Multi-provider support** (Yahoo Finance, Alpha Vantage, NSE, BSE)
- **Data Adapter Layer** - Unified data format across all providers
- **Parallel Processing** - Fast, concurrent analysis of multiple stocks
- **Indian Stock Market Support** - NSE and BSE integration

### Technical Analysis
- **Basic Indicators**
  - Moving Averages (SMA, EMA)
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
- **Intraday Indicators**
  - Stochastic Oscillator
  - ADX (Average Directional Index)
  - ATR (Average True Range)
  - CCI (Commodity Channel Index)
  - Ichimoku Cloud
  - Williams %R
  - MFI (Money Flow Index)
  - Parabolic SAR
  - Fibonacci Retracement
- **Volume Analysis**
  - Volume Profile
  - OBV (On-Balance Volume)
  - CMF (Chaikin Money Flow)
  - Volume Oscillator
  - Unusual Volume Detection
- **Momentum Indicators**
  - ROC (Rate of Change)
  - Momentum
  - PROC (Price Rate of Change)
  - RMI (Relative Momentum Index)
  - TSI (True Strength Index)

### Pattern Recognition
- **Candlestick Patterns**
  - Hammer, Doji, Engulfing, Harami
  - Shooting Star, Morning Star, Evening Star
  - Three Black Crows, Three White Soldiers
- **Chart Patterns**
  - Support/Resistance Levels
  - Trend Lines
  - Triangles (Ascending, Descending, Symmetrical)
  - Head and Shoulders
  - Double Top/Bottom

### Entry Point Detection
- **Signal Scoring** - Multi-factor weighted analysis
- **Entry Signals** - Strong Buy, Buy, Watch, Avoid classifications
- **Risk Metrics** - ATR-based stop-loss, risk-reward ratios, position sizing
- **Confidence Levels** - Signal confidence scoring

### Alerts & Notifications
- **Alert Types** - Price, Signal, Pattern, Volume, Risk alerts
- **Notification Channels** - In-app, Email, Browser Push
- **Real-time Monitoring** - Background alert checking
- **Alert History** - Track alert performance

### Backtesting System
- **Strategy Testing** - Test strategies on historical data
- **Performance Metrics** - Returns, Win Rate, Profit Factor, Max Drawdown, Sharpe Ratio
- **Trade Simulation** - Realistic trade execution with transaction costs
- **Backtest History** - Save, retrieve, and compare backtests

### User-Friendly Features
- **Simple Dashboard** - Non-trading user interface
- **Signal Interpreter** - Plain language explanations
- **Educational Content** - Tooltips and explanations
- **Portfolio Tracking** - Monitor your holdings

### Data Export
- **Advanced Export** - Custom criteria and filters
- **Multiple Formats** - Excel, CSV, JSON, Word
- **Scheduled Exports** - Automated data export
- **Batch Processing** - Export multiple stocks

### Fundamental Analysis
- Financial Statements
- Key Metrics
- Growth Analysis

### Report Generation
- Excel Reports
- Word Reports
- Customizable Templates

## Project Structure

```
stockport/
├── app.py                   # Main Streamlit application entry point
├── config/                  # Configuration and constants
│   ├── app_config.py       # Unified application settings
│   └── constants/          # Application constants
│       ├── NumericConstants.py
│       ├── StringConstants.py
│       ├── DataConstants.py
│       ├── AlertConstants.py
│       ├── BacktestConstants.py
│       └── UIMessages.py
├── core/                    # Core business logic
│   ├── stock_analyzer.py   # Main analysis orchestrator
│   ├── enhanced_analyzer.py # Enhanced analysis with new features
│   ├── parallel_analyzer.py # Parallel processing
│   └── task_queue.py       # Task queue management
├── services/                # Business logic services
│   ├── data_providers/     # Data fetching services
│   │   ├── adapters/       # Data adapter layer
│   │   └── providers/      # Provider implementations
│   ├── analyzers/          # Analysis services
│   │   ├── indicators/     # Technical indicators
│   │   ├── patterns/       # Pattern recognition
│   │   ├── signals/        # Signal generation
│   │   └── risk/           # Risk calculations
│   ├── alerts/             # Alert system
│   ├── backtesting/        # Backtesting engine
│   ├── interpreters/      # Signal translation
│   └── storage/            # Data storage
├── models/                  # Data models
│   ├── stock_data.py       # Stock data models
│   ├── signals.py          # Signal models
│   ├── alert.py            # Alert models
│   ├── backtest_result.py  # Backtest models
│   └── data_schema.py      # Data schema definitions
├── ui/                      # User interface
│   ├── components/          # Reusable UI components
│   └── pages/               # Page-level components
├── utils/                   # Utility functions
│   ├── debug_utils.py       # Logging and debugging
│   └── file_utils.py        # File operations
├── docs/                    # Documentation
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
streamlit run app.py
```

Or use the run script:
```bash
python run_app.py
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