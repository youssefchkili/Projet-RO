# Stop all running servers

Write-Host "🛑 Stopping Maintenance Routing Application..." -ForegroundColor Red
Write-Host ""

# Stop Python processes (FastAPI/Uvicorn)
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "Stopping Python backend servers..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force
    Write-Host "✅ Python servers stopped" -ForegroundColor Green
} else {
    Write-Host "No Python servers running" -ForegroundColor Gray
}

# Stop Node processes (Vite)
$nodeProcesses = Get-Process node -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host "Stopping Node.js frontend servers..." -ForegroundColor Yellow
    $nodeProcesses | Stop-Process -Force
    Write-Host "✅ Node.js servers stopped" -ForegroundColor Green
} else {
    Write-Host "No Node.js servers running" -ForegroundColor Gray
}

Write-Host ""
Write-Host "✅ All servers stopped successfully!" -ForegroundColor Green
Write-Host ""
