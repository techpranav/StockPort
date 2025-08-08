# Technical String Constants and Configuration Keys
# This file contains technical constants, API keys, file patterns, and configuration values

# Directory paths
output_dir="D:\\OneDrive - Technia AB\\Pranav\\Development\\Projects\\Upwork\\StockAnalyzer\\output\\output"
input_dir="D:\\OneDrive - Technia AB\\Pranav\\Development\\Projects\\Upwork\\StockAnalyzer\\input"

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

# File Names (consolidated - removed duplicates)
STOCK_FILE = "stocks.txt"
COMPLETED_FILE = "completed.txt"
FAILED_FILE = "failed.txt"
TEMP_STOCKS_FILE = "temp_stocks.txt"

# Excel Sheet Names
SHEET_COMPANY_INFO = "Company Info"
SHEET_KEY_METRICS = "Key Metrics"
SHEET_TECHNICAL_ANALYSIS = "Technical Analysis"
SHEET_FUNDAMENTAL_ANALYSIS = "Fundamental Analysis"
SHEET_PORTFOLIO_ANALYSIS = "Portfolio Analysis"

# UI Tab Names
TAB_OVERVIEW = "Overview"
TAB_TECHNICAL_ANALYSIS = "Technical Analysis"
TAB_FUNDAMENTAL_ANALYSIS = "Fundamental Analysis"
TAB_PORTFOLIO = "Portfolio"

# DataFrame Column Names
COLUMN_METRIC = "Metric"
COLUMN_VALUE = "Value"
COLUMN_ATTRIBUTE = "Attribute"
COLUMN_INDICATOR = "Indicator"
COLUMN_SERIAL_NUMBER = "Serial Number"
COLUMN_STOCK_NAME = "Stock Name"
COLUMN_OVERVIEW = "Overview"
COLUMN_SUMMARY = "Summary"
COLUMN_DECISION = "Decision"

# Currency and Formatting
CURRENCY_SYMBOL = "$"
PERCENTAGE_SYMBOL = "%"
NOT_AVAILABLE = "N/A"

# Company Info Keys (for UI display)
COMPANY_INFO_KEYS = {
    'name': 'Company Name',
    'sector': 'Sector',
    'industry': 'Industry',
    'market_cap': 'Market Cap',
    'employees': 'Employees',
    'country': 'Country',
    'exchange': 'Exchange',
    'currency': 'Currency',
    'website': 'Website',
    'description': 'Description',
    'phone': 'Phone',
    'address': 'Address',
    'city': 'City',
    'state': 'State',
    'zip_code': 'Zip Code'
}

# Financial Metrics Display Names
FINANCIAL_METRICS_DISPLAY = {
    'revenue': 'Revenue',
    'net_income': 'Net Income',
    'gross_profit': 'Gross Profit',
    'operating_income': 'Operating Income',
    'eps': 'EPS',
    'pe_ratio': 'P/E Ratio',
    'dividend_yield': 'Dividend Yield',
    'beta': 'Beta',
    'total_assets': 'Total Assets',
    'total_liabilities': 'Total Liabilities',
    'total_equity': 'Total Equity',
    'operating_cash_flow': 'Operating Cash Flow',
    'investing_cash_flow': 'Investing Cash Flow',
    'financing_cash_flow': 'Financing Cash Flow',
    'free_cash_flow': 'Free Cash Flow'
}

# Financial Statement Keys
INCOME_STATEMENT_KEYS = [
    "Total Revenue",
    "Cost of Revenue",
    "Gross Profit",
    "Operating Income",
    "Net Income",
    "Basic EPS",
    "Diluted EPS",
    "EBITDA",
    "EBIT",
    "Income Before Tax",
    "Income Tax Expense",
    "Interest Expense",
    "Research Development",
    "Selling General Administrative",
    "Operating Expenses",
    "Other Operating Expenses",
    "Total Operating Expenses"
]

BALANCE_SHEET_KEYS = [
    "Total Assets",
    "Current Assets",
    "Cash And Cash Equivalents",
    "Short Term Investments",
    "Net Receivables",
    "Inventory",
    "Total Current Liabilities",
    "Long Term Debt",
    "Total Liab",
    "Total Stockholder Equity",
    "Retained Earnings",
    "Cash",
    "Short Long Term Debt",
    "Other Stockholder Equity",
    "Property Plant Equipment",
    "Good Will",
    "Intangible Assets",
    "Accounts Payable"
]

CASHFLOW_KEYS = [
    "Total Cash From Operating Activities",
    "Total Cash From Investing Activities",
    "Total Cash From Financing Activities",
    "Change In Cash",
    "Repurchase Of Stock",
    "Net Borrowings",
    "Effect Of Exchange Rate",
    "Change In Inventory",
    "Investments",
    "Dividends Paid",
    "Stock Based Compensation",
    "Free Cash Flow",
    "Capital Expenditure",
    "Net Income",
    "Depreciation",
    "Other Cashflows From Investing Activities",
    "Other Cashflows From Financing Activities"
]

