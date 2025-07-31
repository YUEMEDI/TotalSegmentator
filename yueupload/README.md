# 🚀 YUEUPLOAD - Advanced DICOM Upload System

## 📋 System Overview

**YUEUPLOAD** is a standalone, modular DICOM upload system that communicates with:
- **YUETransfer** - User authentication and file management
- **TotalSegmentator** - Medical image segmentation processing
- **user_files** - File storage and organization

## 🏗️ Architecture

```
TotalSegmentator/
├── yueupload/                     # ← This system (lowercase)
│   ├── app/                      # Main application
│   ├── config/                   # Configuration files
│   ├── templates/                # HTML templates
│   ├── static/                   # CSS, JS, images
│   ├── uploads/                  # Temporary upload storage
│   ├── logs/                     # System logs
│   └── tests/                    # Test files
├── yuetransfer/                  # YUETransfer system
├── totalsegmentator/             # TotalSegmentator system
└── user_files/                   # User file storage
```

## 🔗 Communication Interfaces

### **1. YUETransfer Communication**
- **Authentication**: Use YUETransfer's user system
- **File Browser**: Integrate with existing file browser
- **User Management**: Share user sessions and permissions
- **Navigation**: Seamless integration in YUETransfer interface

### **2. TotalSegmentator Communication**
- **API Endpoints**: Send files for segmentation
- **Job Management**: Track segmentation progress
- **Results Handling**: Receive and organize segmentation results
- **Configuration**: Share TotalSegmentator settings

### **3. user_files Communication**
- **Storage Integration**: Direct access to user folders
- **File Organization**: Use existing folder structure
- **Metadata Management**: Store DICOM metadata
- **Backup Integration**: Work with existing backup systems

## 📁 Folder Structure

```
yueupload/
├── app/
│   ├── __init__.py              # Flask app initialization
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── upload.py            # Upload routes
│   │   ├── preview.py           # DICOM preview routes
│   │   ├── metadata.py          # Metadata routes
│   │   └── integration.py       # Integration routes
│   ├── models/
│   │   ├── __init__.py
│   │   ├── upload.py            # Upload models
│   │   └── dicom.py             # DICOM models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── upload_service.py    # Upload processing
│   │   ├── dicom_service.py     # DICOM processing
│   │   ├── preview_service.py   # Preview generation
│   │   └── integration_service.py # System integration
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py        # File operations
│       ├── dicom_utils.py       # DICOM utilities
│       └── security.py          # Security utilities
├── config/
│   ├── __init__.py
│   ├── settings.py              # Main settings
│   ├── yuetransfer.py           # YUETransfer config
│   ├── totalsegmentator.py      # TotalSegmentator config
│   └── user_files.py            # user_files config
├── templates/
│   ├── base.html                # Base template
│   ├── upload/
│   │   ├── index.html           # Main upload interface
│   │   ├── progress.html        # Upload progress
│   │   ├── preview.html         # DICOM preview
│   │   └── metadata.html        # Metadata display
│   └── components/
│       ├── upload_form.html     # Upload form component
│       ├── progress_bar.html    # Progress bar component
│       └── preview_card.html    # Preview card component
├── static/
│   ├── css/
│   │   ├── main.css             # Main styles
│   │   ├── upload.css           # Upload styles
│   │   └── preview.css          # Preview styles
│   ├── js/
│   │   ├── upload.js            # Upload functionality
│   │   ├── dragdrop.js          # Drag and drop
│   │   ├── preview.js           # Preview handling
│   │   └── progress.js          # Progress tracking
│   └── img/
│       ├── icons/               # System icons
│       └── previews/            # Generated previews
├── uploads/
│   ├── temp/                    # Temporary uploads
│   ├── processing/              # Files being processed
│   └── completed/               # Completed uploads
├── logs/
│   ├── upload.log               # Upload logs
│   ├── error.log                # Error logs
│   └── access.log               # Access logs
├── tests/
│   ├── test_upload.py           # Upload tests
│   ├── test_dicom.py            # DICOM tests
│   └── test_integration.py      # Integration tests
├── requirements.txt             # Python dependencies
├── config.py                    # Main configuration
├── run.py                       # Application entry point
├── start_yueupload.bat          # Windows startup script
├── start_yueupload.sh           # Unix/Linux/Mac startup script
└── README.md                    # This file
```

