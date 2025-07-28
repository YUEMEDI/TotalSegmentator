# YueTransfer - Medical Imaging Transfer & Processing Platform

A comprehensive standalone SFTP + Web interface application for handling large medical imaging files with TotalSegmentator integration.

## 🎯 Features

### **File Transfer & Management**
- **SFTP Server**: Secure file transfer for large DICOM datasets (bypasses browser limitations)
- **Web Interface**: Modern, responsive UI for file management
- **Multi-User Support**: Each user has isolated storage space with quotas
- **File Browser**: Intuitive navigation with search, filtering, and bulk operations
- **Drag & Drop Upload**: Easy file upload through web interface

### **TotalSegmentator Integration**
- **Background Processing**: Asynchronous segmentation jobs
- **Multiple Tasks**: Support for various TotalSegmentator tasks (total, lung_vessels, etc.)
- **Job Management**: Track progress, view results, cancel jobs
- **Batch Processing**: Process multiple files simultaneously

### **User Management**
- **Role-Based Access**: Users and administrators with different permissions
- **Storage Quotas**: Configurable storage limits per user
- **User Isolation**: Complete file separation between users
- **Admin Panel**: Comprehensive user and system management

### **Professional Features**
- **Security**: CSRF protection, secure sessions, user isolation
- **Monitoring**: System health, storage usage, job tracking
- **Logging**: Comprehensive audit trail
- **Error Handling**: Graceful error pages and API responses

## 🏗️ Architecture

```
yuetransfer/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── config/                # Configuration files
├── app/                   # Main application
│   ├── __init__.py        # Flask app factory
│   ├── config.py          # Configuration management
│   ├── sftp_server.py     # SFTP server implementation
│   ├── models/            # Database models
│   │   └── user.py        # User and job models
│   ├── routes/            # Web routes
│   │   ├── auth.py        # Authentication routes
│   │   ├── main.py        # Main application routes
│   │   ├── admin.py       # Admin panel routes
│   │   └── api.py         # API endpoints
│   ├── templates/         # HTML templates
│   │   ├── base.html      # Base template
│   │   ├── auth/          # Authentication templates
│   │   ├── main/          # Main application templates
│   │   └── admin/         # Admin panel templates
│   ├── static/            # CSS, JS, images
│   │   ├── css/style.css  # Custom styles
│   │   └── js/app.js      # JavaScript functionality
│   └── utils/             # Utility modules
│       ├── auth.py        # Authentication utilities
│       ├── file_manager.py # File management
│       ├── totalsegmentator_integration.py # TotalSegmentator
│       ├── logger.py      # Logging utilities
│       ├── error_handlers.py # Error handling
│       └── context_processors.py # Template context
├── uploads/               # User file storage
├── results/              # Processing results
└── logs/                 # Application logs
```

## 🚀 Installation

### **Prerequisites**
- Python 3.9+ 
- pip package manager
- TotalSegmentator (optional, for processing functionality)

### **1. Clone/Create Directory**
```bash
mkdir yuetransfer
cd yuetransfer
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Install TotalSegmentator (Optional)**
```bash
pip install TotalSegmentator
```

### **4. Initialize Application**
```bash
python main.py
```

The application will:
- Create necessary directories
- Initialize the database
- Create default admin user (username: `admin`, password: `yuetransfer123`)
- Start both SFTP and Web servers

## 🔧 Configuration

### **Default Settings**
- **Web Interface**: http://localhost:8080
- **SFTP Server**: localhost:2222
- **Admin User**: admin / yuetransfer123 (⚠️ Change immediately!)

### **Custom Configuration**
Create `config/config.yaml`:
```yaml
# Server Settings
WEB_HOST: "0.0.0.0"
WEB_PORT: 8080
SFTP_HOST: "0.0.0.0"
SFTP_PORT: 2222

# Storage Settings
UPLOAD_FOLDER: "./app/uploads"
RESULTS_FOLDER: "./app/results"
MAX_CONTENT_LENGTH: 17179869184  # 16GB

# Security Settings
SECRET_KEY: "your-secret-key-here"
SESSION_TIMEOUT: 3600

# Database
SQLALCHEMY_DATABASE_URI: "sqlite:///yuetransfer.db"

