#!/usr/bin/env python3
"""
Reset Admin User Script
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app import create_app, db
from app.models.user import User, UserManager
from app.config import Config

def reset_admin_user():
    """Reset admin user with new credentials"""
    print("🔧 Resetting Admin User...")
    
    # Create app context
    config = Config()
    app = create_app(config)
    
    with app.app_context():
        # Delete existing admin user
        old_admin = User.query.filter_by(username='admin').first()
        if old_admin:
            db.session.delete(old_admin)
            print("✅ Deleted old admin user")
        
        # Delete existing pokpok user if exists
        existing_pokpok = User.query.filter_by(username='pokpok').first()
        if existing_pokpok:
            db.session.delete(existing_pokpok)
            print("✅ Deleted existing pokpok user")
        
        # Commit changes
        db.session.commit()
        
        # Create new admin user
        user_manager = UserManager()
        admin_user = user_manager.create_user(
            username='pokpok',
            password='pokpok',
            email='pokpok@yuetransfer.local',
            is_admin=True
        )
        
        if admin_user:
            print("✅ New admin user created successfully!")
            print(f"   Username: pokpok")
            print(f"   Password: pokpok")
            print(f"   Email: pokpok@yuetransfer.local")
            print(f"   Admin: Yes")
        else:
            print("❌ Failed to create new admin user")
            return False
    
    return True

if __name__ == "__main__":
    success = reset_admin_user()
    if success:
        print("\n🎯 Admin user reset completed!")
        print("🌐 You can now login with: pokpok / pokpok")
    else:
        print("\n❌ Admin user reset failed!")
        sys.exit(1) 