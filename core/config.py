import os
from pathlib import Path
import yfinance as yf
import pandas as pd

# Feature Flags
ENABLE_AI_FEATURES = False  # Set to True to enable AI analysis
ENABLE_GOOGLE_DRIVE = False  # Set to True to enable Google Drive integration
ENABLE_TECHNICAL_ANALYSIS = True  # Set to True to enable technical analysis features
ENABLE_FUNDAMENTAL_ANALYSIS = True  # Set to True to enable fundamental analysis features
ENABLE_PORTFOLIO_ANALYSIS = True  # Set to True to enable portfolio analysis features

# Base directories
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Create directories if they don't exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# File paths
STOCK_FILE = os.path.join(INPUT_DIR, "stocks.txt")
COMPLETED_FILE = os.path.join(INPUT_DIR, "completed_stocks.txt")
FAILED_FILE = os.path.join(INPUT_DIR, "failed_stocks.txt")
EXCEL_FILE = os.path.join(OUTPUT_DIR, "stock_analysis.xlsx")

# AI Configuration
CHATGPT = "chatgpt"
OLLAMA = "ollama"
DEFAULT_AI_MODE = CHATGPT

# API Configuration
OPENAI_API_KEY = ""  # Add your OpenAI API key here

# Financial Statement Keys
INCOME_STATEMENT_KEYS = [
    "totalRevenue",
    "grossProfits",
    "operatingIncome",
    "netIncome",
    "ebitda"
]

BALANCE_SHEET_KEYS = [
    "totalAssets",
    "totalLiabilities",
    "totalStockholderEquity",
    "cashAndCashEquivalents",
    "totalDebt"
]

CASHFLOW_KEYS = [
    "totalCashFromOperatingActivities",
    "totalCashFromInvestingActivities",
    "totalCashFromFinancingActivities",
    "freeCashFlow"
]

# Rate Limiting
DELAY_BETWEEN_CALLS = 60  # seconds between API calls 

# class YahooFinanceService:
#     def fetch_stock_data(self, symbol: str) -> pd.DataFrame:
#         """Fetch stock data from Yahoo Finance."""
#         data = yf.download(symbol, period="1y", interval="1d")
#
#         # Log the fetched data
#         print(f"Fetched data for {symbol}:\n{data.head()}")  # Log the first few rows of the DataFrame
#
#         return data