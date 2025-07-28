# YueTransfer Server Startup Script (CSRF Disabled) for PowerShell
Write-Host "🚀 Starting YueTransfer Server (CSRF Disabled)..." -ForegroundColor Green

# Set the Python path
$pythonPath = "C:\Users\ZERO\.conda\envs\totalsegmentator\python.exe"

# Check if Python exists
if (Test-Path $pythonPath) {
    Write-Host "✅ Found Python at: $pythonPath" -ForegroundColor Green
    
    # Start the application
    Write-Host "🌐 Starting web server..." -ForegroundColor Yellow
    & $pythonPath start_server_no_csrf.py
} else {
    Write-Host "❌ Python not found at: $pythonPath" -ForegroundColor Red
    Write-Host "Please check your conda environment setup." -ForegroundColor Red
}

Write-Host "Press any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 