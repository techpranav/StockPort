output_dir="D:\\OneDrive - Technia AB\\Pranav\\Development\\Projects\\Upwork\\StockAnalyzer\\output\\output"
input_dir="D:\\OneDrive - Technia AB\\Pranav\\Development\\Projects\\Upwork\\StockAnalyzer\\input"

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
    "Total Current Assets",
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
        "operating_income": "operatingIncome",
        "net_income": "netIncome"
    },
    "balance_sheet": {
        "total_assets": "totalAssets",
        "total_liabilities": "totalLiab",
        "total_equity": "totalStockholderEquity"
    },
    "cashflow": {
        "operating_cashflow": "totalCashFromOperatingActivities",
        "investing_cashflow": "totalCashFromInvestingActivities",
        "financing_cashflow": "totalCashFromFinancingActivities"
    }
}
