# Complete TotalSegmentator Remote Access Deployment Script
# Run as Administrator on Windows

param(
    [Parameter(Mandatory=$false)]
    [string]$Domain = "totalseg.local",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("cloudflare", "nginx", "tailscale")]
    [string]$Method = "cloudflare",
    
    [Parameter(Mandatory=$false)]
    [string]$QnapIP = "192.168.1.100"
)

Write-Host "🚀 TotalSegmentator Remote Access Setup" -ForegroundColor Green
Write-Host "Domain: $Domain" -ForegroundColor Cyan
Write-Host "Method: $Method" -ForegroundColor Cyan
Write-Host "QNAP IP: $QnapIP" -ForegroundColor Cyan

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Function to install Chocolatey
function Install-Chocolatey {
    if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Host "📦 Installing Chocolatey package manager..." -ForegroundColor Yellow
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Write-Host "✅ Chocolatey installed successfully" -ForegroundColor Green
    } else {
        Write-Host "✅ Chocolatey already installed" -ForegroundColor Green
    }
}

# Function to setup Docker
function Setup-Docker {
    Write-Host "🐳 Setting up Docker Desktop..." -ForegroundColor Yellow
    
    if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
        choco install docker-desktop -y
        Write-Host "⚠️  Docker Desktop installed. Please restart your computer and run this script again." -ForegroundColor Yellow
        Write-Host "After restart, enable WSL2 and GPU support in Docker Desktop settings." -ForegroundColor Cyan
        exit 0
    } else {
        Write-Host "✅ Docker already installed" -ForegroundColor Green
    }
}

# Function to create TotalSegmentator Docker setup
function Create-DockerSetup {
    Write-Host "📝 Creating Docker configuration..." -ForegroundColor Yellow
    
    $dockerDir = "C:\TotalSegmentator"
    New-Item -ItemType Directory -Path $dockerDir -Force | Out-Null
    
    # Create Dockerfile
    $dockerfile = @"
FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install TotalSegmentator
RUN pip install TotalSegmentator

# Install web app dependencies
RUN pip install fastapi uvicorn python-multipart aiofiles redis celery

# Create app directory
WORKDIR /app

# Copy application code (you'll need to create this)
# COPY . /app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"@

    $dockerfile | Out-File -FilePath "$dockerDir\Dockerfile" -Encoding UTF8
    
    # Create docker-compose.yml
    $dockerCompose = @"
version: '3.8'

services:
  totalsegmentator:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - "\\$QnapIP\medical-data:/data"
      - "./temp:/tmp"
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - PYTHONPATH=/app
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl/certs:ro
    depends_on:
      - totalsegmentator
    restart: unless-stopped

volumes:
  redis_data:
"@

    $dockerCompose | Out-File -FilePath "$dockerDir\docker-compose.yml" -Encoding UTF8
    
    Write-Host "✅ Docker configuration created at $dockerDir" -ForegroundColor Green
}

# Function to setup Cloudflare Tunnel
function Setup-CloudflareTunnel {
    Write-Host "☁️ Setting up Cloudflare Tunnel..." -ForegroundColor Yellow
    
    # Install cloudflared
    if (!(Get-Command cloudflared -ErrorAction SilentlyContinue)) {
        $url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        $output = "C:\Windows\System32\cloudflared.exe"
        
        Write-Host "Downloading cloudflared..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri $url -OutFile $output
        
        Write-Host "✅ Cloudflared installed" -ForegroundColor Green
    }
    
    Write-Host "🔧 Cloudflare Tunnel Setup Instructions:" -ForegroundColor Cyan
    Write-Host "1. Go to https://dash.cloudflare.com/" -ForegroundColor White
    Write-Host "2. Select your domain" -ForegroundColor White
    Write-Host "3. Go to Zero Trust > Networks > Tunnels" -ForegroundColor White
    Write-Host "4. Create a new tunnel named 'totalsegmentator'" -ForegroundColor White
    Write-Host "5. Copy the tunnel token and run:" -ForegroundColor White
    Write-Host "   cloudflared service install <TOKEN>" -ForegroundColor Yellow
    Write-Host "6. Configure routes in Cloudflare dashboard:" -ForegroundColor White
    Write-Host "   - $Domain -> http://localhost:8000" -ForegroundColor Yellow
    Write-Host "   - files.$Domain -> http://$QnapIP:8080" -ForegroundColor Yellow
}

# Function to setup Nginx
function Setup-Nginx {
    Write-Host "🌐 Setting up Nginx..." -ForegroundColor Yellow
    
    # Install nginx
    choco install nginx -y
    
    # Copy our nginx config
    $nginxConfig = Get-Content "nginx-reverse-proxy.conf" -Raw
    $nginxConfig = $nginxConfig -replace "QNAP_IP", $QnapIP
    $nginxConfig = $nginxConfig -replace "yourdomain.com", $Domain
    
    $nginxConfigPath = "C:\tools\nginx\conf\nginx.conf"
    $nginxConfig | Out-File -FilePath $nginxConfigPath -Encoding UTF8
    
    Write-Host "✅ Nginx configured" -ForegroundColor Green
    Write-Host "⚠️  Don't forget to:" -ForegroundColor Yellow
    Write-Host "   1. Set up SSL certificates" -ForegroundColor White
    Write-Host "   2. Configure port forwarding (80, 443)" -ForegroundColor White
    Write-Host "   3. Update DNS records" -ForegroundColor White
}

