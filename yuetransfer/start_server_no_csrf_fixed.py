#!/usr/bin/env python3
"""
YueTransfer Server - No CSRF Version for Testing
"""

import os
import sys
from app import create_app

def main():
    """Start the YueTransfer server without CSRF protection"""
    
    # Create Flask app
    app = create_app()
    
    # Completely disable CSRF protection
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False
    
    # Fix session configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-for-testing-only'
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    
    # Disable CSRF in all forms
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    app.config['WTF_CSRF_SSL_STRICT'] = False
    
    print("🚀 Starting YueTransfer Server (No CSRF)")
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