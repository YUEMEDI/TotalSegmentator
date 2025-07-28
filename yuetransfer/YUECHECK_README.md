# YueCheck - System Configuration Checker

## 🎯 Purpose

`yuecheck.py` is a comprehensive system analysis tool that checks your machine configuration **before** running the YueTransfer and TotalSegmentator setup scripts. This prevents installation conflicts and protects your existing development environment.

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
pip install -r yuecheck_requirements.txt
```

### Step 2: Run System Check
```bash
python yuecheck.py
```

### Step 3: Review Report
The script will generate:
- **Console output**: Summary with visual indicators (✅❌⚠️)
- **JSON report**: Detailed system information saved to `yuecheck_report_YYYYMMDD_HHMMSS.json`

## 🔍 What It Checks

### 🖥️ System Information
- Operating System (Windows version, edition, build)
- System architecture and processor details
- Admin privileges status
- System uptime and boot time

### 🔧 Hardware
- **CPU**: Physical/logical cores, frequency, current usage
- **Memory**: Total, available, used RAM (GB)
- **Storage**: Disk space on all drives, free/used space
- **Performance**: Real-time system utilization

### 🐍 Python Environment
- **Current Python**: Version, executable path, installation directory
- **All Python Installations**: Scans PATH and common locations
- **Package Analysis**: Checks for key packages like Flask, PyTorch, TensorFlow, TotalSegmentator
- **Environment Conflicts**: Identifies version mismatches

### 🐨 Conda Analysis
- **Installation Detection**: Miniconda/Anaconda in standard locations
- **Functionality Test**: Verifies conda commands work
- **Environment Listing**: Shows existing conda environments
- **PATH Integration**: Checks if conda is accessible from command line

### 🎮 GPU & CUDA
- **NVIDIA GPU**: Detection via `nvidia-smi`
- **CUDA Toolkit**: Version detection via `nvcc`
- **PyTorch CUDA**: GPU availability and device information
- **Compatibility**: CUDA/PyTorch version matching

### 🌐 Network & Ports
- **Port Availability**: Tests ports 5000 (Flask), 2222 (SFTP), 8080, 3000
- **Network Interfaces**: Lists all network adapters and IP addresses
- **Connectivity**: Basic network stack verification

### 💾 Storage Requirements
- **Space Analysis**: Calculates required vs. available disk space
- **Breakdown**: 
  - YueTransfer environment: ~1GB
  - TotalSegmentator environment: ~15GB
  - User data storage: ~10GB minimum
  - Temporary processing: ~5GB
  - **Total recommended**: 35GB

### 🔐 Permissions
- **File System**: Write permissions in current directory
- **Admin Rights**: Windows administrator status
- **Environment Access**: Conda environment creation rights

## 📊 Report Interpretation

### Status Indicators

#### ✅ **READY TO INSTALL**
- All requirements met
- No conflicts detected
- Safe to proceed with setup

#### ⚠️ **READY WITH RECOMMENDATIONS**
- Installation possible but with caveats
- Review recommendations for optimal performance
- Consider addressing suggestions before setup

#### ❌ **CONFLICTS FOUND** 
- **STOP**: Do not run setup scripts yet
- Resolve all conflicts first
- Re-run yuecheck.py after fixes

### Common Issues & Solutions

#### 🐨 **Conda Not Found**
```
❌ Conda/Miniconda not found or not working
💡 Install Miniconda to D:\ProgramData\miniconda3\ before running setup
```
**Solution**: Download and install Miniconda from [docs.conda.io](https://docs.conda.io/en/latest/miniconda.html)

#### 🐍 **Python Version Issues**
```
❌ Python version too old (< 3.8). TotalSegmentator requires Python 3.8+
💡 Update Python to 3.10.13 or newer
```
**Solution**: Install Python 3.10.13 from [python.org](https://www.python.org/downloads/)

#### 💾 **Insufficient Storage**
```
❌ Insufficient disk space for installation
💡 Free up at least 35GB of disk space
```
**Solution**: Clean up files or move data to external storage

#### 🌐 **Port Conflicts**
```
❌ Ports already in use: 5000, 2222
💡 Stop services using these ports or modify configuration
```
**Solution**: Stop web servers, or modify `config.yaml` to use different ports

#### 🎮 **GPU/CUDA Issues**
```
❌ NVIDIA GPU found but CUDA not installed. GPU acceleration unavailable
💡 Install CUDA toolkit for GPU acceleration
```
**Solution**: Install CUDA Toolkit from [developer.nvidia.com](https://developer.nvidia.com/cuda-toolkit)

## 🛡️ Safety Features

- **Non-Destructive**: Only reads system information, makes no changes
- **Environment Protection**: Identifies existing Python/conda installations
- **Conflict Prevention**: Warns about version mismatches before installation
- **Detailed Logging**: Complete system state saved for troubleshooting

## 📝 Example Output

```
🏥 YUETRANSFER SYSTEM CHECK REPORT
================================================================================

📅 Timestamp: 2024-01-15T14:30:45
🖥️  System: Windows-10-10.0.26100-SP0
🏗️  Architecture: AMD64

💻 HARDWARE
   CPU: 8 cores / 16 threads
   Memory: 32.0GB total, 24.5GB available
   Disk C:\: 256.8GB free / 512.0GB total

🐍 PYTHON
   Current: Python 3.10.13
   Location: D:\ProgramData\miniconda3\python.exe
   Installations found: 3

🐨 CONDA
   Status: ✅ Working (conda 23.7.2)
   Location: D:\ProgramData\miniconda3\Scripts\conda.exe
   Environments: 5 found

🎮 GPU & CUDA
   NVIDIA GPU: ✅ Available
   CUDA: ✅ Available

🌐 NETWORK
   Port 5000: ✅ Available
   Port 2222: ✅ Available

💾 STORAGE
   Drive D:\: 456.2GB available ✅ Sufficient
   Required: 35GB recommended

🎯 OVERALL STATUS: ✅ READY TO INSTALL
```

## 🔧 Advanced Usage

### Custom Requirements Check
Edit `yuecheck.py` to modify storage requirements or add custom checks:

```python
requirements = {
    'yuetransfer_env': 1,  # GB
    'totalsegmentator_env': 15,  # GB
    'user_data': 20,  # GB (increase for more data)
    'temp_processing': 10,  # GB (increase for large files)
    'total_recommended': 50  # GB total
}
```

### Automated Checking
Use in scripts or CI/CD:

```bash
python yuecheck.py
if [ $? -eq 0 ]; then
    echo "System ready, proceeding with setup..."
    call start_yuetransfer.bat
else
    echo "System check failed, aborting setup"
    exit 1
fi
```

---

**Always run `yuecheck.py` before setup to ensure a smooth installation experience!** 🚀 