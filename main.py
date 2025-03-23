from services.yahoo_finance import *
from ai.chatgpt_api import get_stock_summary, getShortSummary, getOverallShortSummary
from reports.generate_word import generate_word_report
from reports.generate_excel import generate_excel_report
import json
import pandas as pd
import time
import os
from constants.Constants import *
from util.Utils import *
from util.googledrive import *
import traceback
from services.yahoo_finance import YahooFinanceService

STOCK_FILE = f"{input_dir}\\stocks.txt"
COMPLETED_FILE = f"{input_dir}\\completed.txt"
FAILED_FILE = f"{input_dir}\\failed.txt"
EXCEL_FILE = f"{getOutputDirectory()}\\stock_summary.xlsx"


def read_stock_symbols():
    """Reads stock symbols from 'stocks.txt'."""
    if not os.path.exists(STOCK_FILE):
        print(f"{STOCK_FILE} not found!")
        return []
    with open(STOCK_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]


def update_stock_file(remaining_symbols):
    """Writes the remaining symbols back to 'stocks.txt'."""
    with open(STOCK_FILE, "w") as f:
        for symbol in remaining_symbols:
            f.write(symbol + "\n")


def append_to_completed(symbol):
    """Appends a completed stock symbol to 'completed.txt'."""
    with open(COMPLETED_FILE, "a") as f:
        f.write(symbol + "\n")


def append_to_failed(symbol):
    """Appends a failed stock symbol to 'failed.txt'."""
    with open(FAILED_FILE, "a") as f:
        f.write(symbol + "\n")


def save_stock_data_to_file(symbol, data):
    """Save stock data to a JSON file."""
    directory = os.path.join(getOutputDirectory(), symbol)
    os.makedirs(directory, exist_ok=True)
    
    file_path = os.path.join(directory, f"{symbol}_stock_data.json")
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Saved data to {file_path}")


def format_financials(financial_dict, title):
    formatted_str = f"\n### {title} ###\n"
    for key, values in financial_dict.items():
        formatted_str += f"{key}: {values}\n"
    return formatted_str


def process_stock_symbol(stock):
    try:
        print(f"Processing stock: {stock}")
        yf_service = YahooFinanceService()
        
        # Add delay to avoid rate limiting
        time.sleep(2)
        
        # Fetch stock data
        stock_data = yf_service.fetch_stock_data(stock)
        
        # Filter the data
        filtered_data = yf_service.filter_stock_data(stock_data)
        
        # Save the data
        save_stock_data_to_file(stock, filtered_data)
        
        return {
            "symbol": stock,
            "status": "success",
            "data": filtered_data
        }
    except Exception as e:
        print(f"Error processing {stock}: {str(e)}")
        return {
            "symbol": stock,
            "status": "error",
            "error": str(e)
        }


def main():
    stock_symbols = read_stock_symbols()
    if not stock_symbols:
        print("No stock symbols to process.")
        return

    stock_summaries = []
    delay_between_stocks = 5  # Delay between processing different stocks

    for stock in stock_symbols[:]:  # Create a copy to modify list safely
        try:
            print(f"\nProcessing stock: {stock}")
            result = process_stock_symbol(stock)
            stock_summaries.append([
                len(stock_summaries) + 1,
                stock,
                result['status']
            ])

            # Remove stock from list & update file
            stock_symbols.remove(stock)
            update_stock_file(stock_symbols)

            # Append to completed file
            append_to_completed(stock)

            # Add delay before processing next stock
            if stock_symbols:  # Only delay if there are more stocks to process
                print(f"Waiting {delay_between_stocks} seconds before processing next stock...")
                time.sleep(delay_between_stocks)

        except Exception as e:
            print(f"Error processing {stock}: {e}")
            traceback.print_exc()

            # Append the failed symbol to a failed file
            append_to_failed(stock)

            # Remove the failed symbol from the list and update the stock file
            stock_symbols.remove(stock)
            update_stock_file(stock_symbols)

            # Add delay before processing next stock
            if stock_symbols:  # Only delay if there are more stocks to process
                print(f"Waiting {delay_between_stocks} seconds before processing next stock...")
                time.sleep(delay_between_stocks)

            # Continue processing the next symbol
            continue

    print("\nProcessing complete!")


def getFinancialsText(stock_data):
    financials = stock_data["filtered_financials"]
    # Extract and format quarterly financials

    quarterly_financials_string = (
            format_financials(financials["quarterly_income_statement"].to_dict(), "Quarterly Income Statement") +
            format_financials(financials["quarterly_balance_sheet"].to_dict(), "Quarterly Balance Sheet") +
            format_financials(financials["quarterly_cashflow"].to_dict(), "Quarterly Cash Flow Statement")
    )
    yearly_financials_string = (
            format_financials(financials["yearly_income_statement"].to_dict(), "Yearly Income Statement") +
            format_financials(financials["yearly_balance_sheet"].to_dict(), "Yearly Balance Sheet") +
            format_financials(financials["yearly_cashflow"].to_dict(), "Yearly Cash Flow Statement")
    )
    str_financials = quarterly_financials_string + "\n\n" + yearly_financials_string
    return str_financials


if __name__ == "__main__":
    main()