## 🔧 Configuration

### **YUETransfer Integration**
```python
# config/yuetransfer.py
YUETRANSFER_URL = "http://localhost:5000"
YUETRANSFER_AUTH_ENDPOINT = "/api/auth"
YUETRANSFER_FILE_ENDPOINT = "/api/files"
```

### **TotalSegmentator Integration**
```python
# config/totalsegmentator.py
TOTALSEGMENTATOR_URL = "http://localhost:8000"
TOTALSEGMENTATOR_API_KEY = "your_api_key"
TOTALSEGMENTATOR_ENDPOINTS = {
    "upload": "/api/upload",
    "process": "/api/process",
    "status": "/api/status",
    "download": "/api/download"
}
```

### **user_files Integration**
```python
# config/user_files.py
USER_FILES_ROOT = "../user_files"
USER_FILES_STRUCTURE = {
    "uploads": "uploads",
    "projects": "projects",
    "patients": "patients",
    "studies": "studies",
    "previews": "previews",
    "metadata": "metadata"
}
```

## 🚀 Quick Start

### **⚠️ Important: Python Environment Compatibility**

YUEUPLOAD is configured to use **Python 3.10.13** for compatibility with YUETransfer and TotalSegmentator systems.

### **1. Installation (Recommended Method)**

#### **Windows:**
```bash
# Use the provided batch file (recommended)
start_yueupload.bat

# Or manually use the correct Python environment
C:\Users\ZERO\.conda\envs\totalsegmentator\python.exe run.py
```

#### **Unix/Linux/Mac:**
```bash
# Use the provided shell script (recommended)
chmod +x start_yueupload.sh
./start_yueupload.sh

# Or manually activate the conda environment
conda activate totalsegmentator
python run.py
```

### **2. Manual Installation (Alternative)**
```bash
cd yueupload

# Install dependencies in the correct environment
C:\Users\ZERO\.conda\envs\totalsegmentator\python.exe -m pip install -r requirements.txt

# Run the application
C:\Users\ZERO\.conda\envs\totalsegmentator\python.exe run.py
```

### **3. Access the Interface**
- **Web Interface**: http://localhost:5001
- **API Documentation**: http://localhost:5001/api/docs

## 📊 Features

### **Sprint 1: Foundation**
- ✅ Basic upload interface
- ✅ Drag and drop functionality
- ✅ DICOM file detection
- ✅ 256x256 preview generation
- ✅ Integration with YUETransfer

### **Sprint 2: Organization**
- ✅ Folder upload support
- ✅ Smart file organization
- ✅ Duplicate detection
- ✅ Metadata extraction

### **Sprint 3: Advanced Features**
- ✅ Multiple preview sizes
- ✅ DICOM anonymization
- ✅ Progress tracking
- ✅ Resume upload

### **Sprint 4: Integration**
- ✅ TotalSegmentator integration
- ✅ 10GB file support
- ✅ Mobile responsive
- ✅ Backup integration

### **Sprint 5: Production**
- ✅ SFTP support
- ✅ Advanced error handling
- ✅ Export reports
- ✅ Dark mode

## 🔒 Security

- **User Authentication**: Integrated with YUETransfer
- **File Validation**: DICOM file verification
- **Path Security**: Directory traversal protection
- **Access Control**: User-specific file access
- **Audit Logging**: Complete activity tracking

## 📈 Performance

- **Upload Speed**: 100MB/s target
- **Preview Generation**: <5 seconds
- **Duplicate Detection**: <1 second for 1000 files
- **System Response**: <2 seconds

## 🛠️ Development

### **Running Tests**
```bash
# Use the correct Python environment
C:\Users\ZERO\.conda\envs\totalsegmentator\python.exe -m pytest tests/
```

### **Code Style**
```bash
# Format code
C:\Users\ZERO\.conda\envs\totalsegmentator\python.exe -m black app/
C:\Users\ZERO\.conda\envs\totalsegmentator\python.exe -m flake8 app/
```

