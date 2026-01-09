# Start Backend and Frontend Servers
# Kills existing processes on ports 8001 and 8501 first

Write-Host "=== Stockport Server Startup ===" -ForegroundColor Cyan

# Step 1: Kill existing processes
Write-Host "`n[1/4] Checking and killing processes on ports 8001 and 8501..." -ForegroundColor Yellow

# Kill port 8001 (Backend)
$port8001 = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
if ($port8001) {
    $pid8001 = $port8001.OwningProcess
    Write-Host "  Killing process $pid8001 on port 8001..."
    Stop-Process -Id $pid8001 -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Kill port 8501 (Frontend/Streamlit)
$port8501 = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
if ($port8501) {
    $pid8501 = $port8501.OwningProcess
    Write-Host "  Killing process $pid8501 on port 8501..."
    Stop-Process -Id $pid8501 -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Also kill any Python processes that might be holding ports
Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
    $_.Path -like "*stockport*" -or $_.CommandLine -like "*start_backend*" -or $_.CommandLine -like "*streamlit*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "  Ports cleared. Waiting 3 seconds..." -ForegroundColor Green
Start-Sleep -Seconds 3

# Step 2: Activate venv
Write-Host "`n[2/4] Activating virtual environment..." -ForegroundColor Yellow
$venvPath = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "  Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Virtual environment not found at $venvPath" -ForegroundColor Red
}

# Step 3: Start Backend
Write-Host "`n[3/4] Starting Backend Server (port 8001)..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & ".\venv\Scripts\python.exe" ".\start_backend.py"
} -Name "StockportBackend"

Start-Sleep -Seconds 5

# Check if backend started
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/status" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Host "  Backend Server: RUNNING on http://localhost:8001" -ForegroundColor Green
} catch {
    Write-Host "  Backend Server: Starting... (may take a few seconds)" -ForegroundColor Yellow
}

# Step 4: Start Frontend
Write-Host "`n[4/4] Starting Frontend Server (port 8501)..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & ".\venv\Scripts\streamlit.exe" run app.py --server.headless true --server.port 8501
} -Name "StockportFrontend"

Start-Sleep -Seconds 5

# Check if frontend started
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8501" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Host "  Frontend Server: RUNNING on http://localhost:8501" -ForegroundColor Green
} catch {
    Write-Host "  Frontend Server: Starting... (may take a few seconds)" -ForegroundColor Yellow
}

Write-Host "`n=== Servers Starting ===" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8001" -ForegroundColor White
Write-Host "Frontend: http://localhost:8501" -ForegroundColor White
Write-Host "`nMonitoring logs... Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Monitor jobs
try {
    while ($true) {
        # Show backend output
        $backendOutput = Receive-Job -Job $backendJob -ErrorAction SilentlyContinue
        if ($backendOutput) {
            Write-Host "[BACKEND] $backendOutput" -ForegroundColor Cyan
        }
        
        # Show frontend output
        $frontendOutput = Receive-Job -Job $frontendJob -ErrorAction SilentlyContinue
        if ($frontendOutput) {
            Write-Host "[FRONTEND] $frontendOutput" -ForegroundColor Magenta
        }
        
        Start-Sleep -Seconds 2
    }
} finally {
    Write-Host "`nStopping servers..." -ForegroundColor Yellow
    Stop-Job -Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job -Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Write-Host "Servers stopped." -ForegroundColor Green
}