# Function to setup Tailscale
function Setup-Tailscale {
    Write-Host "🔗 Setting up Tailscale..." -ForegroundColor Yellow
    
    # Install Tailscale
    choco install tailscale -y
    
    Write-Host "🔧 Tailscale Setup Instructions:" -ForegroundColor Cyan
    Write-Host "1. Run: tailscale up" -ForegroundColor Yellow
    Write-Host "2. Follow the authentication link" -ForegroundColor White
    Write-Host "3. Your TotalSegmentator will be accessible at:" -ForegroundColor White
    Write-Host "   http://[tailscale-ip]:8000" -ForegroundColor Yellow
    Write-Host "4. Install Tailscale client on devices that need access" -ForegroundColor White
}

# Function to setup Windows services
function Setup-WindowsServices {
    Write-Host "⚙️ Setting up Windows services..." -ForegroundColor Yellow
    
    # Create TotalSegmentator service script
    $serviceScript = @"
@echo off
cd /d C:\TotalSegmentator
docker-compose up -d
"@
    $serviceScript | Out-File -FilePath "C:\TotalSegmentator\start-service.bat" -Encoding ASCII
    
    # Create scheduled task to start on boot
    $taskAction = New-ScheduledTaskAction -Execute "C:\TotalSegmentator\start-service.bat"
    $taskTrigger = New-ScheduledTaskTrigger -AtStartup
    $taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $taskPrincipal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    
    Register-ScheduledTask -TaskName "TotalSegmentator Auto Start" -Action $taskAction -Trigger $taskTrigger -Settings $taskSettings -Principal $taskPrincipal -Force
    
    Write-Host "✅ Auto-start service configured" -ForegroundColor Green
}

# Function to test connectivity
function Test-Setup {
    Write-Host "🧪 Testing setup..." -ForegroundColor Yellow
    
    # Test local connectivity
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10 -ErrorAction Stop
        Write-Host "✅ Local TotalSegmentator service is responding" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Local service not responding. Make sure Docker containers are running." -ForegroundColor Yellow
    }
    
    # Test QNAP connectivity
    try {
        $response = Invoke-WebRequest -Uri "http://$QnapIP:8080" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ QNAP file manager is accessible" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  QNAP not accessible. Check IP address and file manager service." -ForegroundColor Yellow
    }
}

# Main execution
Write-Host "Starting deployment..." -ForegroundColor Green

# Install prerequisites
Install-Chocolatey
Setup-Docker

# Create Docker setup
Create-DockerSetup

# Setup chosen remote access method
switch ($Method) {
    "cloudflare" { Setup-CloudflareTunnel }
    "nginx" { Setup-Nginx }
    "tailscale" { Setup-Tailscale }
}

# Setup Windows services
Setup-WindowsServices

# Test setup
Test-Setup

Write-Host "`n🎉 Remote Access Setup Complete!" -ForegroundColor Green
Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan

switch ($Method) {
    "cloudflare" {
        Write-Host "1. Complete Cloudflare Tunnel setup in dashboard" -ForegroundColor White
        Write-Host "2. Start Docker containers: cd C:\TotalSegmentator && docker-compose up -d" -ForegroundColor White
        Write-Host "3. Access via: https://$Domain" -ForegroundColor White
    }
    "nginx" {
        Write-Host "1. Run SSL setup: .\setup-ssl-certificates.ps1 -Domain $Domain" -ForegroundColor White
        Write-Host "2. Configure router port forwarding (80, 443)" -ForegroundColor White
        Write-Host "3. Update DNS records to point to your public IP" -ForegroundColor White
        Write-Host "4. Start services: cd C:\TotalSegmentator && docker-compose up -d" -ForegroundColor White
        Write-Host "5. Access via: https://$Domain" -ForegroundColor White
    }
    "tailscale" {
        Write-Host "1. Run: tailscale up" -ForegroundColor White
        Write-Host "2. Complete authentication" -ForegroundColor White
        Write-Host "3. Start Docker containers: cd C:\TotalSegmentator && docker-compose up -d" -ForegroundColor White
        Write-Host "4. Access via Tailscale IP on port 8000" -ForegroundColor White
    }
}

Write-Host "`n🔧 Useful Commands:" -ForegroundColor Cyan
Write-Host "Start services: cd C:\TotalSegmentator && docker-compose up -d" -ForegroundColor White
Write-Host "Stop services: cd C:\TotalSegmentator && docker-compose down" -ForegroundColor White
Write-Host "View logs: cd C:\TotalSegmentator && docker-compose logs -f" -ForegroundColor White
Write-Host "Restart: cd C:\TotalSegmentator && docker-compose restart" -ForegroundColor White 