#!/usr/bin/env python3
"""
YueTransfer Server - Simple Version with Error Handling
"""

import os
import sys
from app import create_app

def main():
    """Start the YueTransfer server with error handling"""
    
    # Create Flask app
    app = create_app()
    
    # Disable CSRF protection
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False
    
    # Fix session configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-for-testing-only'
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    
    # Create necessary directories
    from app.config import Config
    config = Config()
    
    # Create base directories
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(config.RESULTS_FOLDER, exist_ok=True)
    os.makedirs(config.DATABASE_PATH, exist_ok=True)
    
    print("🚀 Starting YueTransfer Server (Simple)")
    print("=" * 50)
    print("🌐 Web Interface: http://localhost:8080")
    print("🔑 Login Credentials:")
    print("   - pokpok / pokpok (Admin)")
    print("   - aaa / aaa (User)")
    print("   - bbb / bbb (User)")
    print("   - ccc / ccc (User)")
    print("=" * 50)
    print("⚠️  CSRF Protection: DISABLED (Development Only)")
    print("=" * 50)
    
    # Start the server
    app.run(
        host='127.0.0.1',
        port=8080,
        debug=True,
        use_reloader=False
    )

if __name__ == '__main__':
    main() 