# Financial Statement Types
FINANCIAL_STATEMENT_TYPES = {
    "yearly": {
        "income_statement": "yearly_income_statement",
        "balance_sheet": "yearly_balance_sheet",
        "cashflow": "yearly_cashflow"
    },
    "quarterly": {
        "income_statement": "quarterly_income_statement",
        "balance_sheet": "quarterly_balance_sheet",
        "cashflow": "quarterly_cashflow"
    }
}

# Financial Statement Sheet Names
FINANCIAL_SHEET_NAMES = {
    "yearly": {
        "income_statement": "Yearly Income Statement",
        "balance_sheet": "Yearly Balance Sheet",
        "cashflow": "Yearly Cash Flow"
    },
    "quarterly": {
        "income_statement": "Quarterly Income Statement",
        "balance_sheet": "Quarterly Balance Sheet",
        "cashflow": "Quarterly Cash Flow"
    }
}

# Financial Statement Filter Keys
FINANCIAL_STATEMENT_FILTER_KEYS = {
    "yearly": {
        "income_statement": "yearly_income_statement",
        "balance_sheet": "yearly_balance_sheet",
        "cashflow": "yearly_cashflow"
    },
    "quarterly": {
        "income_statement": "quarterly_income_statement",
        "balance_sheet": "quarterly_balance_sheet",
        "cashflow": "quarterly_cashflow"
    }
}

# Financial Metrics Keys
FINANCIAL_METRICS_KEYS = {
    "income_statement": {
        "revenue": "totalRevenue",
        "gross_profit": "grossProfits",
        "operating_income": "Operating Income",
        "net_income": "Net Income"
    },
    "balance_sheet": {
        "total_assets": "totalAssets",
        "total_liabilities": "Current Liabilities",
        "total_equity": "totalStockholderEquity"
    },
    "cashflow": {
        "operating_cashflow": "operatingCashflow",
        "investing_cashflow": "Investing Cash Flow",
        "financing_cashflow": "Financing Cash Flow"
    }
}

# Export Keys for Financial Statements
BALANCE_SHEET_EXPORT_KEYS = [
    "Treasury Shares Number",
    "Ordinary Shares Number", 
    "Share Issued",
    "Net Debt",
    "Total Debt",
    "Tangible Book Value",
    "Invested Capital",
    "Working Capital",
    "Net Tangible Assets",
    "Capital Lease Obligations",
    "Common Stock Equity",
    "Total Capitalization",
    "Total Equity Gross Minority Interest",
    "Stockholders Equity"
]

INCOME_STATEMENT_EXPORT_KEYS = [
    "Tax Effect Of Unusual Items",
    "Tax Rate For Calcs",
    "Normalized EBITDA",
    "Net Income From Continuing Operation Net Minority Interest",
    "Reconciled Depreciation",
    "Reconciled Cost Of Revenue",
    "EBITDA",
    "EBIT",
    "Net Interest Income",
    "Interest Expense",
    "Interest Income",
    "Normalized Income",
    "Net Income From Continuing And Discontinued Operation",
    "Total Expenses",
    "Total Operating Income As Reported"
]

CASHFLOW_EXPORT_KEYS = [
    "Free Cash Flow",
    "Repurchase Of Capital Stock",
    "Repayment Of Debt",
    "Issuance Of Debt",
    "Issuance Of Capital Stock",
    "Capital Expenditure",
    "Interest Paid Supplemental Data",
    "Income Tax Paid Supplemental Data",
    "End Cash Position",
    "Beginning Cash Position",
    "Changes In Cash",
    "Financing Cash Flow",
    "Cash Flow From Continuing Financing Activities",
    "Net Other Financing Charges",
    "Cash Dividends Paid"
]

# API Related Constants (consolidated - removed duplicates)
API_RETRY_ATTEMPTS = 5
DELAY_BETWEEN_CALLS = 60  # seconds between API calls (was also API_DELAY_SECONDS)
RATE_LIMIT_DELAY = 10

# AI Configuration
CHATGPT = "chatgpt"
OLLAMA = "ollama"
DEFAULT_AI_MODE = CHATGPT

# API Configuration
OPENAI_API_KEY = ""  # Add your OpenAI API key here

# Default Values
DEFAULT_PERIOD = "1y"
DEFAULT_INTERVAL = "1d"
DEFAULT_LIMIT = 5

# Options
AI_MODEL_OPTIONS = ["ChatGPT", "Ollama"] 