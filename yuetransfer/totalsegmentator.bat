@echo off
echo ========================================
echo TOTALSEGMENTATOR GPU PROCESSING
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
echo Checking totalsegmentator environment...
"%CONDA_PATH%" env list | findstr totalsegmentator
if errorlevel 1 (
    echo ERROR: totalsegmentator environment not found
    echo Please run the setup first
    pause
    exit /b 1
)

echo.
echo Testing GPU availability...
"%CONDA_PATH%" run -n totalsegmentator python -c "import torch; print('PyTorch CUDA:', torch.cuda.is_available()); print('GPU Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
if errorlevel 1 (
    echo ERROR: GPU test failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo TOTALSEGMENTATOR COMMAND LINE
echo ========================================
echo.
echo Usage examples:
echo.
echo 1. Basic segmentation (GPU):
echo    totalsegmentator -i input.nii.gz -o output_folder -d gpu
echo.
echo 2. Fast segmentation (GPU):
echo    totalsegmentator -i input.nii.gz -o output_folder -d gpu -f
echo.
echo 3. Specific anatomical structures:
echo    totalsegmentator -i input.nii.gz -o output_folder -d gpu -rs liver kidney spleen
echo.
echo 4. With preview:
echo    totalsegmentator -i input.nii.gz -o output_folder -d gpu -p
echo.
echo Available options:
echo -i: Input file (NIfTI, DICOM folder, or ZIP)
echo -o: Output directory
echo -d: Device (gpu, cpu, mps)
echo -f: Fast mode (3mm resolution)
echo -ff: Fastest mode (6mm resolution)
echo -p: Generate preview PNG
echo -rs: ROI subset (specific structures)
echo -v: Verbose output
echo.
echo Type 'totalsegmentator --help' for full options
echo.

REM Start interactive mode
echo Starting TotalSegmentator in interactive mode...
echo Type 'exit' to quit
echo.
"%CONDA_PATH%" run -n totalsegmentator cmd /k

pause 