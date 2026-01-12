@echo off
title Stock Analysis Tool - Complete Installation
color 0A

echo ========================================
echo    Stock Analysis Tool Setup
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed
    echo.
    echo 🔧 Automatically downloading and installing Python...
    echo.
    
    :: Create temp directory for downloads
    if not exist "temp" mkdir temp
    cd temp
    
    :: Download Python installer (latest 3.11.x for Windows)
    echo 📥 Downloading Python 3.11.8 (latest stable)...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python-installer.exe'}"
    
    if not exist "python-installer.exe" (
        echo ❌ Failed to download Python installer
        echo.
        echo Please download Python manually from: https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during installation
        echo.
        pause
        exit /b 1
    )
    
    echo ✅ Python installer downloaded
    echo.
    echo 🔧 Installing Python (this may take a few minutes)...
    echo ⚠️  IMPORTANT: In the installer, check "Add Python to PATH" and "Install for all users"
    echo.
    
    :: Run Python installer silently with PATH option
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    echo.
    echo ⏳ Waiting for Python installation to complete...
    timeout /t 30 /nobreak >nul
    
    :: Clean up installer
    del python-installer.exe
    cd ..
    rmdir temp
    
    :: Refresh environment variables
    echo 🔄 Refreshing environment variables...
    call refreshenv.cmd 2>nul
    if %errorlevel% neq 0 (
        echo 🔄 Refreshing PATH manually...
        set PATH=%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\Scripts
        set PATH=%PATH%;C:\Program Files\Python311;C:\Program Files\Python311\Scripts
    )
    
    :: Test Python again
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Python installation may not have completed properly
        echo.
        echo Please restart your computer and try again, or install Python manually
        echo from: https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    )
    
    echo ✅ Python installed successfully!
) else (
    echo ✅ Python found: 
    python --version
)

echo.

:: Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip is not available
    echo.
    echo 🔧 Installing pip...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo ❌ Failed to install pip
        echo.
        echo Please reinstall Python and ensure pip is included
        echo.
        pause
        exit /b 1
    )
    echo ✅ pip installed
) else (
    echo ✅ pip found
)

echo.

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 🔧 Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

echo.

:: Activate virtual environment and install dependencies
echo 🔧 Installing dependencies...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated
echo.

:: Upgrade pip
echo 🔧 Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo 🔧 Installing required packages...
echo ⏳ This may take 5-10 minutes on first run...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    echo.
    echo Trying alternative installation method...
    pip install --user -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Installation failed completely
        echo.
        echo Common solutions:
        echo 1. Check your internet connection
        echo 2. Try running as administrator
        echo 3. Disable antivirus temporarily
        echo.
        pause
        exit /b 1
    )
)

echo ✅ Dependencies installed successfully
echo.

:: Launch the application
echo 🚀 Launching Stock Analysis Tool...
echo.
echo The tool will open in your default web browser.
echo If it doesn't open automatically, go to: http://localhost:8501
echo.
echo To stop the tool, close this window or press Ctrl+C
echo.
pause

:: Launch Streamlit
streamlit run ui/pages/main_page.py

echo.
echo Tool stopped. Press any key to exit...
pause >nul
