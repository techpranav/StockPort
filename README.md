# Stock Port

A comprehensive stock analysis application that provides technical and fundamental analysis of stocks, portfolio management, and AI-powered insights.

## Features

- **Technical Analysis**
  - Price charts with multiple indicators (MACD, RSI, etc.)
  - Support and resistance levels
  - Volume analysis
  - Trend analysis

- **Fundamental Analysis**
  - Financial ratios calculation
  - Company financials analysis
  - Sector comparison
  - Valuation metrics

- **Portfolio Management**
  - Portfolio tracking
  - Performance metrics
  - Risk analysis
  - Sector allocation
  - Recommendations

- **AI Integration**
  - Stock analysis summaries
  - Investment recommendations
  - Market sentiment analysis

## Installation

1. Clone the repository:
```bash
git clone https://bitbucket.org/yourusername/stock-analyzer.git
cd stock-analyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file with the following variables:
```
OPENAI_API_KEY=your_openai_api_key
GOOGLE_DRIVE_CREDENTIALS=your_google_drive_credentials
```

## Usage

1. Start the application:
```bash
streamlit run app/main.py
```

2. Access the web interface at `http://localhost:8501`

## Project Structure

```
stock-analyzer/
├── app/
│   ├── components/
│   │   ├── analysis.py
│   │   ├── portfolio.py
│   │   └── sidebar.py
│   └── main.py
├── core/
│   ├── config.py
│   └── stock_analyzer.py
├── services/
│   ├── ai_service.py
│   ├── fundamental_analysis.py
│   ├── portfolio_service.py
│   ├── report_service.py
│   ├── technical_analysis.py
│   └── yahoo_finance.py
├── utils/
│   ├── drive_utils.py
│   └── file_utils.py
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 