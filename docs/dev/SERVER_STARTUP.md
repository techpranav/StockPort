# Server Startup Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server**
   ```bash
   streamlit run app.py
   ```
   
   Or use the run script:
   ```bash
   python run_app.py
   ```

3. **Access the Application**
   - Local: `http://localhost:8501`
   - Network: `http://<your-ip>:8501`

## Troubleshooting

### Missing Dependencies
If you get `ModuleNotFoundError`, install missing packages:
```bash
pip install <package-name>
```

Common missing packages:
- `bcrypt` - For authentication
- `streamlit` - Core framework
- `pandas`, `numpy` - Data processing
- `yfinance` - Stock data

### Port Already in Use
If port 8501 is already in use:
```bash
streamlit run app.py --server.port 8502
```

### Import Errors
Make sure you're running from the project root directory:
```bash
cd /path/to/stockport
streamlit run app.py
```

### Python Version
The application requires Python 3.8+. Check your version:
```bash
python --version
```

## Background Running

To run in background (Linux/Mac):
```bash
nohup streamlit run app.py > streamlit.log 2>&1 &
```

To run in background (Windows PowerShell):
```powershell
Start-Process streamlit -ArgumentList "run app.py" -WindowStyle Hidden
```

## Monitoring Logs

Check Streamlit logs for errors:
- Default location: Console output
- Log file: Check `streamlit.log` if running in background

## Common Issues

1. **pandas-ta incompatibility**: Removed from requirements (incompatible with Python 3.14)
2. **bcrypt missing**: Added to requirements.txt
3. **Import path issues**: Ensure you're in the project root

