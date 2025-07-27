# Manual TotalSegmentator Setup Guide

If the batch files are having issues, follow these manual steps:

## Step 1: Check and Fix Environment

### Open Command Prompt and run:

```cmd
REM Navigate to yuetransfer folder
cd D:\GitHub\TotalSegmentator\yuetransfer

REM Use full path to conda
set CONDA_PATH=D:\ProgramData\miniconda3\Scripts\conda.exe

REM List all environments
"%CONDA_PATH%" env list

REM Remove totalsegmentator environment if it exists
"%CONDA_PATH%" env remove -n totalsegmentator -y

REM Create fresh environment
"%CONDA_PATH%" create -n totalsegmentator python=3.10.13 -y
```

## Step 2: Install TensorFlow 2.10.1

```cmd
REM Install TensorFlow 2.10.1 (last with Windows GPU support)
"%CONDA_PATH%" run -n totalsegmentator pip install tensorflow==2.10.1
```

## Step 3: Install PyTorch 2.1.2

```cmd
REM Install PyTorch 2.1.2 with CUDA 11.8
"%CONDA_PATH%" run -n totalsegmentator pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118
```

## Step 4: Install Scientific Packages

```cmd
REM Install scientific computing packages
"%CONDA_PATH%" run -n totalsegmentator pip install numpy==1.23.5
"%CONDA_PATH%" run -n totalsegmentator pip install scipy==1.10.1
"%CONDA_PATH%" run -n totalsegmentator pip install scikit-learn==1.2.2
"%CONDA_PATH%" run -n totalsegmentator pip install pandas==1.5.3
"%CONDA_PATH%" run -n totalsegmentator pip install matplotlib==3.7.2
"%CONDA_PATH%" run -n totalsegmentator pip install seaborn==0.12.2
```

## Step 5: Install Medical Imaging Packages

```cmd
REM Install medical imaging packages
"%CONDA_PATH%" run -n totalsegmentator pip install simpleitk==2.2.1
"%CONDA_PATH%" run -n totalsegmentator pip install pydicom==2.4.3
"%CONDA_PATH%" run -n totalsegmentator pip install nibabel==5.0.1
```

## Step 6: Install TotalSegmentator

```cmd
REM Install TotalSegmentator
"%CONDA_PATH%" run -n totalsegmentator pip install totalsegmentator
```

## Step 7: Test Installation

### Test TensorFlow GPU:
```cmd
"%CONDA_PATH%" run -n totalsegmentator python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}'); print(f'GPU Available: {len(tf.config.list_physical_devices(\"GPU\")) > 0}')"
```

### Test PyTorch GPU:
```cmd
"%CONDA_PATH%" run -n totalsegmentator python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}')"
```

### Test TotalSegmentator:
```cmd
"%CONDA_PATH%" run -n totalsegmentator python -c "import totalsegmentator; print('TotalSegmentator: OK')"
```

## Troubleshooting

### If environment creation fails:
- Check if conda is working: `"%CONDA_PATH%" --version`
- Try creating environment with different name: `"%CONDA_PATH%" create -n totalseg python=3.10.13 -y`

### If TensorFlow installation fails:
- Try installing without GPU: `"%CONDA_PATH%" run -n totalsegmentator pip install tensorflow-cpu==2.10.1`

### If PyTorch installation fails:
- Try CPU-only version: `"%CONDA_PATH%" run -n totalsegmentator pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cpu`

### If TotalSegmentator installation fails:
- Check dependencies: `"%CONDA_PATH%" run -n totalsegmentator pip list`
- Try installing from source: `"%CONDA_PATH%" run -n totalsegmentator pip install git+https://github.com/wasserth/TotalSegmentator.git` 