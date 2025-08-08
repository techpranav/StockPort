# String Constants
# This file contains all string constants used throughout the application
# Constants are reused within this file to avoid duplication

import os
from pathlib import Path

# Get the project root directory (two levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Basic String Values (reused throughout)
STR_TECHNICAL_ANALYSIS = "Technical Analysis"
STR_FUNDAMENTAL_ANALYSIS = "Fundamental Analysis"
STR_COMPANY_INFO = "Company Info"
STR_OVERVIEW = "Overview"
STR_PORTFOLIO = "Portfolio"
STR_REVENUE = "Revenue"
STR_NET_INCOME = "Net Income"
STR_GROSS_PROFIT = "Gross Profit"
STR_OPERATING_INCOME = "Operating Income"
STR_TOTAL_ASSETS = "Total Assets"
STR_TOTAL_LIABILITIES = "Total Liabilities"
STR_TOTAL_EQUITY = "Total Equity"
STR_OPERATING_CASH_FLOW = "Operating Cash Flow"
STR_INVESTING_CASH_FLOW = "Investing Cash Flow"
STR_FINANCING_CASH_FLOW = "Financing Cash Flow"
STR_FREE_CASH_FLOW = "Free Cash Flow"
STR_UNKNOWN = "Unknown"
STR_METRIC = "Metric"
STR_VALUE = "Value"
STR_INCOME_STATEMENT = "income_statement"
STR_BALANCE_SHEET = "balance_sheet"
STR_CASHFLOW = "cashflow"
STR_YEARLY = "yearly"
STR_QUARTERLY = "quarterly"

# Directory paths (relative to project root)
output_dir = str(PROJECT_ROOT / "output")
input_dir = str(PROJECT_ROOT / "input")
reports_dir = str(PROJECT_ROOT / "reports")
logs_dir = str(PROJECT_ROOT / "logs")

# File Extensions
EXCEL_EXTENSION = ".xlsx"
WORD_EXTENSION = ".docx"
TEXT_EXTENSION = ".txt"
JSON_EXTENSION = ".json"

# File Name Patterns
REPORT_FILE_PATTERN = "{symbol}_report_{timestamp}"
ANALYSIS_REPORT_FILE_PATTERN = "{symbol}_Analysis_Report"
FINANCIALS_FILE_PATTERN = "{symbol}_financials_{timestamp}"
TECHNICAL_ANALYSIS_FILE_PATTERN = "{symbol}_technical_analysis_{timestamp}"
STOCK_SUMMARY_FILE = "stock_summary"
STOCK_ANALYSIS_FILE = "stock_analysis"

# Directory Names
REPORTS_DIR = "reports"
INPUT_DIR_NAME = "input"
OUTPUT_DIR_NAME = "output"

# File Names
STOCK_FILE = "stocks.txt"
COMPLETED_FILE = "completed.txt"
FAILED_FILE = "failed.txt"
TEMP_STOCKS_FILE = "temp_stocks.txt"

# Excel Sheet Names (reusing constants)
SHEET_COMPANY_INFO = STR_COMPANY_INFO
SHEET_KEY_METRICS = "Key Metrics"
SHEET_TECHNICAL_ANALYSIS = STR_TECHNICAL_ANALYSIS
SHEET_FUNDAMENTAL_ANALYSIS = STR_FUNDAMENTAL_ANALYSIS
SHEET_PORTFOLIO_ANALYSIS = "Portfolio Analysis"

# UI Tab Names (reusing constants)
TAB_OVERVIEW = STR_OVERVIEW
TAB_TECHNICAL_ANALYSIS = STR_TECHNICAL_ANALYSIS
TAB_FUNDAMENTAL_ANALYSIS = STR_FUNDAMENTAL_ANALYSIS
TAB_PORTFOLIO = STR_PORTFOLIO

# DataFrame Column Names (reusing constants)
COLUMN_METRIC = STR_METRIC
COLUMN_VALUE = STR_VALUE
COLUMN_ATTRIBUTE = "Attribute"
COLUMN_INDICATOR = "Indicator"
COLUMN_SERIAL_NUMBER = "Serial Number"
COLUMN_STOCK_NAME = "Stock Name"
COLUMN_OVERVIEW = STR_OVERVIEW
COLUMN_SUMMARY = "Summary"
COLUMN_DECISION = "Decision"

