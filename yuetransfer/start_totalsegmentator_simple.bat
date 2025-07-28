@echo off
echo ========================================
echo TOTALSEGMENTATOR ENVIRONMENT SETUP
echo ========================================

REM Set paths
set CONDA_PATH=D:\anaconda3\Scripts\conda.exe
set PYTHON_PATH=C:\Users\ZERO\.conda\envs\totalsegmentator\python.exe
set PIP_PATH=C:\Users\ZERO\.conda\envs\totalsegmentator\Scripts\pip.exe

echo Checking conda installation...
"%CONDA_PATH%" --version

if errorlevel 1 (
    echo ERROR: Conda not found at %CONDA_PATH%
    pause
    exit /b 1
)

echo.
echo Checking if totalsegmentator environment exists...
"%CONDA_PATH%" env list | findstr totalsegmentator

if errorlevel 1 (
    echo Creating totalsegmentator environment...
    "%CONDA_PATH%" create -n totalsegmentator python=3.10.13 -y
    
    if errorlevel 1 (
        echo ERROR: Failed to create conda environment
        pause
        exit /b 1
    )
) else (
    echo Environment totalsegmentator already exists.
)

echo.
echo Installing PyTorch with CUDA 11.8 support...
"%PIP_PATH%" install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118

if errorlevel 1 (
    echo ERROR: Failed to install PyTorch
    pause
    exit /b 1
)

echo.
echo Installing TensorFlow 2.10.1...
"%PIP_PATH%" install tensorflow==2.10.1

if errorlevel 1 (
    echo ERROR: Failed to install TensorFlow
    pause
    exit /b 1
)

echo.
echo Installing CUDA dependencies...
"%CONDA_PATH%" install -n totalsegmentator -c conda-forge cudnn=8.9.7.29 -y

if errorlevel 1 (
    echo ERROR: Failed to install CUDA dependencies
    pause
    exit /b 1
)

echo.
echo Installing TotalSegmentator...
"%PIP_PATH%" install totalsegmentator

if errorlevel 1 (
    echo ERROR: Failed to install TotalSegmentator
    pause
    exit /b 1
)

echo.
echo Testing installations...
"%PYTHON_PATH%" -c "import torch; print(f'PyTorch: {torch.__version__}')"
"%PYTHON_PATH%" -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}')"
"%PYTHON_PATH%" -c "import totalsegmentator; print('TotalSegmentator: OK')"

echo.
echo ========================================
echo TOTALSEGMENTATOR SETUP COMPLETE!
echo ========================================
echo.
echo Environment: totalsegmentator
echo Python: 3.10.13
echo PyTorch: 2.1.2 with CUDA 11.8
echo TensorFlow: 2.10.1
echo TotalSegmentator: 2.10.0
echo.
echo Next steps:
echo 1. Run python init_db.py
echo 2. Run yueserver.bat to start the server
echo 3. Run totalsegmentator.bat for AI processing
echo.
pause 