### **Documentation**
```bash
# Generate API docs
C:\Users\ZERO\.conda\envs\totalsegmentator\python.exe -m pdoc app/
```

## 📞 Support

- **Documentation**: This README + inline code comments
- **Issues**: Create GitHub issues
- **Configuration**: Check config/ directory
- **Logs**: Check logs/ directory

---

**🎯 Ready for Sprint 1 implementation!** 🚀
### **Code Style**
```bash
# Format code
C:\Users\ZERO\.conda\envs\totalsegmentator\python.exe -m black app/
C:\Users\ZERO\.conda\envs\totalsegmentator\python.exe -m flake8 app/
```

### **Documentation**
```bash
# Generate API docs
C:\Users\ZERO\.conda\envs\totalsegmentator\python.exe -m pdoc app/
```

## 📞 Support

- **Documentation**: This README + inline code comments
- **Issues**: Create GitHub issues
- **Configuration**: Check config/ directory
- **Logs**: Check logs/ directory

---

**🎯 Ready for Sprint 1 implementation!** 🚀

## 📋 System Overview

**YUEUPLOAD** is a standalone, modular DICOM upload system that communicates with:
- **YUETransfer** - User authentication and file management
- **TotalSegmentator** - Medical image segmentation processing
- **user_files** - File storage and organization

## 🏗️ Architecture

```
TotalSegmentator/
├── YUEUPLOAD/                    # ← This system
│   ├── app/                      # Main application
│   ├── config/                   # Configuration files
│   ├── templates/                # HTML templates
│   ├── static/                   # CSS, JS, images
│   ├── uploads/                  # Temporary upload storage
│   ├── logs/                     # System logs
│   └── tests/                    # Test files
├── yuetransfer/                  # YUETransfer system
├── totalsegmentator/             # TotalSegmentator system
└── user_files/                   # User file storage
```

## 🔗 Communication Interfaces

### **1. YUETransfer Communication**
- **Authentication**: Use YUETransfer's user system
- **File Browser**: Integrate with existing file browser
- **User Management**: Share user sessions and permissions
- **Navigation**: Seamless integration in YUETransfer interface

### **2. TotalSegmentator Communication**
- **API Endpoints**: Send files for segmentation
- **Job Management**: Track segmentation progress
- **Results Handling**: Receive and organize segmentation results
- **Configuration**: Share TotalSegmentator settings

### **3. user_files Communication**
- **Storage Integration**: Direct access to user folders
- **File Organization**: Use existing folder structure
- **Metadata Management**: Store DICOM metadata
- **Backup Integration**: Work with existing backup systems

## 📁 Folder Structure

```
YUEUPLOAD/
├── app/
│   ├── __init__.py              # Flask app initialization
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── upload.py            # Upload routes
│   │   ├── preview.py           # DICOM preview routes
│   │   ├── metadata.py          # Metadata routes
│   │   └── integration.py       # Integration routes
│   ├── models/
│   │   ├── __init__.py
│   │   ├── upload.py            # Upload models
│   │   └── dicom.py             # DICOM models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── upload_service.py    # Upload processing
│   │   ├── dicom_service.py     # DICOM processing
│   │   ├── preview_service.py   # Preview generation
│   │   └── integration_service.py # System integration
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py        # File operations
│       ├── dicom_utils.py       # DICOM utilities
│       └── security.py          # Security utilities
├── config/
│   ├── __init__.py
│   ├── settings.py              # Main settings
│   ├── yuetransfer.py           # YUETransfer config
│   ├── totalsegmentator.py      # TotalSegmentator config
│   └── user_files.py            # user_files config
├── templates/
│   ├── base.html                # Base template
│   ├── upload/
│   │   ├── index.html           # Main upload interface
│   │   ├── progress.html        # Upload progress
│   │   ├── preview.html         # DICOM preview
│   │   └── metadata.html        # Metadata display
│   └── components/
│       ├── upload_form.html     # Upload form component
│       ├── progress_bar.html    # Progress bar component
│       └── preview_card.html    # Preview card component
├── static/
│   ├── css/
│   │   ├── main.css             # Main styles
│   │   ├── upload.css           # Upload styles
│   │   └── preview.css          # Preview styles
│   ├── js/
│   │   ├── upload.js            # Upload functionality
│   │   ├── dragdrop.js          # Drag and drop
│   │   ├── preview.js           # Preview handling
│   │   └── progress.js          # Progress tracking
│   └── img/
│       ├── icons/               # System icons
│       └── previews/            # Generated previews
├── uploads/
│   ├── temp/                    # Temporary uploads
│   ├── processing/              # Files being processed
│   └── completed/               # Completed uploads
├── logs/
│   ├── upload.log               # Upload logs
│   ├── error.log                # Error logs
│   └── access.log               # Access logs
├── tests/
│   ├── test_upload.py           # Upload tests
│   ├── test_dicom.py            # DICOM tests
│   └── test_integration.py      # Integration tests
├── requirements.txt             # Python dependencies
├── config.py                    # Main configuration
├── run.py                       # Application entry point
└── README.md                    # This file
```

