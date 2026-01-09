# Start Backend + UI + Docs with Port Management
# This script kills existing processes, starts servers (backend + Streamlit + MkDocs),
# and monitors error logs.

Write-Host "=== Stockport Server Startup ===" -ForegroundColor Cyan

# Step 1: Kill existing processes
Write-Host "`n[1/5] Freeing ports 8001, 8501, 8000, 8002..." -ForegroundColor Yellow

# Function to kill process on port
function Kill-Port {
    param($Port)
    $conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($conn) {
        $pid = $conn.OwningProcess
        Write-Host "  Killing process $pid on port $Port..."
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
}

Kill-Port 8001
Kill-Port 8501
Kill-Port 8000
Kill-Port 8002

# Kill any Python processes related to stockport
Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
    $_.Path -like "*stockport*" 
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "  Ports cleared. Waiting 3 seconds..." -ForegroundColor Green
Start-Sleep -Seconds 3

# Step 2: Activate venv
Write-Host "`n[2/5] Activating virtual environment..." -ForegroundColor Yellow
$venvPath = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath | Out-Null
    Write-Host "  Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Virtual environment not found" -ForegroundColor Red
    exit 1
}

# Step 3: Start Backend
Write-Host "`n[3/5] Starting Backend Server (port 8001)..." -ForegroundColor Yellow
$backendProcess = Start-Process -FilePath ".\venv\Scripts\python.exe" -ArgumentList "start_backend.py" -PassThru -NoNewWindow -RedirectStandardOutput "backend.log" -RedirectStandardError "backend_error.log"
Write-Host "  Backend process started (PID: $($backendProcess.Id))" -ForegroundColor Green

Start-Sleep -Seconds 8

# Check backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/status" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Host "  ✓ Backend: RUNNING on http://localhost:8001" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Backend: Starting... (check backend.log for details)" -ForegroundColor Yellow
}

# Step 4: Start Frontend (Streamlit UI)
Write-Host "`n[4/5] Starting Frontend Server (port 8501)..." -ForegroundColor Yellow
$frontendProcess = Start-Process -FilePath ".\venv\Scripts\streamlit.exe" -ArgumentList "run", "app.py", "--server.headless", "true", "--server.port", "8501" -PassThru -NoNewWindow -RedirectStandardOutput "frontend.log" -RedirectStandardError "frontend_error.log"
Write-Host "  Frontend process started (PID: $($frontendProcess.Id))" -ForegroundColor Green

Start-Sleep -Seconds 8

# Check frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8501" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Host "  ✓ Frontend: RUNNING on http://localhost:8501" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Frontend: Starting... (check frontend.log for details)" -ForegroundColor Yellow
}

# Step 5: Start Documentation (MkDocs)
Write-Host "`n[5/5] Starting Documentation Servers (dev: 8000, user: 8002)..." -ForegroundColor Yellow

$docsDevProcess = Start-Process -FilePath ".\venv\Scripts\mkdocs.exe" -ArgumentList "serve", "-f", "mkdocs.yml", "-a", "127.0.0.1:8000" -PassThru -NoNewWindow -RedirectStandardOutput "docs_dev.log" -RedirectStandardError "docs_dev_error.log"
Write-Host "  Dev docs process started (PID: $($docsDevProcess.Id))" -ForegroundColor Green

$docsUserProcess = Start-Process -FilePath ".\venv\Scripts\mkdocs.exe" -ArgumentList "serve", "-f", "mkdocs-user.yml", "-a", "127.0.0.1:8002" -PassThru -NoNewWindow -RedirectStandardOutput "docs_user.log" -RedirectStandardError "docs_user_error.log"
Write-Host "  User docs process started (PID: $($docsUserProcess.Id))" -ForegroundColor Green

Start-Sleep -Seconds 4

# Check docs
try {
    $null = Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Host "  ✓ Dev Docs: RUNNING on http://127.0.0.1:8000" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Dev Docs: Starting... (check docs_dev.log for details)" -ForegroundColor Yellow
}

try {
    $null = Invoke-WebRequest -Uri "http://127.0.0.1:8002/" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Host "  ✓ User Docs: RUNNING on http://127.0.0.1:8002" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ User Docs: Starting... (check docs_user.log for details)" -ForegroundColor Yellow
}

Write-Host "`n=== Servers Started ===" -ForegroundColor Cyan
Write-Host "Backend:   http://localhost:8001" -ForegroundColor White
Write-Host "Frontend:  http://localhost:8501" -ForegroundColor White
Write-Host "Dev Docs:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "User Docs: http://127.0.0.1:8002" -ForegroundColor White
Write-Host "`nLogs:" -ForegroundColor Yellow
Write-Host "  Backend:  backend.log, backend_error.log" -ForegroundColor Gray
Write-Host "  Frontend: frontend.log, frontend_error.log" -ForegroundColor Gray
Write-Host "  Dev Docs: docs_dev.log, docs_dev_error.log" -ForegroundColor Gray
Write-Host "  User Docs: docs_user.log, docs_user_error.log" -ForegroundColor Gray
Write-Host "`nTo stop servers, press Ctrl+C or run: Get-Process python | Where-Object {`$_.Path -like '*stockport*'} | Stop-Process" -ForegroundColor Yellow

# Monitor logs
Write-Host "`n=== Monitoring Logs (Press Ctrl+C to stop) ===" -ForegroundColor Cyan
try {
    while ($true) {
        if (Test-Path "backend_error.log") {
            $backendErrors = Get-Content "backend_error.log" -Tail 5 -ErrorAction SilentlyContinue
            if ($backendErrors) {
                Write-Host "[BACKEND ERROR]" -ForegroundColor Red
                $backendErrors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
            }
        }
        
        if (Test-Path "frontend_error.log") {
            $frontendErrors = Get-Content "frontend_error.log" -Tail 5 -ErrorAction SilentlyContinue
            if ($frontendErrors) {
                Write-Host "[FRONTEND ERROR]" -ForegroundColor Red
                $frontendErrors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
            }
        }

        if (Test-Path "docs_dev_error.log") {
            $docsDevErrors = Get-Content "docs_dev_error.log" -Tail 5 -ErrorAction SilentlyContinue
            if ($docsDevErrors) {
                Write-Host "[DEV DOCS ERROR]" -ForegroundColor Red
                $docsDevErrors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
            }
        }

        if (Test-Path "docs_user_error.log") {
            $docsUserErrors = Get-Content "docs_user_error.log" -Tail 5 -ErrorAction SilentlyContinue
            if ($docsUserErrors) {
                Write-Host "[USER DOCS ERROR]" -ForegroundColor Red
                $docsUserErrors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
            }
        }
        
        Start-Sleep -Seconds 5
    }
} finally {
    Write-Host "`nStopping servers..." -ForegroundColor Yellow
    if ($backendProcess -and !$backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    if ($frontendProcess -and !$frontendProcess.HasExited) {
        Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    if ($docsDevProcess -and !$docsDevProcess.HasExited) {
        Stop-Process -Id $docsDevProcess.Id -Force -ErrorAction SilentlyContinue
    }
    if ($docsUserProcess -and !$docsUserProcess.HasExited) {
        Stop-Process -Id $docsUserProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "Servers stopped." -ForegroundColor Green
}

