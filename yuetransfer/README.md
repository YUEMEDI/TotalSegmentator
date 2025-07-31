# YueTransfer - Secure File Transfer & Management System

A standalone web application for secure file transfer and management with Google OAuth integration, designed for medical image processing workflows.

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** (Windows, Mac, Linux) - OR - **Docker** (recommended)
- **Internet Connection** (for Google OAuth and CDN resources)
- **Web Browser** (Chrome, Firefox, Safari, Edge)
- **Google OAuth credentials** (optional, for Google login)

### Installation Options

#### **🐳 Option 1: Docker (Recommended)**
```bash
# Windows
docker-run.bat

# Mac/Linux
chmod +x docker-run.sh
./docker-run.sh

# Universal
docker-compose up -d
```
**Access**: http://localhost:5000

#### **🐍 Option 2: Python Native**

##### **Windows:**
1. **Install Python**: Download from [python.org](https://python.org) or use Anaconda
2. **Clone/Copy**: Copy the `yuetransfer` folder to your machine
3. **Install Dependencies**: `pip install -r requirements.txt`
4. **Start Server**: Double-click `start_server.bat` or run `python start_server_step3_google_fixed.py`

##### **Mac/Linux:**
1. **Install Python**: Usually pre-installed, or use package manager
2. **Clone/Copy**: Copy the `yuetransfer` folder to your machine
3. **Make Scripts Executable**: `chmod +x *.sh`
4. **Install Dependencies**: `./install_dependencies.sh`
5. **Start Server**: `./start_server.sh`

##### **Universal Method:**
```bash
# 1. Copy yuetransfer folder to any machine
# 2. Install Python 3.8+
# 3. Install dependencies
pip install -r requirements.txt

# 4. Start server
python start_server_step3_google_fixed.py

# 5. Access web interface
# Open http://localhost:5000 in your browser
```

### Configure Google OAuth (Optional)
- Follow the guide in `google_oauth_setup.md`
- Or run: `python update_google_oauth.py`

## 🔑 Login Methods

### Traditional Login
- **Admin**: pokpok / pokpok
- **Users**: aaa/aaa, bbb/bbb, ccc/ccc

### Google OAuth Login
- Click "Sign in with Google" button
- Requires Google OAuth credentials to be configured

## ✨ Features

### ✅ Implemented
- **User Authentication**: Traditional + Google OAuth
- **File Management**: Browse, create folders, delete, rename
- **Bulk Operations**: Select multiple files/folders
- **User Isolation**: Each user has their own file space
- **Modern UI**: Responsive, Bootstrap-based interface
- **Security**: CSRF protection, secure file paths
- **Cross-Platform**: Works on Windows, Mac, Linux
- **Docker Support**: Production-ready containerization

### 🚧 Planned Features
- **File Upload**: Drag-and-drop file upload
- **TotalSegmentator Integration**: Medical image processing
- **SFTP Server**: Large file transfer support
- **Admin Panel**: User management and monitoring
- **File Preview**: Image and document previews
- **Search**: File and folder search functionality

## 📁 Project Structure

```
yuetransfer/
├── start_server_step3_google_fixed.py  # Main server application
├── start_server.bat                    # Windows startup script
├── start_server.sh                     # Unix/Linux/Mac startup script
├── install_dependencies.sh             # Cross-platform dependency installer
├── update_google_oauth.py              # Google OAuth config tool
├── update_google_oauth.bat             # OAuth config script
├── requirements.txt                    # Python dependencies
├── README.md                          # This file
├── google_oauth_setup.md              # Google OAuth setup guide
├── GOOGLE_OAUTH_QUICK_REFERENCE.md    # Quick OAuth reference
├── user_files/                        # User data directory
├── Dockerfile                         # Docker container definition
├── docker-compose.yml                 # Multi-service orchestration
├── nginx.conf                         # Reverse proxy configuration
├── docker-run.sh                      # Unix/Linux/Mac Docker runner
├── docker-run.bat                     # Windows Docker runner
├── DOCKER_README.md                   # Docker documentation
└── .dockerignore                      # Docker build exclusions
```

## 🔧 Configuration

### Google OAuth Setup
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google+ API
3. Create OAuth 2.0 credentials
4. Add redirect URI: `http://localhost:5000/login/google/authorized`
5. Update credentials in the server file or use the update script

### Server Configuration
- **Port**: 5000 (configurable in the server file)
- **Host**: 127.0.0.1 (localhost)
- **Debug Mode**: Enabled for development

## 🐳 Docker Deployment

### **Quick Docker Start:**
```bash
# Windows
docker-run.bat

# Mac/Linux
./docker-run.sh

# Universal
docker-compose up -d
```

### **Production with Nginx:**
```bash
# Windows
docker-run.bat production

# Mac/Linux
./docker-run.sh production

# Universal
docker-compose --profile production up -d
```

### **Docker Features:**
- ✅ **Production-ready** - Optimized container with security
- ✅ **Nginx Reverse Proxy** - Rate limiting, SSL, compression
- ✅ **Health Checks** - Automatic monitoring
- ✅ **Volume Persistence** - User data survives container restarts
- ✅ **Easy Scaling** - Horizontal scaling support
- ✅ **Security Hardened** - Non-root user, minimal attack surface

**📖 For detailed Docker documentation, see: `DOCKER_README.md`**

## 🛠️ Development

### Adding New Features
1. Edit `start_server_step3_google_fixed.py`
2. Add new routes and functionality
3. Update templates as needed
4. Test thoroughly before deployment

### File Structure
- **Templates**: HTML templates are embedded in the Python file
- **Static Files**: CSS/JS are loaded from CDN
- **User Data**: Stored in `user_files/` directory

## 🔒 Security Features

- **User Authentication**: Flask-Login integration
- **Session Management**: Secure session handling
- **File Path Security**: Prevents directory traversal attacks
- **CSRF Protection**: Cross-site request forgery protection
- **User Isolation**: Users can only access their own files
- **Docker Security**: Non-root user, isolated networks, security headers

## 📝 Usage

1. **Login**: Use traditional credentials or Google OAuth
2. **Browse Files**: Navigate through your file structure
3. **Create Folders**: Use the "New Folder" button
4. **Manage Files**: Select files for bulk operations
5. **Delete/Rename**: Use the action buttons for each file

## 🌍 Cross-Platform Support

### **Windows:**
- ✅ **Fully Supported** - Native Python and batch scripts
- ✅ **Easy Installation** - Python from python.org or Anaconda
- ✅ **Batch Scripts** - `start_server.bat` works perfectly
- ✅ **Docker Support** - `docker-run.bat` for containerized deployment

### **Mac:**
- ✅ **Fully Supported** - Python comes pre-installed
- ✅ **Shell Scripts** - `start_server.sh` and `install_dependencies.sh`
- ✅ **Terminal Commands** - Same Python commands work
- ✅ **Docker Support** - `docker-run.sh` for containerized deployment

### **Linux:**
- ✅ **Fully Supported** - Python usually pre-installed
- ✅ **Package Manager** - `apt`, `yum`, or `pip` for dependencies
- ✅ **Shell Scripts** - `start_server.sh` and `install_dependencies.sh`
- ✅ **Docker Support** - `docker-run.sh` for containerized deployment

## 🐛 Troubleshooting

### Common Issues
- **"ModuleNotFoundError"**: Install dependencies with `pip install -r requirements.txt`
- **Google OAuth errors**: Check credentials and redirect URI
- **Port already in use**: Change port in server file or kill existing process
- **Permission denied (Mac/Linux)**: Run `chmod +x *.sh` to make scripts executable
- **Docker issues**: Check `DOCKER_README.md` for detailed troubleshooting

### Getting Help
- Check the Google OAuth setup guide
- Review server logs for error messages
- Ensure all dependencies are installed
- Verify Python version (3.8+ required)
- For Docker issues, see `DOCKER_README.md`

## 📄 License

This project is part of the TotalSegmentator workflow system.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**YueTransfer** - Secure, modern file management for medical imaging workflows. 