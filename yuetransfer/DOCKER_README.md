# 🐳 YueTransfer Docker Deployment

Complete Docker setup for YueTransfer with production-ready configuration.

## 🚀 Quick Start

### Prerequisites
- **Docker** - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** - [Install Docker Compose](https://docs.docker.com/compose/install/)

### Quick Deployment

#### **Windows:**
```bash
# Double-click or run:
docker-run.bat

# Or with specific options:
docker-run.bat start
docker-run.bat production
docker-run.bat stop
```

#### **Mac/Linux:**
```bash
# Make script executable
chmod +x docker-run.sh

# Run with options:
./docker-run.sh start
./docker-run.sh production
./docker-run.sh stop
```

#### **Universal Docker Commands:**
```bash
# Build and start
docker-compose up -d

# Start with nginx (production)
docker-compose --profile production up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f
```

## 📁 Docker Files Structure

```
yuetransfer/
├── Dockerfile                    # Main container definition
├── docker-compose.yml           # Multi-service orchestration
├── nginx.conf                   # Reverse proxy configuration
├── .dockerignore               # Files to exclude from build
├── docker-run.sh               # Unix/Linux/Mac runner script
├── docker-run.bat              # Windows runner script
└── DOCKER_README.md            # This documentation
```

## 🔧 Docker Configuration

### **Dockerfile Features:**
- **Python 3.11 slim** - Optimized for size and security
- **Non-root user** - Security best practice
- **Health checks** - Container monitoring
- **Multi-stage build** - Optimized layers
- **Security headers** - Production hardening

### **Docker Compose Services:**

#### **YueTransfer App:**
- **Port**: 5000 (internal)
- **Volumes**: 
  - `./user_files:/app/user_files` - User data persistence
  - `./logs:/app/logs` - Log persistence
- **Environment**: Production settings
- **Health Check**: HTTP endpoint monitoring

#### **Nginx (Production):**
- **Ports**: 80 (HTTP), 443 (HTTPS)
- **Features**:
  - Reverse proxy
  - Rate limiting
  - Gzip compression
  - Security headers
  - SSL/TLS support

## 🌍 Deployment Options

### **1. Development Mode**
```bash
# Simple deployment
docker-compose up -d

# Access: http://localhost:5000
```

### **2. Production Mode**
```bash
# With nginx reverse proxy
docker-compose --profile production up -d

# Access: http://localhost (port 80)
# Direct: http://localhost:5000
```

### **3. Custom Configuration**
```bash
# Edit docker-compose.yml for custom settings
# Then run:
docker-compose up -d
```

## 🔒 Security Features

### **Container Security:**
- ✅ **Non-root user** - Runs as `yuetransfer` user
- ✅ **Minimal base image** - Reduced attack surface
- ✅ **Health checks** - Automatic failure detection
- ✅ **Resource limits** - Prevent resource exhaustion

### **Network Security:**
- ✅ **Isolated networks** - Container communication only
- ✅ **Port exposure** - Only necessary ports exposed
- ✅ **Reverse proxy** - Additional security layer

### **Application Security:**
- ✅ **Rate limiting** - Prevent brute force attacks
- ✅ **Security headers** - XSS, CSRF protection
- ✅ **Input validation** - Path traversal prevention
- ✅ **Session management** - Secure user sessions

## 📊 Monitoring & Logging

### **Health Checks:**
```bash
# Check container health
docker-compose ps

# View health check logs
docker-compose logs yuetransfer
```

### **Logs:**
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f yuetransfer

# View nginx logs
docker-compose logs -f nginx
```

### **Metrics:**
```bash
# Container resource usage
docker stats

# Disk usage
docker system df
```

## 🔧 Customization

### **Environment Variables:**
```yaml
# In docker-compose.yml
environment:
  - FLASK_ENV=production
  - PYTHONUNBUFFERED=1
  - CUSTOM_VAR=value
```

### **Volume Mounts:**
```yaml
# Add custom volumes
volumes:
  - ./custom_data:/app/custom_data
  - ./config:/app/config
```

### **Port Configuration:**
```yaml
# Change exposed ports
ports:
  - "8080:5000"  # External:Internal
```

## 🚀 Production Deployment

### **1. SSL/TLS Setup:**
```bash
# Create SSL directory
mkdir ssl

# Add your certificates
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem

# Edit nginx.conf to enable HTTPS
# Uncomment HTTPS server block
```

### **2. Domain Configuration:**
```nginx
# In nginx.conf
server_name your-domain.com;
```

### **3. Environment Variables:**
```bash
# Create .env file
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
```

### **4. Database (Optional):**
```yaml
# Add to docker-compose.yml
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: yuetransfer
      POSTGRES_USER: yuetransfer
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

## 🛠️ Troubleshooting

### **Common Issues:**

#### **Port Already in Use:**
```bash
# Check what's using the port
netstat -tulpn | grep :5000

# Kill the process or change port in docker-compose.yml
```

#### **Permission Issues:**
```bash
# Fix volume permissions
sudo chown -R 1000:1000 user_files logs
```

#### **Build Failures:**
```bash
# Clean build
docker-compose build --no-cache

# Check Dockerfile syntax
docker build -t test .
```

#### **Container Won't Start:**
```bash
# Check logs
docker-compose logs yuetransfer

# Check health status
docker-compose ps
```

### **Debug Commands:**
```bash
# Enter container
docker-compose exec yuetransfer /bin/bash

# Check container resources
docker stats yuetransfer

# Inspect container
docker inspect yuetransfer
```

## 📈 Performance Optimization

### **Resource Limits:**
```yaml
# In docker-compose.yml
services:
  yuetransfer:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

### **Caching:**
```yaml
# Enable Docker layer caching
docker-compose build --parallel
```

### **Scaling:**
```bash
# Scale the application
docker-compose up -d --scale yuetransfer=3
```

## 🔄 Updates & Maintenance

### **Update Application:**
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### **Update Dependencies:**
```bash
# Update requirements.txt
# Then rebuild
docker-compose build --no-cache
```

### **Backup:**
```bash
# Backup user data
tar -czf backup-$(date +%Y%m%d).tar.gz user_files/

# Backup with Docker
docker run --rm -v yuetransfer_user_files:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz -C /data .
```

## 🎯 Best Practices

### **Security:**
- ✅ Always use non-root users
- ✅ Keep base images updated
- ✅ Scan images for vulnerabilities
- ✅ Use secrets for sensitive data
- ✅ Enable security scanning

### **Performance:**
- ✅ Use multi-stage builds
- ✅ Optimize layer caching
- ✅ Set resource limits
- ✅ Use health checks
- ✅ Monitor resource usage

### **Maintenance:**
- ✅ Regular image updates
- ✅ Log rotation
- ✅ Backup strategies
- ✅ Monitoring setup
- ✅ Documentation updates

---

**🐳 YueTransfer Docker** - Production-ready containerized deployment!