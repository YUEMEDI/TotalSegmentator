#!/usr/bin/env python3
"""
Test user authentication in YueTransfer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import UserManager

def test_login():
    """Test user authentication"""
    app = create_app()
    
    with app.app_context():
        print("🔐 Testing User Authentication...")
        print("=" * 50)
        
        user_manager = UserManager()
        
        # Test credentials
        test_credentials = [
            ('pokpok', 'pokpok'),
            ('aaa', 'aaa'),
            ('bbb', 'bbb'),
            ('ccc', 'ccc'),
        ]
        
        for username, password in test_credentials:
            try:
                user = user_manager.authenticate_user(username, password)
                if user:
                    admin_status = "👑 ADMIN" if user.is_admin else "👤 USER"
                    print(f"✅ {username} / {password} - {admin_status}")
                else:
                    print(f"❌ {username} / {password} - Invalid credentials")
            except Exception as e:
                print(f"❌ {username} / {password} - Error: {e}")

if __name__ == '__main__':
    test_login() 