## 🔧 Configuration

### **YUETransfer Integration**
```python
# config/yuetransfer.py
YUETRANSFER_URL = "http://localhost:5000"
YUETRANSFER_AUTH_ENDPOINT = "/api/auth"
YUETRANSFER_FILE_ENDPOINT = "/api/files"
```

### **TotalSegmentator Integration**
```python
# config/totalsegmentator.py
TOTALSEGMENTATOR_URL = "http://localhost:8000"
TOTALSEGMENTATOR_API_KEY = "your_api_key"
TOTALSEGMENTATOR_ENDPOINTS = {
    "upload": "/api/upload",
    "process": "/api/process",
    "status": "/api/status",
    "download": "/api/download"
}
```

### **user_files Integration**
```python
# config/user_files.py
USER_FILES_ROOT = "../user_files"
USER_FILES_STRUCTURE = {
    "uploads": "uploads",
    "projects": "projects",
    "patients": "patients",
    "studies": "studies",
    "previews": "previews",
    "metadata": "metadata"
}
```

## 🚀 Quick Start

### **1. Installation**
```bash
cd YUEUPLOAD
pip install -r requirements.txt
```

### **2. Configuration**
```bash
# Copy and edit configuration files
cp config/settings.example.py config/settings.py
```

### **3. Run the System**
```bash
python run.py
```

### **4. Access the Interface**
- **Web Interface**: http://localhost:5001
- **API Documentation**: http://localhost:5001/api/docs

## 📊 Features

### **Sprint 1: Foundation**
- ✅ Basic upload interface
- ✅ Drag and drop functionality
- ✅ DICOM file detection
- ✅ 256x256 preview generation
- ✅ Integration with YUETransfer

### **Sprint 2: Organization**
- ✅ Folder upload support
- ✅ Smart file organization
- ✅ Duplicate detection
- ✅ Metadata extraction

### **Sprint 3: Advanced Features**
- ✅ Multiple preview sizes
- ✅ DICOM anonymization
- ✅ Progress tracking
- ✅ Resume upload

### **Sprint 4: Integration**
- ✅ TotalSegmentator integration
- ✅ 10GB file support
- ✅ Mobile responsive
- ✅ Backup integration

### **Sprint 5: Production**
- ✅ SFTP support
- ✅ Advanced error handling
- ✅ Export reports
- ✅ Dark mode

## 🔒 Security

- **User Authentication**: Integrated with YUETransfer
- **File Validation**: DICOM file verification
- **Path Security**: Directory traversal protection
- **Access Control**: User-specific file access
- **Audit Logging**: Complete activity tracking

## 📈 Performance

- **Upload Speed**: 100MB/s target
- **Preview Generation**: <5 seconds
- **Duplicate Detection**: <1 second for 1000 files
- **System Response**: <2 seconds

## 🛠️ Development

### **Running Tests**
```bash
python -m pytest tests/
```

### **Code Style**
```bash
# Format code
black app/
flake8 app/
```

### **Documentation**
```bash
# Generate API docs
python -m pdoc app/
```

## 📞 Support

- **Documentation**: This README + inline code comments
- **Issues**: Create GitHub issues
- **Configuration**: Check config/ directory
- **Logs**: Check logs/ directory

---

**🎯 Ready for Sprint 1 implementation!** 🚀