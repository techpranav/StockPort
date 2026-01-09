# Simple Server Startup Script
# Kills ports and starts both servers

Write-Host "=== Stockport Server Startup ===" -ForegroundColor Cyan

# Kill existing processes
Write-Host "`n[1/3] Freeing ports..." -ForegroundColor Yellow
$port8001 = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
if ($port8001) {
    Stop-Process -Id $port8001.OwningProcess -Force -ErrorAction SilentlyContinue
}
$port8501 = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
if ($port8501) {
    Stop-Process -Id $port8501.OwningProcess -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

# Activate venv
Write-Host "`n[2/3] Activating venv..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1" | Out-Null

# Start Backend
Write-Host "`n[3/3] Starting servers..." -ForegroundColor Yellow
Write-Host "  Starting Backend (port 8001)..." -ForegroundColor Gray
Start-Process -FilePath ".\venv\Scripts\python.exe" -ArgumentList "start_backend.py" -WindowStyle Minimized

Start-Sleep -Seconds 8

# Start Frontend
Write-Host "  Starting Frontend (port 8501)..." -ForegroundColor Gray
Start-Process -FilePath ".\venv\Scripts\streamlit.exe" -ArgumentList "run", "app.py", "--server.headless", "true", "--server.port", "8501" -WindowStyle Minimized

Start-Sleep -Seconds 8

# Check status
Write-Host "`n=== Server Status ===" -ForegroundColor Cyan
try {
    $b = Invoke-WebRequest -Uri "http://localhost:8001/status" -TimeoutSec 3 -UseBasicParsing
    Write-Host "✓ Backend: RUNNING on http://localhost:8001" -ForegroundColor Green
} catch {
    Write-Host "⚠ Backend: Starting... (may take a few more seconds)" -ForegroundColor Yellow
}

try {
    $f = Invoke-WebRequest -Uri "http://localhost:8501" -TimeoutSec 3 -UseBasicParsing
    Write-Host "✓ Frontend: RUNNING on http://localhost:8501" -ForegroundColor Green
} catch {
    Write-Host "⚠ Frontend: Starting... (may take a few more seconds)" -ForegroundColor Yellow
}

Write-Host "`nServers are starting. Access:" -ForegroundColor White
Write-Host "  Backend:  http://localhost:8001" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop monitoring (servers will continue running)" -ForegroundColor Yellow

