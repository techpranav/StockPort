import yfinance as yf
import pandas as pd


def fetch_financials(stock):
    """Fetches yearly and quarterly financials from Yahoo Finance."""
    ticker = yf.Ticker(stock)

    yearly_income_statement = ticker.financials
    yearly_balance_sheet = ticker.balance_sheet
    yearly_cashflow = ticker.cashflow

    quarterly_income_statement = ticker.quarterly_financials
    quarterly_balance_sheet = ticker.quarterly_balance_sheet
    quarterly_cashflow = ticker.quarterly_cashflow

    return {
        "yearly_income_statement": yearly_income_statement,
        "yearly_balance_sheet": yearly_balance_sheet,
        "yearly_cashflow": yearly_cashflow,
        "quarterly_income_statement": quarterly_income_statement,
        "quarterly_balance_sheet": quarterly_balance_sheet,
        "quarterly_cashflow": quarterly_cashflow,
    }


def export_to_excel(stock, financials):
    """Exports financial data to an Excel file."""
    with pd.ExcelWriter(f"{stock}_financials.xlsx") as writer:
        financials["yearly_income_statement"].to_excel(writer, sheet_name="Yearly Income Statement")
        financials["yearly_balance_sheet"].to_excel(writer, sheet_name="Yearly Balance Sheet")
        financials["yearly_cashflow"].to_excel(writer, sheet_name="Yearly Cash Flow")
        financials["quarterly_income_statement"].to_excel(writer, sheet_name="Quarterly Income Statement")
        financials["quarterly_balance_sheet"].to_excel(writer, sheet_name="Quarterly Balance Sheet")
        financials["quarterly_cashflow"].to_excel(writer, sheet_name="Quarterly Cash Flow")
    print(f"Financial data exported to {stock}_financials.xlsx")


def main():
    stock = "AAPL"  # Replace with any stock symbol
    financials = fetch_financials(stock)
    export_to_excel(stock, financials)


if __name__ == "__main__":
    main()
