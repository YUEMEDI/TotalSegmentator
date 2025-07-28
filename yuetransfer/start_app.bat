@echo off
echo 🚀 Starting YueTransfer Application...

REM Set Anaconda paths
set CONDA_PATH=D:\anaconda3
set PATH=%CONDA_PATH%;%CONDA_PATH%\Scripts;%CONDA_PATH%\Library\bin;%PATH%

REM Activate conda environment and start app
call %CONDA_PATH%\Scripts\activate.bat yuetransfer && python main.py

pause 