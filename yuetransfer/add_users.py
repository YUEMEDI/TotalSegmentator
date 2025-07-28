#!/usr/bin/env python3
"""
Script to add additional users to YueTransfer database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User, UserManager
from app.utils.auth import create_default_admin

def add_users():
    """Add additional users to the database"""
    app = create_app()
    
    with app.app_context():
        # Ensure default admin exists
        create_default_admin()
        
        # Add additional users
        users_to_add = [
            {'username': 'aaa', 'password': 'aaa', 'email': 'aaa@example.com', 'is_admin': False},
            {'username': 'bbb', 'password': 'bbb', 'email': 'bbb@example.com', 'is_admin': False},
            {'username': 'ccc', 'password': 'ccc', 'email': 'ccc@example.com', 'is_admin': False},
        ]
        
        user_manager = UserManager()
        
        for user_data in users_to_add:
            try:
                # Check if user already exists
                existing_user = User.query.filter_by(username=user_data['username']).first()
                if existing_user:
                    print(f"✅ User '{user_data['username']}' already exists")
                    continue
                
                # Create new user
                user = user_manager.create_user(
                    username=user_data['username'],
                    password=user_data['password'],
                    email=user_data['email'],
                    is_admin=user_data['is_admin']
                )
                print(f"✅ Created user: {user_data['username']} / {user_data['password']}")
                
            except Exception as e:
                print(f"❌ Failed to create user {user_data['username']}: {e}")
        
        # List all users
        print("\n📋 All Users in Database:")
        print("-" * 40)
        all_users = User.query.all()
        for user in all_users:
            admin_status = "👑 ADMIN" if user.is_admin else "👤 USER"
            print(f"{admin_status} | {user.username} / {user.password} | {user.email}")
        
        print(f"\n✅ Total users: {len(all_users)}")

if __name__ == '__main__':
    add_users() 