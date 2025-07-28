@echo off
echo 🚀 Starting YueTransfer Server (CSRF Disabled)...

REM Set Anaconda paths
set CONDA_PATH=D:\anaconda3
set PATH=%CONDA_PATH%;%CONDA_PATH%\Scripts;%CONDA_PATH%\Library\bin;%PATH%

REM Activate conda environment and start server
call %CONDA_PATH%\Scripts\activate.bat yuetransfer && python start_server_no_csrf.py

pause 