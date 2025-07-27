# Manual Setup Guide for YueTransfer

If the batch files are having issues, follow these manual steps:

## Step 1: Set up YueTransfer Environment

### Open Command Prompt and run:

```cmd
REM Navigate to yuetransfer folder
cd D:\GitHub\TotalSegmentator\yuetransfer

REM Add Miniconda to PATH
set PATH=%PATH%;D:\ProgramData\miniconda3;D:\ProgramData\miniconda3\Scripts;D:\ProgramData\miniconda3\Library\bin

REM Check conda
conda --version

REM Create environment
conda create -n yuetransfer python=3.10.13 -y

REM Activate environment
conda activate yuetransfer

REM Install packages one by one
pip install flask==2.3.3
pip install flask-login==0.6.3
pip install flask-wtf==1.1.1
pip install werkzeug==2.3.7
pip install paramiko==3.3.1
pip install cryptography==41.0.7
pip install python-magic==0.4.27
pip install pillow==10.0.1
pip install pydicom==2.4.3
pip install nibabel==5.1.0
pip install sqlalchemy==2.0.23
pip install flask-sqlalchemy==3.1.1
pip install psutil==5.9.5
pip install pyyaml==6.0.1
pip install waitress==2.1.2
```

## Step 2: Set up TotalSegmentator Environment

### In a new Command Prompt window:

```cmd
REM Navigate to yuetransfer folder
cd D:\GitHub\TotalSegmentator\yuetransfer

REM Add Miniconda to PATH
set PATH=%PATH%;D:\ProgramData\miniconda3;D:\ProgramData\miniconda3\Scripts;D:\ProgramData\miniconda3\Library\bin

REM Create environment
conda create -n totalsegmentator python=3.10.13 -y

REM Activate environment
conda activate totalsegmentator

REM Install TensorFlow 2.10.1 (last with Windows GPU support)
pip install tensorflow==2.10.1

REM Install PyTorch 2.1.2 with CUDA 11.8
pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118

REM Install scientific packages
pip install numpy==1.23.5
pip install scipy==1.10.1
pip install scikit-learn==1.2.2
pip install pandas==1.5.3
pip install matplotlib==3.7.2
pip install seaborn==0.12.2

REM Install medical imaging packages
pip install simpleitk==2.2.1
pip install pydicom==2.4.3
pip install nibabel==5.1.0

REM Install TotalSegmentator
pip install totalsegmentator
```

## Step 3: Test the Setup

### Test YueTransfer:
```cmd
conda activate yuetransfer
python -c "import flask, paramiko, pydicom; print('YueTransfer: OK')"
```

### Test TotalSegmentator:
```cmd
conda activate totalsegmentator
python -c "import tensorflow as tf; print(f'TF: {tf.__version__}'); print(f'GPU: {len(tf.config.list_physical_devices(\"GPU\")) > 0}')"
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"
```

## Step 4: Start YueTransfer

```cmd
conda activate yuetransfer
python main.py
```

## Troubleshooting

### If conda command not found:
- Make sure Miniconda is installed in `D:\ProgramData\miniconda3`
- Try using full path: `D:\ProgramData\miniconda3\Scripts\conda.exe`

### If packages fail to install:
- Try installing one by one to identify the problematic package
- Check your internet connection
- Try using a different pip mirror: `pip install package --index-url https://pypi.org/simple/`

### If GPU not detected:
- Make sure CUDA drivers are installed
- Check if TensorFlow 2.10.1 is compatible with your CUDA version
- Try running: `nvidia-smi` to check GPU status 