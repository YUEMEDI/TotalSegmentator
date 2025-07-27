# TotalSegmentator Server Setup Instructions

## 🎯 Overview

This guide sets up a complete TotalSegmentator server with:
- **YueTransfer**: Web interface + SFTP server for file uploads
- **TotalSegmentator**: AI-powered medical image segmentation with GPU acceleration
- **User Management**: Multi-user support with isolated storage
- **GPU Acceleration**: Full CUDA support for fast processing

## 📋 Prerequisites

### Hardware Requirements
- **GPU**: NVIDIA GPU with CUDA support (RTX 3060 or better recommended)
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 100GB+ free space for models and data
- **Network**: Internet connection for initial setup

### Software Requirements
- **Windows 10/11** (64-bit)
- **Miniconda** (Python 3.10.13)
- **NVIDIA GPU Drivers** (latest)
- **CUDA Toolkit 11.8**

## 🚀 Quick Setup

### Step 1: Install Miniconda
1. Download Miniconda from: https://docs.conda.io/en/latest/miniconda.html
2. Install to: `D:\ProgramData\miniconda3`
3. **Important**: Add Miniconda to PATH during installation

### Step 2: Install CUDA Toolkit
1. Download CUDA Toolkit 11.8 from: https://developer.nvidia.com/cuda-11-8-0-download-archive
2. Install with default settings
3. Verify installation: `nvcc --version`

### Step 3: Clone Repository
```cmd
git clone https://github.com/your-repo/TotalSegmentator.git
cd TotalSegmentator
```

### Step 4: Run Setup Scripts
```cmd
cd yuetransfer

REM Setup YueTransfer environment
start_yuetransfer.bat

REM Setup TotalSegmentator environment  
start_totalsegmentator.bat

REM Initialize database
python init_db.py
```

## 🔧 Detailed Setup

### Environment Configuration

#### YueTransfer Environment (Web Server)
- **Python**: 3.10.13
- **Purpose**: Web interface, SFTP server, file management
- **Key Packages**: Flask, Paramiko, SQLAlchemy, Pillow

#### TotalSegmentator Environment (AI Processing)
- **Python**: 3.10.13
- **Purpose**: Medical image segmentation
- **Key Packages**: PyTorch, TensorFlow, TotalSegmentator, nnunetv2
- **GPU**: CUDA 11.8 + cuDNN 8.9.7.29

### Configuration Files

#### `config/config.yaml`
```yaml
server:
  web_port: 5000
  sftp_port: 2222
  
database:
  path: "yuetransfer.db"
  
security:
  secret_key: "your-secret-key"
  
storage:
  base_path: "user_data"
  max_file_size: 1073741824  # 1GB
  
totalsegmentator:
  gpu_device: "gpu"
  fast_mode: true
```

## 🏃‍♂️ Running the Server

### Start YueTransfer Web Server
```cmd
yueserver.bat
```
- **Web Interface**: http://localhost:5000
- **SFTP Server**: localhost:2222
- **Default Admin**: admin / admin123

### Run TotalSegmentator Processing
```cmd
totalsegmentator.bat
```

### Example Commands
```cmd
# Basic segmentation
totalsegmentator -i input.nii.gz -o output -d gpu

# Fast segmentation
totalsegmentator -i input.nii.gz -o output -d gpu -f

# Specific structures
totalsegmentator -i input.nii.gz -o output -d gpu -rs liver kidney spleen
```

## 📁 File Structure

```
yuetransfer/
├── app/                    # Flask application
│   ├── routes/            # Web routes
│   ├── templates/         # HTML templates
│   ├── static/           # CSS/JS files
│   └── utils/            # Utility functions
├── config/               # Configuration files
├── user_data/           # User uploads and results
├── main.py              # Server entry point
├── init_db.py           # Database initialization
├── yueserver.bat        # Start web server
├── totalsegmentator.bat # Start AI processing
└── requirements.txt     # Python dependencies
```

## 🔐 Security Features

### User Management
- **User Registration**: Self-service registration
- **Role-based Access**: Admin and regular users
- **Storage Isolation**: Each user has separate storage space
- **File Permissions**: Users can only access their own files

### SFTP Security
- **SSH Key Authentication**: Supported
- **Password Authentication**: Supported
- **Port Isolation**: Separate from web server
- **User-specific Roots**: Users can only access their directories

## 📊 Monitoring & Logs

### System Monitoring
- **CPU Usage**: Real-time monitoring
- **Memory Usage**: Available RAM tracking
- **GPU Usage**: CUDA memory monitoring
- **Disk Usage**: Storage space tracking

### Log Files
- **Application Logs**: `logs/app.log`
- **Error Logs**: `logs/error.log`
- **Access Logs**: `logs/access.log`

## 🛠️ Troubleshooting

### Common Issues

#### GPU Not Detected
```cmd
# Check CUDA installation
nvcc --version
nvidia-smi

# Test PyTorch GPU
conda run -n totalsegmentator python -c "import torch; print(torch.cuda.is_available())"
```

#### Environment Issues
```cmd
# Recreate environment
conda env remove -n yuetransfer
conda env remove -n totalsegmentator
# Then run setup scripts again
```

#### Port Conflicts
```cmd
# Check port usage
netstat -an | findstr :5000
netstat -an | findstr :2222

# Change ports in config.yaml if needed
```

### Performance Optimization

#### GPU Memory
- Use `-f` flag for fast mode (3mm resolution)
- Use `-ff` flag for fastest mode (6mm resolution)
- Process large images in chunks with `-fs` flag

#### Storage
- Regular cleanup of temporary files
- Monitor disk space usage
- Configure storage quotas in config.yaml

## 🔄 Maintenance

### Regular Tasks
1. **Database Backup**: Backup `yuetransfer.db` regularly
2. **Log Rotation**: Archive old log files
3. **Storage Cleanup**: Remove old temporary files
4. **Security Updates**: Keep dependencies updated

### Updates
```cmd
# Update YueTransfer
conda run -n yuetransfer pip install --upgrade -r requirements.txt

# Update TotalSegmentator
conda run -n totalsegmentator pip install --upgrade totalsegmentator
```

## 📞 Support

### Logs Location
- Application: `logs/app.log`
- Errors: `logs/error.log`
- Access: `logs/access.log`

### Configuration
- Main config: `config/config.yaml`
- Database: `yuetransfer.db`

### Environment Info
```cmd
# YueTransfer environment
conda run -n yuetransfer python -c "import sys; print(sys.version)"

# TotalSegmentator environment
conda run -n totalsegmentator python -c "import torch; print(torch.__version__)"
```

## ✅ Verification Checklist

- [ ] Miniconda installed and in PATH
- [ ] CUDA Toolkit 11.8 installed
- [ ] NVIDIA drivers up to date
- [ ] YueTransfer environment created
- [ ] TotalSegmentator environment created
- [ ] Database initialized
- [ ] Web server starts without errors
- [ ] GPU acceleration working
- [ ] SFTP server accessible
- [ ] File uploads working
- [ ] Segmentation processing working

## 🎉 Success!

Your TotalSegmentator server is now ready for production use!

**Access Points:**
- **Web Interface**: http://localhost:5000
- **SFTP Server**: localhost:2222
- **Admin Login**: admin / admin123

**Next Steps:**
1. Configure your domain/IP for external access
2. Set up SSL certificates for HTTPS
3. Configure firewall rules
4. Set up monitoring and backups
5. Train your users on the interface 