@echo off
echo ========================================
echo YueTransfer with Google OAuth Login
echo ========================================
echo.

REM Check if conda environment is activated
if "%CONDA_DEFAULT_ENV%"=="totalsegmentator" (
    echo ✅ Conda environment: totalsegmentator
) else (
    echo ⚠️  Activating totalsegmentator environment...
    call conda activate totalsegmentator
)

echo.
echo 🚀 Starting YueTransfer Server with Google OAuth...
echo.
echo ⚠️  IMPORTANT: Make sure you have configured Google OAuth credentials!
echo     Check google_oauth_setup.md for detailed instructions.
echo.
echo 🌐 Web Interface: http://localhost:5000
echo 🔑 Login Methods:
echo    - Traditional: pokpok/pokpok, aaa/aaa, bbb/bbb, ccc/ccc
echo    - Google OAuth: Click "Sign in with Google" button
echo.
echo Press Ctrl+C to stop the server
echo ========================================

python start_server_step3_google.py

pause 