#!/bin/bash

# Stock Analysis Tool - Quick Launch
# For macOS and Linux users

echo "========================================"
echo "   Stock Analysis Tool"
echo "========================================"
echo

echo "🚀 Starting the tool..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo
    echo "Please run 'install_and_run.sh' first to set up the tool."
    echo
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Launch Streamlit
echo "✅ Launching application..."
echo
echo "The tool will open in your browser at: http://localhost:8501"
echo "To stop: Press Ctrl+C"
echo

streamlit run ui/pages/main_page.py

echo
echo "Tool stopped."
