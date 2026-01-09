# Start Redis for Stockport
# Options:
# 1. If Redis is installed: redis-server
# 2. If using Memurai: memurai.exe
# 3. If using Docker: docker run -d -p 6379:6379 --name redis redis
# 4. If using WSL: wsl redis-server

Write-Host 'Checking for Redis...'
if (Get-Command redis-server -ErrorAction SilentlyContinue) {
    Write-Host 'Starting Redis server...'
    Start-Process redis-server -WindowStyle Minimized
    Start-Sleep -Seconds 2
    Write-Host 'Redis should be running on port 6379'
} elseif (Get-Command memurai -ErrorAction SilentlyContinue) {
    Write-Host 'Starting Memurai (Redis-compatible)...'
    Start-Process memurai -WindowStyle Minimized
    Start-Sleep -Seconds 2
    Write-Host 'Memurai should be running on port 6379'
} else {
    Write-Host 'Redis not found. Please install Redis or Memurai.'
    Write-Host 'Download Redis: https://github.com/microsoftarchive/redis/releases'
    Write-Host 'Or Memurai: https://www.memurai.com/get-memurai'
}
