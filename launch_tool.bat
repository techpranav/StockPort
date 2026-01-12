@echo off
title Stock Analysis Tool - Quick Launch
color 0B

echo ========================================
echo    Stock Analysis Tool
echo ========================================
echo.
echo 🚀 Starting the tool...
echo.

:: Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found!
    echo.
    echo Please run 'install_and_run.bat' first to set up the tool.
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Launch Streamlit
echo ✅ Launching application...
echo.
echo The tool will open in your browser at: http://localhost:8501
echo To stop: Close this window or press Ctrl+C
echo.
streamlit run ui/pages/main_page.py

echo.
echo Tool stopped. Press any key to exit...
pause >nul
