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
    
    def delete_user(self, user_id):
        """Delete a user and their files"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Delete user files
            import shutil
            user_upload_path = user.get_upload_path()
            user_results_path = user.get_results_path()
            
            if os.path.exists(user_upload_path):
                shutil.rmtree(user_upload_path)
            if os.path.exists(user_results_path):
                shutil.rmtree(user_results_path)
            
            # Delete user from database
            self.db.session.delete(user)
            self.db.session.commit()
            
            return True
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def get_all_users(self, include_inactive=False):
        """Get all users"""
        query = User.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.all()
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        upload_path = user.get_upload_path()
        results_path = user.get_results_path()
        
        stats = {
            'total_files': 0,
            'dicom_files': 0,
            'nifti_files': 0,
            'archive_files': 0,
            'storage_used': user.storage_used,
            'storage_quota': user.storage_quota,
            'storage_percentage': user.get_storage_usage_percentage()
        }
        
        # Count files by type
        if os.path.exists(upload_path):
            for root, dirs, files in os.walk(upload_path):
                for file in files:
                    stats['total_files'] += 1
                    ext = file.lower().split('.')[-1]
                    
                    if ext == 'dcm':
                        stats['dicom_files'] += 1
                    elif ext in ['nii', 'gz']:
                        stats['nifti_files'] += 1
                    elif ext in ['zip', 'tar']:
                        stats['archive_files'] += 1
        
        return stats
    
    def calculate_storage_usage(self, user_id):
        """Calculate and update user storage usage"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        total_size = 0
        upload_path = user.get_upload_path()
        results_path = user.get_results_path()
        
        # Calculate upload folder size
        if os.path.exists(upload_path):
            for root, dirs, files in os.walk(upload_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        
        # Calculate results folder size
        if os.path.exists(results_path):
            for root, dirs, files in os.walk(results_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        
        # Update user storage
        user.storage_used = total_size
        self.db.session.commit()
        
        return total_size

class ProcessingJob(db.Model):
    """Model for tracking TotalSegmentator processing jobs"""
    
    __tablename__ = 'processing_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_name = db.Column(db.String(255), nullable=False)
    input_files = db.Column(db.Text, nullable=False)  # JSON string of file paths
    output_path = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    progress = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # TotalSegmentator settings
    task = db.Column(db.String(100), default='total')
    fast_mode = db.Column(db.Boolean, default=False)
    preview = db.Column(db.Boolean, default=False)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('processing_jobs', lazy=True))
    
    def to_dict(self):
        """Convert job to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_name': self.job_name,
            'status': self.status,
            'progress': self.progress,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'task': self.task,
            'fast_mode': self.fast_mode,
            'preview': self.preview
        }

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