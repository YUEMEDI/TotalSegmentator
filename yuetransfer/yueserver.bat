@echo off
echo ========================================
echo YUETRANSFER WEB SERVER STARTUP
echo ========================================

REM Set Miniconda path
set CONDA_PATH=D:\ProgramData\miniconda3\Scripts\conda.exe

REM Add Miniconda to PATH for this session
set PATH=%PATH%;D:\ProgramData\miniconda3;D:\ProgramData\miniconda3\Scripts;D:\ProgramData\miniconda3\Library\bin

echo Checking conda installation...
"%CONDA_PATH%" --version
if errorlevel 1 (
    echo ERROR: Conda not found at %CONDA_PATH%
    echo Please install Miniconda to D:\ProgramData\miniconda3
    pause
    exit /b 1
)

echo.
echo Checking yuetransfer environment...
"%CONDA_PATH%" env list | findstr yuetransfer
if errorlevel 1 (
    echo ERROR: yuetransfer environment not found
    echo Please run the setup first
    pause
    exit /b 1
)

echo.
echo Starting YueTransfer Web Server...
echo.
echo Server will be available at:
echo - Web Interface: http://localhost:5000
echo - SFTP Server: localhost:2222
echo.
echo Press Ctrl+C to stop the server
echo.

REM Activate environment and start server
"%CONDA_PATH%" run -n yuetransfer python main.py

pause 