# Currency and Formatting
CURRENCY_SYMBOL = "$"
PERCENTAGE_SYMBOL = "%"
NOT_AVAILABLE = "N/A"

# Company Info Keys (for UI display)
COMPANY_INFO_KEYS = [
    'name', 'sector', 'industry', 'market_cap', 'employees', 'country', 
    'exchange', 'currency', 'website', 'description', 'phone', 'address', 
    'city', 'state', 'zip_code'
]

# Financial Metrics Display Names (reusing constants)
FINANCIAL_METRICS_DISPLAY = {
    'revenue': STR_REVENUE,
    'net_income': STR_NET_INCOME,
    'gross_profit': STR_GROSS_PROFIT,
    'operating_income': STR_OPERATING_INCOME,
    'eps': 'EPS',
    'pe_ratio': 'P/E Ratio',
    'dividend_yield': 'Dividend Yield',
    'beta': 'Beta',
    'total_assets': STR_TOTAL_ASSETS,
    'total_liabilities': STR_TOTAL_LIABILITIES,
    'total_equity': STR_TOTAL_EQUITY,
    'operating_cash_flow': STR_OPERATING_CASH_FLOW,
    'investing_cash_flow': STR_INVESTING_CASH_FLOW,
    'financing_cash_flow': STR_FINANCING_CASH_FLOW,
    'free_cash_flow': STR_FREE_CASH_FLOW
}

# Financial Statement Keys (reusing constants where possible)
STR_TOTAL_REVENUE = "Total Revenue"
STR_COST_OF_REVENUE = "Cost of Revenue"
STR_BASIC_EPS = "Basic EPS"
STR_DILUTED_EPS = "Diluted EPS"
STR_EBITDA = "EBITDA"
STR_EBIT = "EBIT"
STR_CURRENT_ASSETS = "Current Assets"
STR_CASH_AND_CASH_EQUIVALENTS = "Cash And Cash Equivalents"
STR_SHORT_TERM_INVESTMENTS = "Short Term Investments"
STR_NET_RECEIVABLES = "Net Receivables"
STR_INVENTORY = "Inventory"
STR_TOTAL_CURRENT_LIABILITIES = "Total Current Liabilities"
STR_LONG_TERM_DEBT = "Long Term Debt"
STR_TOTAL_LIAB = "Total Liab"
STR_TOTAL_DEBT = "Total Debt"
STR_TOTAL_STOCKHOLDER_EQUITY = "Total Stockholder Equity"
STR_RETAINED_EARNINGS = "Retained Earnings"
STR_CASH = "Cash"
STR_CAPITAL_EXPENDITURE = "Capital Expenditure"
STR_DIVIDENDS_PAID = "Dividends Paid"

INCOME_STATEMENT_KEYS = [
    STR_TOTAL_REVENUE, STR_COST_OF_REVENUE, STR_GROSS_PROFIT, STR_OPERATING_INCOME,
    STR_NET_INCOME, STR_BASIC_EPS, STR_DILUTED_EPS, STR_EBITDA, STR_EBIT,
    "Income Before Tax", "Income Tax Expense", "Interest Expense",
    "Research Development", "Selling General Administrative"
]

BALANCE_SHEET_KEYS = [STR_TOTAL_ASSETS,
    STR_CURRENT_ASSETS, STR_CASH_AND_CASH_EQUIVALENTS,
    STR_SHORT_TERM_INVESTMENTS, STR_NET_RECEIVABLES, STR_INVENTORY,
    STR_TOTAL_CURRENT_LIABILITIES, STR_LONG_TERM_DEBT, STR_TOTAL_LIAB,
    STR_TOTAL_STOCKHOLDER_EQUITY, STR_RETAINED_EARNINGS, STR_CASH
]

CASHFLOW_KEYS = [
    STR_OPERATING_CASH_FLOW, STR_INVESTING_CASH_FLOW, STR_FINANCING_CASH_FLOW,
    STR_FREE_CASH_FLOW, STR_CAPITAL_EXPENDITURE, STR_DIVIDENDS_PAID
]

# Export Keys for Financial Statements (reusing existing lists)
BALANCE_SHEET_EXPORT_KEYS = BALANCE_SHEET_KEYS
INCOME_STATEMENT_EXPORT_KEYS = INCOME_STATEMENT_KEYS
CASHFLOW_EXPORT_KEYS = CASHFLOW_KEYS

