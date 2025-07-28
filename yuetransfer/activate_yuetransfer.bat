@echo off
echo 🔧 Activating YueTransfer Environment...

REM Set Anaconda paths
set CONDA_PATH=D:\anaconda3
set PATH=%CONDA_PATH%;%CONDA_PATH%\Scripts;%CONDA_PATH%\Library\bin;%PATH%

REM Activate conda environment
call %CONDA_PATH%\Scripts\activate.bat yuetransfer

REM Show current environment
echo.
echo ✅ Environment activated:
echo    Python: %CONDA_DEFAULT_ENV%
echo    Path: %CONDA_PREFIX%
echo.

REM Keep the window open
cmd /k 