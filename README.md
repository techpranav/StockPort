# Stock Analysis Tool

A comprehensive stock analysis application built with Streamlit that provides fundamental, technical, and portfolio analysis for stocks using Yahoo Finance data.

## Features

- **Single Stock Analysis**: Detailed analysis of individual stocks
- **Mass Stock Analysis**: Batch analysis of multiple stocks from a text file
- **Technical Analysis**: RSI, MACD, Bollinger Bands, Moving Averages
- **Fundamental Analysis**: Financial ratios, balance sheet, cash flow analysis
- **Portfolio Analysis**: Risk metrics, returns analysis, volatility calculations
- **Report Generation**: Excel and Word reports with customizable export options
- **Google Drive Integration**: Automatic upload of reports to Google Drive
- **AI Analysis**: Optional AI-powered insights (requires API key)

## Prerequisites

- Python 3.8 or higher
- Internet connection for stock data fetching
- Google account (optional, for Google Drive integration)

## Installation

### 1. Clone or Download the Repository

```bash
git clone <repository-url>
cd Stockport
```

Or download and extract the ZIP file to a folder named `Stockport`.

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note**: If you encounter issues with `pydrive2`, try:
```bash
pip uninstall pydrive2 pydrive
pip install pydrive2==1.21.3
```

### 3. Set Up Environment Variables (Optional)

Create a `.env` file in the root directory for custom configuration:

```bash
# Google Drive Integration (Optional)
GOOGLE_DRIVE_USE_SERVICE_ACCOUNT=false
GOOGLE_DRIVE_CREDENTIALS_FILE=config/credentials/client_secret.json
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
GOOGLE_DRIVE_SCOPES=https://www.googleapis.com/auth/drive.file

# AI Features (Optional)
OPENAI_API_KEY=your_openai_api_key_here
```

## Quick Start

### 1. Run the Application

```bash
streamlit run ui/pages/main_page.py
```

The application will open in your default web browser at `http://localhost:8501`.

### 2. Basic Usage

1. **Single Stock Analysis**:
   - Enter a stock symbol (e.g., AAPL, MSFT, GOOGL)
   - Adjust historical data period if needed
   - Click "Analyze" to start analysis
   - View results in organized tabs
   - Download reports in Excel or Word format

2. **Mass Stock Analysis**:
   - Create a text file with stock symbols (one per line)
   - Upload the file using the file uploader
   - Click "Analyze All" to process all symbols
   - Monitor progress and view live results
   - Download individual or combined reports

3. **Report History**:
   - View all generated reports
   - Filter by symbol or report type
   - Download or delete reports as needed

## Configuration

### Sidebar Settings

- **Export Options**: Choose which report types to generate (Excel/Word)
- **Analysis Options**: Set historical data period and API call delays
- **Cleanup Options**: Automatically remove old reports
- **Google Drive**: Enable/disable Google Drive integration

### Google Drive Setup (Optional)

1. **OAuth Setup** (Recommended for end users):
   - Click "🔗 Google Drive Setup" in the sidebar
   - Follow the guided setup process
   - Authorize the application once
   - Reports will automatically upload to your Drive

2. **Service Account** (For advanced users):
   - Place `service_account.json` in `config/credentials/`
   - Set `GOOGLE_DRIVE_USE_SERVICE_ACCOUNT=true` in `.env`

## File Structure

```
Stockport/
├── config/                 # Configuration files
│   ├── constants/         # Application constants
│   ├── credentials/       # API keys and credentials
│   └── settings.py        # Application settings
├── core/                  # Core analysis logic
├── services/              # Data and analysis services
├── ui/                    # User interface components
├── utils/                 # Utility functions
├── input/                 # Input files (stock symbols)
├── output/                # Generated reports
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

2. **Google Drive Authentication Issues**:
   - Ensure you have a stable internet connection
   - Check that your Google account has Drive access
   - Verify the OAuth client configuration

3. **Stock Data Not Loading**:
   - Check your internet connection
   - Verify the stock symbol is correct
   - Some stocks may have limited data availability

4. **Memory Issues with Large Files**:
   - Limit the number of symbols in mass analysis
   - Close other applications to free up memory
   - Process stocks in smaller batches

### Performance Tips

- Use shorter historical periods for faster analysis
- Process mass analysis in smaller batches (10-20 symbols)
- Enable cleanup to remove old reports automatically
- Close unused browser tabs to reduce memory usage

## Data Sources

- **Stock Data**: Yahoo Finance (yfinance)
- **Technical Indicators**: TA-Lib (ta)
- **Financial Ratios**: Calculated from company financials
- **AI Analysis**: OpenAI GPT models (optional)

## Security Notes

- API keys are stored locally in `.env` files
- Google Drive credentials are stored securely
- No data is transmitted to external servers (except for stock data fetching)
- Reports are generated and stored locally

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Verify your Python version and dependencies
3. Check the application logs for error messages
4. Ensure all required files are in the correct locations

## License

This tool is provided as-is for educational and analysis purposes. Please ensure compliance with relevant financial data usage terms and conditions.

## Updates

To update the tool:

1. Backup your configuration files
2. Download the latest version
3. Replace the application files
4. Restore your configuration
5. Update dependencies: `pip install -r requirements.txt --upgrade`

---

**Happy Analyzing! 📈** 