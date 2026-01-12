@echo off
title Stock Analysis Tool - Easy Install
color 0E

echo ========================================
echo    Stock Analysis Tool - Easy Install
echo ========================================
echo.
echo 🚀 Starting installation...
echo.

:: Try PowerShell first (more reliable)
echo 🔧 Trying PowerShell installation (recommended)...
powershell -ExecutionPolicy Bypass -File "install_and_run.ps1"

if %errorlevel% neq 0 (
    echo.
    echo ⚠️  PowerShell installation failed, trying batch file...
    echo.
    call install_and_run.bat
)

echo.
echo Installation completed. Press any key to exit...
pause >nul
