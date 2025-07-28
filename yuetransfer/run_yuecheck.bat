@echo off
echo ========================================
echo YUETRANSFER SYSTEM CHECK
echo ========================================

echo Installing yuecheck dependencies...
pip install -r yuecheck_requirements.txt --quiet

if errorlevel 1 (
    echo ERROR: Failed to install yuecheck dependencies
    echo Please ensure Python and pip are working
    pause
    exit /b 1
)

echo.
echo Running comprehensive system check...
echo.

python yuecheck.py

echo.
echo Check complete! Review the report above.
echo If conflicts were found, resolve them before running setup.
echo.
pause 