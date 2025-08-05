# User-Facing Messages, Labels, and Headers
# This file contains all user-visible text including headers, labels, messages, and UI strings

# UI Headers and Titles
HEADER_SINGLE_STOCK_ANALYSIS = "Single Stock Analysis"
HEADER_MASS_ANALYSIS = "Mass Analysis"
HEADER_MASS_STOCK_ANALYSIS = "Mass Stock Analysis"
HEADER_CONFIGURATION = "Configuration"
HEADER_EXPORT_OPTIONS = "Export Options"
HEADER_AI_ANALYSIS_OPTIONS = "AI Analysis Options"
HEADER_GOOGLE_DRIVE_OPTIONS = "Google Drive Options"
HEADER_CLEANUP_OPTIONS = "Cleanup Options"
HEADER_ANALYSIS_OPTIONS = "Analysis Options"

# UI Labels
LABEL_EXPORT_WORD_REPORT = "Export Word Report"
LABEL_EXPORT_EXCEL_REPORT = "Export Excel Report"
LABEL_AI_MODEL = "AI Model"
LABEL_UPLOAD_TO_DRIVE = "Upload to Google Drive"
LABEL_CLIENT_SECRETS_FILE = "Upload Client Secrets File"
LABEL_DELETE_REPORTS_OLDER = "Delete reports older than (days)"
LABEL_DAYS_HISTORICAL_DATA = "Days of historical data"
LABEL_DELAY_API_CALLS = "Delay between API calls (seconds)"

# Help Text
HELP_DISABLE_CLEANUP = "Set to 0 to disable automatic cleanup"
HELP_DISABLE_RATE_LIMITING = "Set to 0 to disable rate limiting"

# UI Section Headers (with emojis)
SECTION_FINANCIAL_METRICS = "#### 📊 Financial Metrics"
SECTION_COMPANY_INFO = "#### 🏢 Company Information"
SECTION_TECHNICAL_ANALYSIS = "#### 📈 Technical Analysis"
SECTION_BALANCE_SHEET = "#### 💰 Balance Sheet Summary"
SECTION_CASH_FLOW = "#### 💸 Cash Flow Summary"
SECTION_AI_ANALYSIS = "#### 🤖 AI Analysis"

# Status Messages
MSG_NO_FINANCIAL_METRICS = "No financial metrics available"
MSG_NO_COMPANY_INFO = "No company information available"
MSG_NO_TECHNICAL_DATA = "No technical analysis data available"
MSG_NO_FUNDAMENTAL_DATA = "No fundamental analysis data available"
MSG_NO_PORTFOLIO_DATA = "No portfolio analysis data available"
MSG_ANALYSIS_COMPLETE = "Analysis complete for {total_stocks} stocks"
MSG_NO_DATA_AVAILABLE = "No data available"
MSG_NO_VALID_SYMBOLS = "No valid stock symbols found in the file"
MSG_PROCESSING_SYMBOL = "Processing {symbol}..."

# Word Document Headers
DOC_HEADER_COMPANY_INFO = "Company Information"
DOC_HEADER_INCOME_STATEMENT = "Income Statement"
DOC_HEADER_BALANCE_SHEET = "Balance Sheet"
DOC_HEADER_CASH_FLOW = "Cash Flow Statement"
DOC_HEADER_AI_SUMMARY = "AI Analysis Summary"

# Log Messages
LOG_FETCHING_DATA = "Fetching data for {symbol}"
LOG_DATA_FETCHED = "Successfully fetched data for {symbol}"
LOG_ERROR_FETCHING = "Error fetching data for {symbol}: {error}"
LOG_PROCESSING_STOCK = "Processing stock: {symbol}"
LOG_STOCK_PROCESSED = "Successfully processed stock: {symbol}"
LOG_ERROR_PROCESSING = "Error processing stock {symbol}: {error}"

