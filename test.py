import pandas as pd
import requests
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup

import yfinance as yf

def fetch_stock_data( symbol: str) -> pd.DataFrame:
        """Fetch stock data from Yahoo Finance."""
        data = yf.download(symbol, period="1y", interval="1d")
        
        # Log the fetched data
        print(f"Fetched data for {symbol}:\n{data.head()}")  # Log the first few rows of the DataFrame
        
        return data 

print(fetch_stock_data("AAPL"))
