import os
from constants.StringConstants import output_dir
from datetime import datetime

outputDirectory = None

def getSymbolOutputDirectory(stock_symbol):
    ticker_dir = f"{output_dir}\\{stock_symbol}"
    os.makedirs(ticker_dir, exist_ok=True)
    return ticker_dir

def getOutputDirectory():
    """
    Create and return the output directory path.
    """
    os.makedirs(output_dir, exist_ok=True)
    return output_dir
