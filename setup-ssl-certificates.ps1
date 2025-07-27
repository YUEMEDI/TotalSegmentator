# PowerShell script to set up SSL certificates for TotalSegmentator
# Run as Administrator

param(
    [Parameter(Mandatory=$true)]
    [string]$Domain,
    
    [Parameter(Mandatory=$false)]
    [string]$Email = "admin@$Domain"
)

Write-Host "Setting up SSL certificates for $Domain" -ForegroundColor Green

# Method 1: Let's Encrypt (Free, Recommended)
function Setup-LetsEncrypt {
    Write-Host "Installing Certbot for Let's Encrypt..." -ForegroundColor Yellow
    
    # Install Chocolatey if not present
    if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Host "Installing Chocolatey..."
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    }
    
    # Install Certbot
    choco install certbot -y
    
    # Get certificate (requires port 80 to be accessible)
    Write-Host "Requesting SSL certificate from Let's Encrypt..."
    Write-Host "Make sure port 80 is forwarded to this machine!" -ForegroundColor Red
    
    $certbotCommand = "certbot certonly --standalone -d $Domain --email $Email --agree-tos --non-interactive"
    cmd /c $certbotCommand
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SSL certificate obtained successfully!" -ForegroundColor Green
        Write-Host "Certificate location: C:\Certbot\live\$Domain\" -ForegroundColor Cyan
        
        # Set up auto-renewal
        $taskAction = New-ScheduledTaskAction -Execute "certbot" -Argument "renew --quiet"
        $taskTrigger = New-ScheduledTaskTrigger -Daily -At "2:00AM"
        $taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
        
        Register-ScheduledTask -TaskName "Certbot Renewal" -Action $taskAction -Trigger $taskTrigger -Settings $taskSettings -Description "Auto-renew Let's Encrypt certificates"
        
        Write-Host "Auto-renewal scheduled for 2:00 AM daily" -ForegroundColor Green
    } else {
        Write-Host "Failed to obtain SSL certificate. Check port forwarding and domain DNS." -ForegroundColor Red
    }
}

# Method 2: Self-signed certificate (for testing)
function Setup-SelfSigned {
    Write-Host "Creating self-signed certificate for testing..." -ForegroundColor Yellow
    
    $certPath = "C:\ssl"
    New-Item -ItemType Directory -Path $certPath -Force
    
    # Create self-signed certificate
    $cert = New-SelfSignedCertificate -DnsName $Domain -CertStoreLocation "cert:\LocalMachine\My" -KeyLength 2048 -KeyAlgorithm RSA -HashAlgorithm SHA256 -KeyExportPolicy Exportable -NotAfter (Get-Date).AddYears(1)
    
    # Export certificate
    $certPassword = ConvertTo-SecureString -String "totalsegmentator2025" -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath "$certPath\$Domain.pfx" -Password $certPassword
    
    # Convert to PEM format for nginx
    $certBase64 = [System.Convert]::ToBase64String($cert.RawData)
    $certPem = "-----BEGIN CERTIFICATE-----`n"
    for ($i = 0; $i -lt $certBase64.Length; $i += 64) {
        $certPem += $certBase64.Substring($i, [Math]::Min(64, $certBase64.Length - $i)) + "`n"
    }
    $certPem += "-----END CERTIFICATE-----"
    
    $certPem | Out-File -FilePath "$certPath\cert.pem" -Encoding ASCII
    
    Write-Host "Self-signed certificate created at: $certPath" -ForegroundColor Green
    Write-Host "Password: totalsegmentator2025" -ForegroundColor Cyan
    Write-Host "WARNING: Self-signed certificates will show security warnings in browsers!" -ForegroundColor Red
}

# Router configuration helper
function Show-RouterConfig {
    Write-Host "`n=== Router Port Forwarding Configuration ===" -ForegroundColor Cyan
    Write-Host "Configure these port forwards on your router:" -ForegroundColor Yellow
    Write-Host "External Port 80  -> Internal IP $(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias Ethernet | Select-Object -First 1).IPAddress Port 80" -ForegroundColor White
    Write-Host "External Port 443 -> Internal IP $(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias Ethernet | Select-Object -First 1).IPAddress Port 443" -ForegroundColor White
    Write-Host "`nDNS Configuration:" -ForegroundColor Yellow
    Write-Host "Point $Domain to your public IP address" -ForegroundColor White
    Write-Host "Your current public IP: $((Invoke-WebRequest -Uri "http://ipinfo.io/ip").Content.Trim())" -ForegroundColor Cyan
}

# Windows Firewall configuration
function Setup-Firewall {
    Write-Host "Configuring Windows Firewall..." -ForegroundColor Yellow
    
    # Allow HTTP and HTTPS
    New-NetFirewallRule -DisplayName "Allow HTTP Inbound" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow -ErrorAction SilentlyContinue
    New-NetFirewallRule -DisplayName "Allow HTTPS Inbound" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow -ErrorAction SilentlyContinue
    New-NetFirewallRule -DisplayName "Allow TotalSegmentator App" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -ErrorAction SilentlyContinue
    
    Write-Host "Firewall rules added for ports 80, 443, and 8000" -ForegroundColor Green
}

# Main execution
Write-Host "Choose SSL certificate method:" -ForegroundColor Cyan
Write-Host "1. Let's Encrypt (Free, requires public domain)" -ForegroundColor White
Write-Host "2. Self-signed (For testing only)" -ForegroundColor White
$choice = Read-Host "Enter choice (1 or 2)"

Setup-Firewall

switch ($choice) {
    "1" { Setup-LetsEncrypt }
    "2" { Setup-SelfSigned }
    default { 
        Write-Host "Invalid choice. Defaulting to self-signed certificate." -ForegroundColor Yellow
        Setup-SelfSigned 
    }
}

Show-RouterConfig

Write-Host "`n=== Next Steps ===" -ForegroundColor Green
Write-Host "1. Configure your router port forwarding" -ForegroundColor White
Write-Host "2. Update DNS records to point to your public IP" -ForegroundColor White
Write-Host "3. Install and configure nginx with the provided config" -ForegroundColor White
Write-Host "4. Start your TotalSegmentator application" -ForegroundColor White
Write-Host "5. Test access via https://$Domain" -ForegroundColor White 