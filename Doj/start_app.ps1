# Maintenance Routing Application Startup Script

Write-Host "Starting Maintenance Routing Application..." -ForegroundColor Green

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    exit 1
}

# Check dependencies
Write-Host "Checking dependencies..." -ForegroundColor Cyan
$packages = pip list 2>&1 | Out-String
if ($packages -notmatch "fastapi" -or $packages -notmatch "PyQt5") {
    Write-Host "Installing missing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
} else {
    Write-Host "Dependencies OK" -ForegroundColor Green
}

# Start backend
Write-Host "Starting backend server..." -ForegroundColor Cyan
$backendPath = Join-Path $PSScriptRoot "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; python main.py"

# Wait for backend
Start-Sleep -Seconds 3

# Start UI
Write-Host "Starting PyQt5 UI..." -ForegroundColor Cyan
$uiPath = Join-Path $PSScriptRoot "ui"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$uiPath'; python main_window.py"

Write-Host "Done! Backend: http://localhost:5000 | API Docs: http://localhost:5000/docs" -ForegroundColor Green
Write-Host "Press any key to close this window..." -ForegroundColor Yellow
Read-Host
