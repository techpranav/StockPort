from constants.Constants import *
import os
from datetime import datetime

outputDirectory = None

def getSymbolOutputDirectory(stock_symbol):
    ticker_dir = f"{getOutputDirectory()}\\{stock_symbol}"
    os.makedirs(ticker_dir, exist_ok=True)
    return ticker_dir

def getOutputDirectory():
    global outputDirectory
    if outputDirectory is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Assumes 'output_dir' is defined in constants.Constants.
        outputDirectory = f"{output_dir}_{timestamp}"
        os.makedirs(outputDirectory, exist_ok=True)

    return outputDirectory
