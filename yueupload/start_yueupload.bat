@echo off
echo 🚀 Starting YUEUPLOAD with correct Python environment
echo ================================================
echo.
echo Using totalsegmentator conda environment (Python 3.10.13)
echo for compatibility with YUETransfer and TotalSegmentator
echo.

REM Use the totalsegmentator conda environment Python
set PYTHON_PATH=C:\Users\ZERO\.conda\envs\totalsegmentator\python.exe

REM Check if the Python path exists
if not exist "%PYTHON_PATH%" (
    echo ❌ Error: totalsegmentator conda environment not found
    echo Expected path: %PYTHON_PATH%
    echo.
    echo Please ensure the totalsegmentator conda environment is installed.
    echo.
    pause
    exit /b 1
)

echo ✅ Found Python: %PYTHON_PATH%
echo.

REM Change to the yueupload directory
cd /d "%~dp0"

REM Run yueupload with the correct Python environment
echo 🎯 Starting YUEUPLOAD...
echo.
"%PYTHON_PATH%" run.py

echo.
echo 👋 YUEUPLOAD stopped
pause