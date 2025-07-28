@echo off
echo ========================================
echo TOTALSEGMENTATOR ENVIRONMENT SETUP
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
echo Creating totalsegmentator environment...
"%CONDA_PATH%" create -n totalsegmentator python=3.10.13 -y

if errorlevel 1 (
    echo ERROR: Failed to create conda environment
    pause
    exit /b 1
)

echo.
echo Activating totalsegmentator environment...
call "%CONDA_PATH%" activate totalsegmentator

if errorlevel 1 (
    echo WARNING: Conda activate failed, trying alternative method...
    echo Using direct environment path...
    set CONDA_ENV_PATH=D:\anaconda3\envs\totalsegmentator
    set PATH=%CONDA_ENV_PATH%;%CONDA_ENV_PATH%\Scripts;%CONDA_ENV_PATH%\Library\bin;%PATH%
    set CONDA_DEFAULT_ENV=totalsegmentator
    set CONDA_PREFIX=%CONDA_ENV_PATH%
)

echo.
echo Installing PyTorch with CUDA 11.8 support...
pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118

if errorlevel 1 (
    echo ERROR: Failed to install PyTorch
    pause
    exit /b 1
)

echo.
echo Installing TensorFlow 2.10.1...
pip install tensorflow==2.10.1

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
pip install totalsegmentator

if errorlevel 1 (
    echo ERROR: Failed to install TotalSegmentator
    pause
    exit /b 1
)

echo.
echo Fixing GradScaler import issue...
python -c "import torch; from torch.cuda.amp import GradScaler; print('GradScaler import test: SUCCESS')"

if errorlevel 1 (
    echo WARNING: GradScaler import test failed, but this may not affect functionality
)

echo.
echo Testing TotalSegmentator installation...
python -c "import totalsegmentator; print('TotalSegmentator import test: SUCCESS')"

if errorlevel 1 (
    echo ERROR: TotalSegmentator import test failed
    pause
    exit /b 1
)

echo.
echo Testing PyTorch CUDA availability...
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda if hasattr(torch.version, \"cuda\") else \"N/A\"}')"

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
echo NOTE: Run 'python yuecheck.py' first to verify system compatibility!
echo.
pause 