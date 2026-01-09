# Kill processes on ports 8001 and 8501

Write-Host "Killing processes on ports 8001 and 8501..."

# Kill port 8001 (Backend)
$port8001 = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
if ($port8001) {
    $pid8001 = $port8001.OwningProcess
    Write-Host "Killing process $pid8001 on port 8001..."
    Stop-Process -Id $pid8001 -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Kill port 8501 (Frontend/Streamlit)
$port8501 = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
if ($port8501) {
    $pid8501 = $port8501.OwningProcess
    Write-Host "Killing process $pid8501 on port 8501..."
    Stop-Process -Id $pid8501 -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Also try to kill any Python processes that might be holding the ports
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*stockport*" } | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Ports cleared. Waiting 3 seconds..."
Start-Sleep -Seconds 3

