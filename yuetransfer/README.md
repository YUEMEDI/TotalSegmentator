# YueTransfer - TotalSegmentator Web Server

A complete web-based solution for medical image segmentation using TotalSegmentator with GPU acceleration.

## 🚀 Quick Start

### Prerequisites
- **Windows 10/11** with NVIDIA GPU
- **Miniconda** installed to `D:\ProgramData\miniconda3`
- **CUDA Toolkit 11.8**

### Setup (3 Steps)

1. **Setup YueTransfer Environment**
   ```cmd
   start_yuetransfer.bat
   ```

2. **Setup TotalSegmentator Environment**
   ```cmd
   start_totalsegmentator.bat
   ```

3. **Initialize Database**
   ```cmd
   python init_db.py
   ```

### Run the Server

**Start Web Server:**
```cmd
yueserver.bat
```
- Web Interface: http://localhost:5000
- SFTP Server: localhost:2222
- Default Admin: admin / admin123

**Run AI Processing:**
```cmd
totalsegmentator.bat
```

## 📋 Features

### YueTransfer (Web Interface)
- **Multi-user Support**: User registration and management
- **File Upload**: Drag & drop interface for DICOM/NIfTI files
- **SFTP Server**: Large file transfers via SFTP
- **Storage Isolation**: Each user has separate storage space
- **Admin Panel**: System monitoring and user management
- **Real-time Processing**: Queue management for segmentation jobs

### TotalSegmentator (AI Processing)
- **GPU Acceleration**: Full CUDA support for fast processing
- **104 Anatomical Structures**: Complete body segmentation
- **Multiple Input Formats**: DICOM, NIfTI, ZIP archives
- **Flexible Processing**: Fast mode, specific ROI selection
- **Quality Output**: High-resolution segmentation masks

## 🔧 Technical Stack

### YueTransfer Environment
- **Python**: 3.10.13
- **Web Framework**: Flask
- **Database**: SQLite with SQLAlchemy
- **File Transfer**: Paramiko (SFTP)
- **UI**: Bootstrap + JavaScript

### TotalSegmentator Environment
- **Python**: 3.10.13
- **Deep Learning**: PyTorch 2.1.2 + TensorFlow 2.10.1
- **GPU**: CUDA 11.8 + cuDNN 8.9.7.29
- **Medical Imaging**: TotalSegmentator 2.10.0
- **Neural Networks**: nnU-Net v2

## 📁 File Structure

```
yuetransfer/
├── app/                    # Flask application
│   ├── routes/            # Web routes (auth, main, admin, api)
│   ├── templates/         # HTML templates
│   ├── static/           # CSS/JS files
│   ├── models/           # Database models
│   └── utils/            # Utility functions
├── config/               # Configuration files
├── user_data/           # User uploads and results
├── main.py              # Server entry point
├── init_db.py           # Database initialization
├── requirements.txt     # Python dependencies
├── yueserver.bat        # Start web server
├── totalsegmentator.bat # Start AI processing
├── start_yuetransfer.bat    # Setup YueTransfer environment
├── start_totalsegmentator.bat # Setup TotalSegmentator environment
└── SETUP_INSTRUCTIONS.md # Detailed setup guide
```

## 🔐 Security

### User Management
- **Self-registration**: Users can create accounts
- **Role-based Access**: Admin and regular users
- **Storage Isolation**: Users can only access their own files
- **Session Management**: Secure login/logout

### SFTP Security
- **SSH Key Authentication**: Supported
- **Password Authentication**: Supported
- **Port Isolation**: Separate from web server
- **User-specific Roots**: Users restricted to their directories

## 📊 Monitoring

### System Metrics
- **CPU Usage**: Real-time monitoring
- **Memory Usage**: Available RAM tracking
- **GPU Usage**: CUDA memory monitoring
- **Disk Usage**: Storage space tracking

### Logs
- **Application Logs**: `logs/app.log`
- **Error Logs**: `logs/error.log`
- **Access Logs**: `logs/access.log`

## 🛠️ Configuration

### Main Configuration (`config/config.yaml`)
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

## 📖 Usage Examples

### Web Interface
1. **Register/Login**: Create account or login as admin
2. **Upload Files**: Drag & drop DICOM/NIfTI files
3. **Process Images**: Select files and start segmentation
4. **Download Results**: Get segmentation masks and statistics

### SFTP Access
```bash
# Connect to SFTP server
sftp -P 2222 username@localhost

# Upload large files
put large_dicom_archive.zip

# Download results
get segmentation_results/
```

### Command Line Processing
```cmd
# Basic segmentation
totalsegmentator -i input.nii.gz -o output -d gpu

# Fast segmentation
totalsegmentator -i input.nii.gz -o output -d gpu -f

# Specific structures
totalsegmentator -i input.nii.gz -o output -d gpu -rs liver kidney spleen
```

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

## 🚨 Troubleshooting

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
# Recreate environments
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

## 📞 Support

### Documentation
- **Setup Guide**: `SETUP_INSTRUCTIONS.md`
- **Manual Setup**: `MANUAL_SETUP.md`
- **TotalSegmentator Setup**: `MANUAL_TOTALSEGMENTATOR_SETUP.md`

### Logs Location
- **Application**: `logs/app.log`
- **Errors**: `logs/error.log`
- **Access**: `logs/access.log`

### Environment Info
```cmd
# YueTransfer environment
conda run -n yuetransfer python -c "import sys; print(sys.version)"

# TotalSegmentator environment
conda run -n totalsegmentator python -c "import torch; print(torch.__version__)"
```

## 🎉 Success!

Your TotalSegmentator server is ready for production use!

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