# AI Configuration
AI_MODEL_OPTIONS = ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet", "None"]
DEFAULT_AI_MODEL = "gpt-3.5-turbo"

# Default Values
DEFAULT_PERIOD = "1y"

# Financial Statement Filter Keys (reusing constants)
FINANCIAL_STATEMENT_FILTER_KEYS = {
    STR_YEARLY: {
        STR_INCOME_STATEMENT: 'yearly_income_statement',
        STR_BALANCE_SHEET: 'yearly_balance_sheet',
        STR_CASHFLOW: 'yearly_cash_flow'
    },
    STR_QUARTERLY: {
        STR_INCOME_STATEMENT: 'quarterly_income_statement',
        STR_BALANCE_SHEET: 'quarterly_balance_sheet',
        STR_CASHFLOW: 'quarterly_cash_flow'
    }
}

# Financial Sheet Names for Excel export (reusing constants)
FINANCIAL_SHEET_NAMES = {
    STR_YEARLY: {
        STR_INCOME_STATEMENT: 'Yearly Income Statement',
        STR_BALANCE_SHEET: 'Yearly Balance Sheet',
        STR_CASHFLOW: 'Yearly Cash Flow'
    },
    STR_QUARTERLY: {
        STR_INCOME_STATEMENT: 'Quarterly Income Statement',
        STR_BALANCE_SHEET: 'Quarterly Balance Sheet',
        STR_CASHFLOW: 'Quarterly Cash Flow'
    }
}

# Technical Analysis Signal Values
TREND_UPTREND = "Uptrend"
TREND_DOWNTREND = "Downtrend"
TREND_SIDEWAYS = "Sideways"
MOMENTUM_OVERBOUGHT = "Overbought"
MOMENTUM_OVERSOLD = "Oversold"
MOMENTUM_NEUTRAL = "Neutral"
VOLATILITY_HIGH = "High"
VOLATILITY_LOW = "Low"
VOLATILITY_NORMAL = "Normal"
VOLUME_HIGH = "High Volume"
VOLUME_LOW = "Low Volume"
VOLUME_NORMAL = "Normal Volume"

# Technical Indicators Names
INDICATOR_RSI = "RSI"
INDICATOR_MACD = "MACD"
INDICATOR_SMA = "SMA"
INDICATOR_EMA = "EMA"
INDICATOR_BOLLINGER_BANDS = "Bollinger Bands"
INDICATOR_VOLUME = "Volume"

# Data Column Names for Technical Analysis
COLUMN_OPEN = "Open"
COLUMN_HIGH = "High"
COLUMN_LOW = "Low"
COLUMN_CLOSE = "Close"
COLUMN_VOLUME = "Volume"
COLUMN_ADJ_CLOSE = "Adj Close"

# Chart and Analysis Labels
LABEL_TREND = "Trend"
LABEL_MOMENTUM = "Momentum"
LABEL_VOLATILITY = "Volatility"
LABEL_VOLUME = "Volume"
LABEL_PRICE = "Price"
LABEL_DATE = "Date"
LABEL_FREQUENCY = "Frequency"

# Yahoo Finance API Keys
YF_KEY_TOTAL_REVENUE = "totalRevenue"
YF_KEY_GROSS_PROFITS = "grossProfits"
YF_KEY_OPERATING_INCOME = "operatingIncome"
YF_KEY_NET_INCOME = "netIncome"
YF_KEY_TOTAL_ASSETS = "totalAssets"
YF_KEY_TOTAL_LIAB = "totalLiab"
YF_KEY_TOTAL_STOCKHOLDER_EQUITY = "totalStockholderEquity"
YF_KEY_OPERATING_CASHFLOW = "operatingCashflow"
YF_KEY_INVESTING_ACTIVITIES = "totalCashFromInvestingActivities"
YF_KEY_FINANCING_ACTIVITIES = "totalCashFromFinancingActivities"
YF_KEY_SECTOR = "sector"
YF_KEY_INDUSTRY = "industry"
YF_KEY_ENTERPRISE_VALUE = "enterpriseValue"

# Report Types
REPORT_TYPE_EXCEL = "excel"
REPORT_TYPE_WORD = "word"

# Common UI Button Labels
BUTTON_ANALYZE = "Analyze"
BUTTON_EXPORT = "Export"
BUTTON_UPLOAD = "Upload"
BUTTON_DELETE = "Delete" 