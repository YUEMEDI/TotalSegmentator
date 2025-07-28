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
    echo ERROR: Failed to create totalsegmentator environment
    pause
    exit /b 1
)

echo.
echo Installing PyTorch with CUDA support...
"%CONDA_PATH%" run -n totalsegmentator pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118
if errorlevel 1 (
    echo ERROR: Failed to install PyTorch
    pause
    exit /b 1
)

echo.
echo Installing TensorFlow...
"%CONDA_PATH%" run -n totalsegmentator pip install tensorflow==2.10.1
if errorlevel 1 (
    echo ERROR: Failed to install TensorFlow
    pause
    exit /b 1
)

echo.
echo Installing cuDNN...
"%CONDA_PATH%" run -n totalsegmentator conda install cudnn=8.9.7.29 -c conda-forge -y
if errorlevel 1 (
    echo ERROR: Failed to install cuDNN
    pause
    exit /b 1
)

echo.
echo Installing TotalSegmentator...
"%CONDA_PATH%" run -n totalsegmentator pip install totalsegmentator
if errorlevel 1 (
    echo ERROR: Failed to install TotalSegmentator
    pause
    exit /b 1
)

echo.
echo Fixing GradScaler import issue...
"%CONDA_PATH%" run -n totalsegmentator python -c "
import os
import sys
nnunetv2_path = os.path.join(sys.prefix, 'lib', 'site-packages', 'nnunetv2', 'training', 'nnUNetTrainer', 'nnUNetTrainer.py')
if os.path.exists(nnunetv2_path):
    with open(nnunetv2_path, 'r') as f:
        content = f.read()
    if 'from torch import GradScaler' in content:
        new_content = content.replace('from torch import GradScaler', 'from torch.cuda.amp import GradScaler')
        with open(nnunetv2_path, 'w') as f:
            f.write(new_content)
        print('Fixed GradScaler import')
    else:
        print('GradScaler import already fixed')
else:
    print('nnunetv2 file not found')
"

echo.
echo Testing GPU availability...
"%CONDA_PATH%" run -n totalsegmentator python -c "import torch; print('PyTorch CUDA:', torch.cuda.is_available()); print('GPU Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

echo.
echo ========================================
echo TOTALSEGMENTATOR SETUP COMPLETE!
echo ========================================
echo.
echo Environment: totalsegmentator
echo Python: 3.10.13
echo PyTorch: 2.1.2+cu118
echo TensorFlow: 2.10.1
echo cuDNN: 8.9.7.29
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