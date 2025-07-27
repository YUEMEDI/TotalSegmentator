#!/usr/bin/env python3
"""
YueTransfer Database Initialization Script
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app import create_app, db
from app.models.user import UserManager, create_default_admin
from app.config import Config

def init_database():
    """Initialize the database and create default admin user"""
    print("🔧 Initializing YueTransfer Database...")
    
    try:
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            # Create all database tables
            print("📊 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Create default admin user
            print("👤 Creating default admin user...")
            create_default_admin()
            
            # Create necessary directories
            print("📁 Creating application directories...")
            create_directories()
            
            print("✅ Database initialization completed successfully!")
            print("\n🎯 Next steps:")
            print("1. Start the application: python main.py")
            print("2. Access the web interface: http://localhost:8080")
            print("3. Login with: admin / admin123")
            print("4. Change the default password immediately!")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary application directories"""
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
        print(f"   ✅ Created: {directory}")

def reset_database():
    """Reset the database (WARNING: This will delete all data!)"""
    print("⚠️  WARNING: This will delete all data!")
    response = input("Are you sure you want to reset the database? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Database reset cancelled.")
        return
    
    try:
        app = create_app()
        
        with app.app_context():
            # Drop all tables
            print("🗑️  Dropping all database tables...")
            db.drop_all()
            
            # Recreate tables
            print("📊 Recreating database tables...")
            db.create_all()
            
            # Create default admin user
            print("👤 Creating default admin user...")
            create_default_admin()
            
            print("✅ Database reset completed successfully!")
            
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        sys.exit(1)

def create_test_users():
    """Create test users for development"""
    print("🧪 Creating test users...")
    
    try:
        app = create_app()
        
        with app.app_context():
            user_manager = UserManager()
            
            # Create test users
            test_users = [
                {
                    'username': 'doctor1',
                    'password': 'password123',
                    'email': 'doctor1@hospital.com',
                    'is_admin': False
                },
                {
                    'username': 'radiologist1',
                    'password': 'password123',
                    'email': 'radiologist1@hospital.com',
                    'is_admin': False
                },
                {
                    'username': 'researcher1',
                    'password': 'password123',
                    'email': 'researcher1@university.edu',
                    'is_admin': False
                }
            ]
            
            for user_data in test_users:
                try:
                    user_manager.create_user(**user_data)
                    print(f"   ✅ Created user: {user_data['username']}")
                except ValueError as e:
                    print(f"   ⚠️  User {user_data['username']} already exists: {e}")
            
            print("✅ Test users created successfully!")
            
    except Exception as e:
        print(f"❌ Failed to create test users: {e}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'reset':
            reset_database()
        elif command == 'test-users':
            create_test_users()
        elif command == 'help':
            print("YueTransfer Database Management")
            print("\nCommands:")
            print("  init_db.py          - Initialize database (default)")
            print("  init_db.py reset    - Reset database (WARNING: deletes all data)")
            print("  init_db.py test-users - Create test users for development")
            print("  init_db.py help     - Show this help message")
        else:
            print(f"Unknown command: {command}")
            print("Use 'init_db.py help' for available commands")
    else:
        init_database()

if __name__ == "__main__":
    main() 