# Logging
LOG_LEVEL: "INFO"
LOG_FILE: "./app/logs/yuetransfer.log"
```

## 📖 Usage

### **Web Interface**

1. **Login**: Navigate to http://localhost:8080
2. **Dashboard**: View statistics and recent activity
3. **Files**: Browse, upload, and manage files
4. **Process**: Send files to TotalSegmentator
5. **Results**: View and download processing results

### **SFTP Transfer (Recommended for Large Files)**

**Command Line:**
```bash
sftp -P 2222 username@localhost
```

**Popular SFTP Clients:**
- **Windows**: WinSCP, FileZilla
- **Mac**: Cyberduck, FileZilla
- **Linux**: FileZilla, command line

### **Admin Functions**

1. **User Management**: Create, edit, delete users
2. **Storage Monitoring**: View usage and quotas
3. **Job Management**: Monitor processing jobs
4. **System Status**: Check health and performance

## 🔐 Security

### **Authentication**
- Username/password authentication
- Session management with timeout
- CSRF protection on forms

### **User Isolation**
- Separate storage directories per user
- Path validation to prevent directory traversal
- File access restricted to user's own files

### **SFTP Security**
- SSH-based file transfer
- User-specific home directories
- No shell access (SFTP only)

## 📊 TotalSegmentator Integration

### **Supported Tasks**
- `total`: Complete segmentation (117 classes)
- `total_mr`: MR image segmentation
- `lung_vessels`: Lung vessel segmentation
- `cerebral_bleed`: Cerebral bleeding detection
- `hip_implant`: Hip implant detection
- And more...

### **Processing Workflow**
1. Upload DICOM or NIfTI files via SFTP or web
2. Select files for processing
3. Choose segmentation task and options
4. Submit job for background processing
5. Monitor progress and view results

### **Job Management**
- Real-time progress tracking
- Job cancellation
- Result download
- Processing history

## 🔍 File Management

### **Supported Formats**
- **Medical**: DICOM (.dcm), NIfTI (.nii, .nii.gz)
- **Archives**: ZIP, TAR, 7Z
- **Images**: JPEG, PNG, TIFF, BMP
- **Documents**: PDF, TXT, CSV

### **File Operations**
- Upload (web + SFTP)
- Download
- Delete
- Rename
- Move
- Create folders
- Bulk operations

### **Storage Features**
- User quotas
- Usage tracking
- File type organization
- Search and filtering

## 🛠️ Development

### **Running in Development Mode**
```bash
python main.py --dev
```

### **Key Components**
- **Flask**: Web framework
- **Paramiko**: SFTP server implementation
- **SQLAlchemy**: Database ORM
- **Bootstrap**: UI framework
- **Threading**: Background job processing

### **Database Models**
- **User**: Authentication and storage management
- **ProcessingJob**: TotalSegmentator job tracking

## 📝 Command Line Options

```bash
python main.py [OPTIONS]

Options:
  --dev                 Run in development mode
  --production         Run in production mode  
  --port PORT          Web server port (default: 8080)
  --sftp-port PORT     SFTP server port (default: 2222)
  --host HOST          Host to bind to (default: 0.0.0.0)
  --config CONFIG      Configuration file path
```

## 🚨 Important Notes

### **First Login**
1. Access http://localhost:8080
2. Login with `admin` / `yuetransfer123`
3. **Immediately change the password**
4. Create additional users as needed

### **Large File Handling**
- Use SFTP for files > 1GB
- Web upload suitable for smaller files
- Browser limitations: ~2-4GB depending on browser/system

### **TotalSegmentator Requirements**
- GPU recommended for fast processing
- CUDA support for GPU acceleration
- Sufficient disk space for results

### **Production Deployment**
- Change default admin password
- Use HTTPS (configure reverse proxy)
- Set up proper firewall rules
- Configure backup procedures
- Monitor disk space and performance

## 🔧 Troubleshooting

### **Common Issues**

**SFTP Connection Failed:**
```bash
# Check if server is running
netstat -an | grep 2222

# Test connection
sftp -P 2222 admin@localhost
```

**TotalSegmentator Not Found:**
```bash
# Install TotalSegmentator
pip install TotalSegmentator

# Verify installation
TotalSegmentator --help
```

**Permission Errors:**
- Ensure write permissions on upload/results directories
- Check user isolation settings
- Verify file ownership

**Database Issues:**
```bash
# Reset database (⚠️ Deletes all data)
rm yuetransfer.db
python main.py  # Will recreate database
```

## 📞 Support

### **Getting Help**
- Check logs in `app/logs/yuetransfer.log`
- Review configuration settings
- Verify TotalSegmentator installation
- Check system resources (disk space, memory)

### **Contact**
- **Default Admin Email**: admin@yuetransfer.local
- **Documentation**: This README file
- **Issues**: Check application logs for details

## 🎉 Success!

You now have a complete medical imaging transfer and processing platform! The application provides:

✅ **Secure SFTP server** for large file transfers  
✅ **Modern web interface** for file management  
✅ **TotalSegmentator integration** for medical image processing  
✅ **Multi-user support** with storage quotas  
✅ **Admin panel** for system management  
✅ **Professional-grade security** and isolation  

**Ready to handle gigabyte-sized medical imaging datasets with ease!** 🏥🧠

---

**YueTransfer** - Professional medical imaging transfer and processing platform. 