"""
YueTransfer User Model and Management
"""

import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """User model for authentication and file management"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    storage_quota = db.Column(db.BigInteger, default=107374182400)  # 100GB default
    storage_used = db.Column(db.BigInteger, default=0)
    
    # User preferences
    theme = db.Column(db.String(20), default='light')
    language = db.Column(db.String(10), default='en')
    timezone = db.Column(db.String(50), default='UTC')
    
    def __init__(self, username, password, email=None, is_admin=False):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.is_admin = is_admin
        
        # Create user directory
        self._create_user_directory()
    
    def _create_user_directory(self):
        """Create user-specific directories"""
        from app.config import Config
        config = Config()
        
        user_dirs = [
            config.get_upload_path(self.username),
            config.get_results_path(self.username),
            os.path.join(config.get_upload_path(self.username), 'dicom_datasets'),
            os.path.join(config.get_upload_path(self.username), 'nifti_files'),
            os.path.join(config.get_upload_path(self.username), 'archives'),
            os.path.join(config.get_upload_path(self.username), 'selected_for_processing')
        ]
        
        for directory in user_dirs:
            os.makedirs(directory, exist_ok=True)
    
    def set_password(self, password):
        """Set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check user password"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Get user ID for Flask-Login"""
        return str(self.id)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def get_storage_usage_percentage(self):
        """Get storage usage as percentage"""
        if self.storage_quota == 0:
            return 0
        return (self.storage_used / self.storage_quota) * 100
    
    def can_upload_file(self, file_size):
        """Check if user can upload file of given size"""
        return (self.storage_used + file_size) <= self.storage_quota
    
    def add_storage_usage(self, size):
        """Add to storage usage"""
        self.storage_used += size
        db.session.commit()
    
    def remove_storage_usage(self, size):
        """Remove from storage usage"""
        self.storage_used = max(0, self.storage_used - size)
        db.session.commit()
    
    def get_upload_path(self):
        """Get user upload path"""
        from app.config import Config
        config = Config()
        return config.get_upload_path(self.username)
    
    def get_results_path(self):
        """Get user results path"""
        from app.config import Config
        config = Config()
        return config.get_results_path(self.username)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'storage_quota': self.storage_quota,
            'storage_used': self.storage_used,
            'storage_usage_percentage': self.get_storage_usage_percentage(),
            'theme': self.theme,
            'language': self.language,
            'timezone': self.timezone
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserManager:
    """User management utility class"""
    
    def __init__(self):
        self.db = db
    
    def create_user(self, username, password, email=None, is_admin=False):
        """Create a new user"""
        try:
            # Check if user already exists
            if self.get_user_by_username(username):
                raise ValueError(f"User '{username}' already exists")
            
            if email and self.get_user_by_email(email):
                raise ValueError(f"Email '{email}' already registered")
            
            # Create user
            user = User(username=username, password=password, email=email, is_admin=is_admin)
            self.db.session.add(user)
            self.db.session.commit()
            
            return user
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return User.query.get(user_id)
    
    def get_user_by_username(self, username):
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    def get_user_by_email(self, email):
        """Get user by email"""
        return User.query.filter_by(email=email).first()
    
    def authenticate_user(self, username, password):
        """Authenticate user with username and password"""
        user = self.get_user_by_username(username)
        if user and user.check_password(password) and user.is_active:
            user.update_last_login()
            return user
        return None
    
    def update_user(self, user_id, **kwargs):
        """Update user information"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Update allowed fields
            allowed_fields = ['email', 'theme', 'language', 'timezone', 'storage_quota']
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)
            
            self.db.session.commit()
            return user
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def change_password(self, user_id, old_password, new_password):
        """Change user password"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            if not user.check_password(old_password):
                raise ValueError("Invalid current password")
            
            user.set_password(new_password)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def delete_user(self, user_id):
        """Delete user and their files"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Delete user files
            self._delete_user_files(user)
            
            # Delete user from database
            self.db.session.delete(user)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def _delete_user_files(self, user):
        """Delete all files belonging to user"""
        import shutil
        from app.config import Config
        
        config = Config()
        user_upload_path = config.get_upload_path(user.username)
        user_results_path = config.get_results_path(user.username)
        
        # Delete user directories
        for path in [user_upload_path, user_results_path]:
            if os.path.exists(path):
                shutil.rmtree(path)
    
    def get_all_users(self, include_inactive=False):
        """Get all users"""
        query = User.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.all()
    
    def get_admin_users(self):
        """Get all admin users"""
        return User.query.filter_by(is_admin=True, is_active=True).all()
    
    def get_user_stats(self):
        """Get user statistics"""
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(is_admin=True, is_active=True).count()
        
        total_storage = db.session.query(db.func.sum(User.storage_used)).scalar() or 0
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users,
            'total_storage_used': total_storage
        }
    
    def search_users(self, query, limit=50):
        """Search users by username or email"""
        return User.query.filter(
            db.or_(
                User.username.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            )
        ).limit(limit).all()

def create_default_admin():
    """Create default admin user if none exists"""
    user_manager = UserManager()
    
    # Check if admin user exists
    admin_user = user_manager.get_user_by_username('admin')
    if not admin_user:
        try:
            # Create default admin user
            admin_user = user_manager.create_user(
                username='admin',
                password='admin123',  # Change this in production!
                email='admin@yuetransfer.local',
                is_admin=True
            )
            print("✅ Default admin user created: admin/admin123")
            print("⚠️  Please change the default password immediately!")
        except Exception as e:
            print(f"❌ Failed to create default admin user: {e}")

def get_user_by_id(user_id):
    """Get user by ID for Flask-Login"""
    return User.query.get(int(user_id)) 