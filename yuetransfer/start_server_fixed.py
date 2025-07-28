#!/usr/bin/env python3
"""
Fixed YueTransfer Server Starter with CSRF Fix
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app import create_app
from app.config import Config

def main():
    """Start the YueTransfer server with CSRF fix"""
    print("🚀 Starting YueTransfer Server (CSRF Fixed)...")
    
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
    
    # Load configuration with CSRF fixes
    config = Config()
    config.WEB_HOST = "127.0.0.1"  # Bind to localhost
    config.WEB_PORT = 8080
    config.DEBUG = True
    config.ENV = "development"
    
    # CSRF and Session fixes
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
    print(f"🔐 CSRF Protection: Enabled")
    print(f"🔑 Secret Key: {config.SECRET_KEY[:20]}...")
    print("=" * 60)
    
    # Create and run the Flask app
    app = create_app(config)
    
    print("✅ Starting web server...")
    print("🌐 Access at: http://localhost:8080")
    print("🔐 Login: pokpok / pokpok")
    print("⚠️  If you get CSRF errors, clear your browser cache/cookies!")
    print("Press Ctrl+C to stop the server")
    
    app.run(
        host=config.WEB_HOST,
        port=config.WEB_PORT,
        debug=config.DEBUG,
        use_reloader=False
    )

if __name__ == "__main__":
    main() 