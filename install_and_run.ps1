# Stock Analysis Tool - Complete Installation (PowerShell)
# Run this script as Administrator for best results

param(
    [switch]$Force
)

# Set execution policy if needed
if ($Force -or (Get-ExecutionPolicy) -eq "Restricted") {
    Write-Host "🔧 Setting execution policy..." -ForegroundColor Yellow
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Stock Analysis Tool Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if Python is installed
function Test-PythonInstalled {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
    }
    catch {
        # Python not in PATH
    }
    
    # Check common Python installation paths
    $pythonPaths = @(
        "C:\Python*",
        "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python*",
        "C:\Program Files\Python*",
        "C:\Program Files (x86)\Python*"
    )
    
    foreach ($path in $pythonPaths) {
        if (Test-Path $path) {
            return $true
        }
    }
    
    return $false
}

# Function to install Python
function Install-Python {
    Write-Host "🔧 Python not found. Installing automatically..." -ForegroundColor Yellow
    Write-Host ""
    
    # Create temp directory
    $tempDir = "temp_python_install"
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $tempDir | Out-Null
    
    try {
        # Download Python installer
        $pythonUrl = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
        $installerPath = "$tempDir\python-installer.exe"
        
        Write-Host "📥 Downloading Python 3.11.8..." -ForegroundColor Blue
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
        
        if (-not (Test-Path $installerPath)) {
            throw "Failed to download Python installer"
        }
        
        Write-Host "✅ Download completed" -ForegroundColor Green
        Write-Host ""
        Write-Host "🔧 Installing Python (this may take a few minutes)..." -ForegroundColor Yellow
        Write-Host "⚠️  The installer will run silently with optimal settings" -ForegroundColor Red
        
        # Run installer silently
        $process = Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0", "Include_pip=1" -Wait -PassThru
        
        if ($process.ExitCode -ne 0) {
            throw "Python installation failed with exit code: $($process.ExitCode)"
        }
        
        Write-Host "✅ Python installation completed" -ForegroundColor Green
        
        # Refresh environment variables
        Write-Host "🔄 Refreshing environment variables..." -ForegroundColor Yellow
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # Test Python
        Start-Sleep -Seconds 5
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python is now available: $pythonVersion" -ForegroundColor Green
        } else {
            throw "Python installation verification failed"
        }
        
    }
    catch {
        Write-Host "❌ Error during Python installation: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install Python manually from: https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
    finally {
        # Cleanup
        if (Test-Path $tempDir) {
            Remove-Item $tempDir -Recurse -Force
        }
    }
}

# Check if Python is installed
if (-not (Test-PythonInstalled)) {
    Install-Python
} else {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
}

Write-Host ""

# Check if pip is available
try {
    $pipVersion = pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ pip found: $pipVersion" -ForegroundColor Green
    } else {
        throw "pip not working"
    }
}
catch {
    Write-Host "❌ pip is not available" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Installing pip..." -ForegroundColor Yellow
    python -m ensurepip --upgrade
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install pip" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ pip installed" -ForegroundColor Green
}

Write-Host ""

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "🔧 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

Write-Host ""

# Activate virtual environment and install dependencies
Write-Host "🔧 Installing dependencies..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "🔧 Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host "🔧 Installing required packages..." -ForegroundColor Yellow
Write-Host "⏳ This may take 5-10 minutes on first run..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Write-Host ""
    Write-Host "Trying alternative installation method..." -ForegroundColor Yellow
    pip install --user -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Installation failed completely" -ForegroundColor Red
        Write-Host ""
        Write-Host "Common solutions:" -ForegroundColor Yellow
        Write-Host "1. Check your internet connection" -ForegroundColor White
        Write-Host "2. Try running as Administrator" -ForegroundColor White
        Write-Host "3. Disable antivirus temporarily" -ForegroundColor White
        Write-Host "4. Check Windows Defender settings" -ForegroundColor White
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
Write-Host ""

# Launch the application
Write-Host "🚀 Launching Stock Analysis Tool..." -ForegroundColor Green
Write-Host ""
Write-Host "The tool will open in your default web browser." -ForegroundColor White
Write-Host "If it doesn't open automatically, go to: http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "To stop the tool, close this window or press Ctrl+C" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue"

# Launch Streamlit
try {
    streamlit run ui/pages/main_page.py
}
catch {
    Write-Host "❌ Failed to launch Streamlit: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Tool stopped. Press Enter to exit..." -ForegroundColor Yellow
Read-Host
