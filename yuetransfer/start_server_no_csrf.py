#!/usr/bin/env python3
"""
YueTransfer Server Starter with CSRF Disabled (Development)
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app import create_app
from app.config import Config

def main():
    """Start the YueTransfer server with CSRF disabled"""
    print("🚀 Starting YueTransfer Server (CSRF Disabled)...")
    
    # Create necessary directories
    directories = [
        "app/uploads",
        "app/results",
        "app/logs",
        "app/static/uploads",
        "app/static/thumbnails",
        "users",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Load configuration
    config = Config()
    config.WEB_HOST = "127.0.0.1"  # Bind to localhost
    config.WEB_PORT = 8080
    config.DEBUG = True
    config.ENV = "development"
    
    # Session settings
    config.SECRET_KEY = 'dev-secret-key-change-in-production-2024'
    config.SESSION_COOKIE_SECURE = False
    config.SESSION_COOKIE_HTTPONLY = True
    config.SESSION_COOKIE_SAMESITE = 'Lax'
    config.PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    print("=" * 60)
    print("🎯 YueTransfer - Medical Imaging Transfer Platform")
    print("=" * 60)
    print(f"🌐 Web Interface: http://{config.WEB_HOST}:{config.WEB_PORT}")
    print(f"📁 Upload Folder: {config.UPLOAD_FOLDER}")
    print(f"🔧 Environment: {config.ENV}")
    print(f"🔐 CSRF Protection: DISABLED (Development)")
    print(f"🔑 Secret Key: {config.SECRET_KEY[:20]}...")
    print("=" * 60)
    
    # Create Flask app
    app = create_app(config)
    
    # Disable CSRF for development
    app.config['WTF_CSRF_ENABLED'] = False
    print("✅ CSRF protection disabled for development")
    
    print("✅ Starting web server...")
    print("🌐 Access at: http://localhost:8080")
    print("🔐 Login: pokpok / pokpok")
    print("Press Ctrl+C to stop the server")
    
    app.run(
        host=config.WEB_HOST,
        port=config.WEB_PORT,
        debug=config.DEBUG,
        use_reloader=False
    )

if __name__ == "__main__":
    main() 