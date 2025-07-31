# 🖥️ Windows TotalSegmentator Server Setup Package

## 🎯 What You Need to Do on Windows

### **1. Clone the Repository**
```powershell
# Open PowerShell and run:
git clone https://github.com/YUEMEDI/TotalSegmentator.git
cd TotalSegmentator
```

### **2. Install Prerequisites**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install Chocolatey (package manager)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Docker Desktop
choco install docker-desktop -y

# Install Python (if not already installed)
choco install python -y

# Restart computer after Docker installation
```

### **3. Install Python Dependencies**
```powershell
# After restart, install Python packages:
pip install TotalSegmentator nibabel scikit-image trimesh numpy scipy fastapi uvicorn python-multipart aiofiles redis celery
```

### **4. Configure GPU Support**
```powershell
# Install NVIDIA Container Toolkit for Docker GPU support
# Download from: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

# Enable GPU support in Docker Desktop:
# Settings → Resources → WSL Integration → Enable
# Settings → Features in Development → Use containerd → Enable
```

## 🚀 Quick Deployment Options

### **Option A: Simple Local Setup**
```powershell
# 1. Test basic functionality
python export_to_web3d.py

# 2. Start web viewer
python serve_web3d.py

# Access at: http://localhost:8000
```

### **Option B: Remote Access Setup**
```powershell
# Run the comprehensive deployment script
.\deploy-remote-access.ps1 -Domain "totalseg.yourdomain.com" -Method "cloudflare" -QnapIP "192.168.1.100"

# Follow the script instructions for:
# - SSL certificates
# - Domain configuration  
# - Remote access setup
```

### **Option C: Docker Containerized**
```powershell
# Create Docker setup
docker-compose up -d

# This will start:
# - TotalSegmentator web service
# - Redis job queue
# - Nginx reverse proxy
```

## 📁 Files You Have Available

### **Core Scripts:**
- `export_to_web3d.py` - NIfTI → STL/OBJ converter
- `simple_web3d_viewer.py` - 3D web viewer generator
- `serve_web3d.py` - Local HTTP server
- `combine_masks_for_slicer.py` - 3D Slicer compatibility
- `fix_nifti_for_slicer.py` - NIfTI header fixes

### **Deployment Scripts:**
- `deploy-remote-access.ps1` - Complete remote setup
- `setup-ssl-certificates.ps1` - SSL management
- `nginx-reverse-proxy.conf` - Nginx configuration
- `cloudflare-tunnel-config.yml` - Tunnel configuration

### **Documentation:**
- `README_CUSTOM_TOOLS.md` - Complete tool documentation
- `prompt.md` - Technical summary
- `totalsegmentator_3d_web_export_conversation.md` - Full conversation

## 🔧 Hardware Configuration

### **Your RTX 3070 Setup:**
```powershell
# Verify GPU is available
nvidia-smi

# Test CUDA availability
python -c "import torch; print(torch.cuda.is_available())"
```

### **QNAP Integration:**
```powershell
# Map network drive to QNAP
net use Z: \\YOUR-QNAP-IP\medical-data /persistent:yes

# Test access
dir Z:\
```

## 🌐 Network Configuration

### **For Local Access:**
- Ensure Windows Firewall allows ports 8000, 80, 443
- Configure QNAP network sharing

### **For Remote Access:**
- Set up router port forwarding
- Configure dynamic DNS (if needed)
- Set up SSL certificates

## 🏥 Medical Data Workflow

### **Typical Process:**
```
1. DICOM/NIfTI Upload → QNAP Storage
2. TotalSegmentator Processing → GPU (RTX 3070)
3. Results Export → STL/OBJ files
4. Web Visualization → 3D viewer
5. Remote Access → Secure viewing
```

### **File Locations:**
```
Z:\medical-data\
├── uploads\          # Input files
├── processing\       # Temp processing
├── results\          # TotalSegmentator output
├── web-exports\      # 3D web viewers
└── archives\         # Completed cases
```

## 🔒 Security Considerations

### **Local Security:**
- Use Windows Defender or enterprise antivirus
- Keep system updated
- Use strong passwords for all accounts

### **Remote Security:**
- SSL certificates for all external access
- VPN for sensitive data
- Regular security updates
- Access logging enabled

## 📊 Performance Optimization

### **RTX 3070 Settings:**
```python
# Optimize CUDA memory usage
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
```

### **System Optimization:**
- Ensure adequate cooling for 24/7 operation
- Use SSD for temporary processing files
- Configure Windows power settings for high performance

## 🚀 Next Steps

### **Phase 1: Basic Setup**
1. Install all prerequisites
2. Test local TotalSegmentator functionality
3. Set up QNAP network access
4. Test 3D web export pipeline

### **Phase 2: Remote Access**
1. Choose remote access method (Cloudflare/VNC/Nginx)
2. Configure SSL certificates
3. Set up domain and DNS
4. Test remote connectivity

### **Phase 3: Production**
1. Configure automatic startup services
2. Set up monitoring and logging
3. Create backup procedures
4. Document user procedures

## 🆘 Troubleshooting

### **Common Issues:**
- **Docker GPU not working:** Enable WSL2 and container features
- **QNAP not accessible:** Check network configuration and permissions
- **SSL certificate issues:** Verify domain DNS and port forwarding
- **Performance issues:** Check GPU drivers and CUDA installation

### **Support Resources:**
- Check `README_CUSTOM_TOOLS.md` for detailed documentation
- Review conversation logs for context
- Test individual components before full deployment

## 📞 Ready to Start?

**Recommended order:**
1. **Install prerequisites** (Docker, Python, dependencies)
2. **Test basic functionality** locally
3. **Configure QNAP access**
4. **Choose and implement remote access method**
5. **Set up production deployment**

All the tools and scripts are ready - just follow this guide step by step! 🎯 