# Error Messages
ERROR_SYMBOL_NOT_FOUND = "Symbol not found: {symbol}"
ERROR_DATA_FETCH_FAILED = "Failed to fetch data for {symbol}"
ERROR_RATE_LIMIT = "Rate limit exceeded. Please try again later."
ERROR_INVALID_SYMBOL = "Invalid symbol: {symbol}"
ERROR_NO_DATA_AVAILABLE = "No data available for {symbol}"
ERROR_PROCESSING_STOCK = "Error processing stock {symbol}: {error}"
ERROR_ANALYZING_SYMBOL = "Error analyzing {symbol}: {error}"
ERROR_MASS_ANALYSIS = "Error in mass analysis: {error}"

# Success Messages
SUCCESS_DATA_SAVED = "Data saved successfully for {symbol}"
SUCCESS_REPORT_GENERATED = "Report generated successfully for {symbol}"
SUCCESS_ANALYSIS_COMPLETE = "Analysis completed successfully"

# Button Labels
BUTTON_ANALYZE = "Analyze"
BUTTON_ANALYZE_STOCK = "Analyze Stock"
BUTTON_ANALYZE_ALL = "Analyze All"
BUTTON_DOWNLOAD_WORD = "Download Word Report"
BUTTON_DOWNLOAD_EXCEL = "Download Excel Report"

# Input Placeholders
PLACEHOLDER_STOCK_SYMBOL = "e.g., AAPL"
PLACEHOLDER_UPLOAD_FILE = "Upload Stock Symbols File"

# Navigation Labels
NAV_CHOOSE_ANALYSIS_TYPE = "Choose Analysis Type"

# Form Labels
FORM_ENTER_STOCK_SYMBOL = "Enter Stock Symbol"
FORM_UPLOAD_SYMBOLS_FILE = "Upload Stock Symbols File"

# Technical Indicators Labels
TECH_CURRENT_PRICE = "Current Price"
TECH_SMA_20 = "20-Day SMA"
TECH_SMA_50 = "50-Day SMA"
TECH_SMA_200 = "200-Day SMA"
TECH_RSI = "RSI"
TECH_MACD = "MACD"
TECH_BOLLINGER_BANDS = "Bollinger Bands"
TECH_VOLUME = "Volume"

# Financial Ratios Labels
RATIO_PE = "P/E Ratio"
RATIO_PB = "P/B Ratio"
RATIO_PS = "P/S Ratio"
RATIO_DEBT_TO_EQUITY = "Debt-to-Equity"
RATIO_CURRENT = "Current Ratio"
RATIO_QUICK = "Quick Ratio"
RATIO_ROE = "Return on Equity"
RATIO_ROA = "Return on Assets"
RATIO_GROSS_MARGIN = "Gross Margin"
RATIO_OPERATING_MARGIN = "Operating Margin"
RATIO_NET_MARGIN = "Net Margin"

# Analysis Summary Labels
SUMMARY_SUCCESSFUL_ANALYSES = "Successful Analyses"
SUMMARY_FAILED_ANALYSES = "Failed Analyses"
SUMMARY_TOTAL_PROCESSED = "Total Processed"
SUMMARY_SUCCESS_RATE = "Success Rate"

# File Upload Messages
UPLOAD_SUCCESS = "File uploaded successfully"
UPLOAD_ERROR = "Error uploading file"
UPLOAD_INVALID_FORMAT = "Invalid file format. Please upload a .txt file"
UPLOAD_DRAG_DROP = "Drag and drop your file here, or click to browse"

# Processing Status Messages
STATUS_INITIALIZING = "Initializing analysis..."
STATUS_FETCHING_DATA = "Fetching stock data..."
STATUS_ANALYZING = "Performing analysis..."
STATUS_GENERATING_REPORT = "Generating reports..."
STATUS_COMPLETE = "Analysis complete!"
STATUS_ERROR = "An error occurred during analysis"

# Validation Messages
VALIDATION_SYMBOL_REQUIRED = "Stock symbol is required"
VALIDATION_FILE_REQUIRED = "Please upload a file with stock symbols"
VALIDATION_INVALID_SYMBOL = "Invalid stock symbol format"
VALIDATION_SYMBOL_TOO_LONG = "Stock symbol is too long" 