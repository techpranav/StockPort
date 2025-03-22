import pandas as pd
import yfinance as yf
import time
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

# Constants
SP500_WIKI_URL = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
START_DATE = '2020-02-10'
END_DATE = '2023-11-18'
EXPORT_FILE = 'sp500_top200_analysis.xlsx'


def fetch_sp500_symbols(top_n=200):
    """Fetches the top N S&P 500 symbols from Wikipedia."""
    try:
        tables = pd.read_html(SP500_WIKI_URL)
        sp500_table = tables[0]
        symbols = sp500_table['Symbol'].tolist()
        return symbols[:top_n]
    except Exception as e:
        print(f"Error fetching S&P 500 symbols: {e}")
        return []


def fetch_historical_data(symbol, start_date, end_date):
    """Fetches historical stock data for a given symbol."""
    try:
        data = yf.download(symbol, start=start_date, end=end_date)
        if data.empty:
            print(f"No data found for {symbol}")
            return None
        data['Symbol'] = symbol
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def calculate_metrics(data):
    """Calculates turnover, daily change, change rate, and highest price."""
    if data is None or data.empty:
        return None, None

    # Ensure 'Change' is calculated as a single-column Series
    print(data)

    # Reset index to ensure it starts from 0
    data.reset_index(drop=True, inplace=True)

    # Initialize lists to store calculated values
    change_values = [0]  # First row has no previous value, so Change = 0
    change_rate_values = [0]  # First row has no previous value, so Change Rate = 0%

    # Compute Change and Change Rate using .iloc[]
    for i in range(1, len(data)):
        change = data.iloc[i]['Close'] - data.iloc[i - 1]['Close']  # Current Close - Previous Close
        change_rate = (change / data.iloc[i - 1]['Close']) * 100  # Percentage Change

        change_values.append(change)
        change_rate_values.append(change_rate)

    # Assign computed values back to the DataFrame
    data['Change'] = change_values
    data['Change Rate'] = change_rate_values

    # # Fill NaN values caused by diff() and shift()
    # data['Change Rate'].fillna(0, inplace=True)

    # Calculate Turnover
    data['Turnover'] = data['Volume'] * data['Close']

    # Determine Highest Price
    highest_price = data['High'].max()

    return data, highest_price


def process_sp500_data(top_n=200):
    """Main function to fetch and process S&P 500 data."""
    symbols = fetch_sp500_symbols(top_n)
    if not symbols:
        print("No symbols retrieved. Exiting.")
        return None, None

    all_data = []
    highest_prices = []

    for symbol in symbols:
        print(f"Fetching data for {symbol}...")
        data = fetch_historical_data(symbol, START_DATE, END_DATE)
        if data is not None:
            data, highest_price = calculate_metrics(data)
            if data is not None:
                all_data.append(data)
            highest_prices.append({'Symbol': symbol, 'Highest Price': highest_price})
        time.sleep(1)  # To avoid hitting API rate limits

    # Combine all stock data into a single DataFrame
    if all_data:
        final_df = pd.concat(all_data)
        highest_prices_df = pd.DataFrame(highest_prices)
        return final_df, highest_prices_df
    return None, None


def export_to_excel(stock_data, highest_prices, filename):
    """Exports stock data and highest prices to an Excel file."""
    if stock_data is None or highest_prices is None:
        print("No data to export.")
        return

    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Stock Data"

    # Convert stock data to rows and append to worksheet
    for row in dataframe_to_rows(stock_data, index=True, header=True):
        ws1.append([cell if not isinstance(cell, pd.Series) else cell.iloc[0] for cell in row])  # Ensure single values

    # Create another sheet for highest prices
    ws2 = wb.create_sheet(title="Highest Prices")
    for row in dataframe_to_rows(highest_prices, index=False, header=True):
        ws2.append([cell if not isinstance(cell, pd.Series) else cell.iloc[0] for cell in row])  # Ensure single values

    wb.save(filename)
    print(f"Data exported to {filename}")


def main():
    print("Starting S&P 500 data processing...")
    stock_data, highest_prices = process_sp500_data(top_n=1)
    if stock_data is not None and highest_prices is not None:
        export_to_excel(stock_data, highest_prices, EXPORT_FILE)
    print("Process completed.")


if __name__ == "__main__":
    main()
