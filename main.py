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


def save_stock_data_to_file(stock_symbol, stock_data):
    """Save stock data (JSON) into a file."""
    processed_data = {str(key): value for key, value in stock_data.items() if not isinstance(value, pd.DataFrame)}
    filename = os.path.join(getSymbolOutputDirectory(stock_symbol), f"{stock_symbol}_stock_data.json")
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(processed_data, file, indent=4, ensure_ascii=False)
    print(f"Stock data saved to: {filename}")


def format_financials(financial_dict, title):
    formatted_str = f"\n### {title} ###\n"
    for key, values in financial_dict.items():
        formatted_str += f"{key}: {values}\n"
    return formatted_str


def process_stock_symbol(stock):
    """Process a single stock symbol and return the results."""
    try:
        print(f"Processing stock: {stock}")
        time.sleep(60)  # Wait 60 seconds to avoid rate limits

        stock_data = fetch_stock_data(stock)
        updated_stock_data = filter_stock_data(stock_data)
        save_stock_data_to_file(stock, updated_stock_data)

        directory = getSymbolOutputDirectory(stock)
        WORD_FILE = f"{directory}\\{stock}_Analysis_Report.docx"
        info = clean_info(updated_stock_data["info"])

        str_financials = getFinancialsText(stock_data)
        gpt_summary = get_stock_summary(stock, updated_stock_data, str_financials)

        word_file = generate_word_report(stock, stock_data, gpt_summary, filename=WORD_FILE)

        # gpt_short_summary = getOverallShortSummary(gpt_summary)
        # gpt_summary_para = getShortSummary(gpt_short_summary)

        # decision = (
        #     "BUY" if "BUY" in gpt_summary.upper() else
        #     "HOLD" if "HOLD" in gpt_summary.upper() else
        #     "SELL" if "SELL" in gpt_summary.upper() else
        #     "NA"
        # )

        # Upload files to Google Drive
        # uploadFilesToDrive(directory)

        return {
            'symbol': stock,
            # 'short_summary': gpt_short_summary,
            # 'summary': gpt_summary_para,
            # 'decision': decision,
            # 'word_file': word_file
        }

    except Exception as e:
        print(f"Error processing {stock}: {e}")
        traceback.print_exc()
        raise e


def main():
    stock_symbols = read_stock_symbols()
    if not stock_symbols:
        print("No stock symbols to process.")
        return

    stock_summaries = []

    for stock in stock_symbols[:]:  # Create a copy to modify list safely
        try:
            result = process_stock_symbol(stock)
            stock_summaries.append([
                len(stock_summaries) + 1,
                stock,
                # result['short_summary'],
                # result['summary'],
                # result['decision']
            ])

            # Remove stock from list & update file
            stock_symbols.remove(stock)
            update_stock_file(stock_symbols)

            # Append to completed file
            append_to_completed(stock)

            # Save Excel file after every iteration
            # generate_excel_report(stock_summaries, EXCEL_FILE)
            # print(f"Excel report updated: {EXCEL_FILE}")

        except Exception as e:
            print(f"Error processing {stock}: {e}")
            traceback.print_exc()

            # Append the failed symbol to a failed file
            append_to_failed(stock)

            # Remove the failed symbol from the list and update the stock file
            stock_symbols.remove(stock)
            update_stock_file(stock_symbols)

            # Continue processing the next symbol
            continue

    print("Processing complete!")


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
