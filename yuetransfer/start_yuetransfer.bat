@echo off
echo ========================================
echo YUETRANSFER ENVIRONMENT SETUP
echo ========================================

REM Set Anaconda path
set CONDA_PATH=D:\anaconda3\Scripts\conda.exe

REM Add Anaconda to PATH for this session
set PATH=%PATH%;D:\anaconda3;D:\anaconda3\Scripts;D:\anaconda3\Library\bin

echo Checking conda installation...
"%CONDA_PATH%" --version
if errorlevel 1 (
    echo ERROR: Conda not found at %CONDA_PATH%
    echo Please verify Anaconda installation at D:\anaconda3
    pause
    exit /b 1
)

echo.
echo Creating yuetransfer environment...
"%CONDA_PATH%" create -n yuetransfer python=3.10.13 -y
if errorlevel 1 (
    echo ERROR: Failed to create yuetransfer environment
    pause
    exit /b 1
)

echo.
echo Installing YueTransfer dependencies...
"%CONDA_PATH%" run -n yuetransfer pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo YUETRANSFER SETUP COMPLETE!
echo ========================================
echo.
echo Environment: yuetransfer
echo Python: 3.10.13
echo Packages: Flask, Paramiko, SQLAlchemy, Pillow
echo.
echo Next steps:
echo 1. Run start_totalsegmentator.bat
echo 2. Run python init_db.py
echo 3. Run yueserver.bat to start the server
echo.
echo NOTE: Run 'python yuecheck.py' first to verify system compatibility!
echo.
pause 