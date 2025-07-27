"""
YueTransfer Configuration
"""

import os
import yaml
from pathlib import Path

class Config:
    """Application configuration"""
    
    # Basic Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    ENV = 'production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///yuetransfer.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 * 1024  # 16GB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'uploads')
    RESULTS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'results')
    
    # SFTP settings
    SFTP_HOST = '0.0.0.0'
    SFTP_PORT = 2222
    SFTP_ROOT_DIR = UPLOAD_FOLDER
    
    # Web server settings
    WEB_HOST = '0.0.0.0'
    WEB_PORT = 8080
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    
    # File processing settings
    ALLOWED_EXTENSIONS = {
        'dicom': ['.dcm'],
        'nifti': ['.nii', '.nii.gz'],
        'archive': ['.zip', '.tar', '.tar.gz'],
        'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    }
    
    # TotalSegmentator integration
    TOTALSEG_INPUT_FOLDER = os.path.join(UPLOAD_FOLDER, 'selected_for_processing')
    TOTALSEG_OUTPUT_FOLDER = RESULTS_FOLDER
    
    # Security settings
    PASSWORD_MIN_LENGTH = 8
    SESSION_TIMEOUT = 3600  # 1 hour
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'logs', 'yuetransfer.log')
    
    # Redis (for background tasks)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # QNAP NAS integration
    QNAP_ENABLED = os.environ.get('QNAP_ENABLED', 'false').lower() == 'true'
    QNAP_HOST = os.environ.get('QNAP_HOST', '')
    QNAP_USERNAME = os.environ.get('QNAP_USERNAME', '')
    QNAP_PASSWORD = os.environ.get('QNAP_PASSWORD', '')
    QNAP_SHARE = os.environ.get('QNAP_SHARE', '')
    
    def __init__(self):
        """Load configuration from file if available"""
        config_file = Path(__file__).parent.parent / 'config' / 'config.yaml'
        if config_file.exists():
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file):
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
                
            for key, value in config_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                    
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
    
    def save_to_file(self, config_file):
        """Save current configuration to YAML file"""
        try:
            config_data = {}
            for key in dir(self):
                if not key.startswith('_') and key.isupper():
                    value = getattr(self, key)
                    if not callable(value):
                        config_data[key] = value
            
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
                
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    @property
    def is_production(self):
        """Check if running in production mode"""
        return self.ENV == 'production'
    
    @property
    def is_development(self):
        """Check if running in development mode"""
        return self.ENV == 'development'
    
    def get_upload_path(self, username):
        """Get user-specific upload path"""
        return os.path.join(self.UPLOAD_FOLDER, username)
    
    def get_results_path(self, username):
        """Get user-specific results path"""
        return os.path.join(self.RESULTS_FOLDER, username) 