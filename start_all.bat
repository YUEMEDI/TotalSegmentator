@echo off
echo ========================================
echo Starting TotalSegmentator System
echo ========================================
echo.

echo [1/2] Starting YUETransfer Server...
echo.
cd /d "%~dp0yuetransfer"
start "YUETransfer Server" cmd /c "start_server_auto.bat"
timeout /t 3 /nobreak >nul

echo.
echo [2/2] Starting YUEUPLOAD Server...
echo.
cd /d "%~dp0yueupload"
start "YUEUPLOAD Server" cmd /c "start_yueupload.bat"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Both servers are starting...
echo ========================================
echo.
echo YUETransfer: http://localhost:5000
echo YUEUPLOAD:   http://localhost:5001/upload
echo.
echo Servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
echo Press any key to close this window...
pause >nul