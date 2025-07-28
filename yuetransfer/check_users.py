#!/usr/bin/env python3
"""
Check users in YueTransfer database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User

def check_users():
    """Check what users exist in the database"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking Users in Database...")
        print("=" * 50)
        
        # Check if database exists
        try:
            users = User.query.all()
            print(f"✅ Found {len(users)} users in database")
            
            if users:
                print("\n📋 Users:")
                for user in users:
                    admin_status = "👑 ADMIN" if user.is_admin else "👤 USER"
                    print(f"{admin_status} | {user.username} | {user.email} | Created: {user.created_at}")
            else:
                print("❌ No users found in database")
                
        except Exception as e:
            print(f"❌ Database error: {e}")
            print("Database might not be initialized")

if __name__ == '__main__':
    check_users() 