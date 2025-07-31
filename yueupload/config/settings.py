# YUEUPLOAD Configuration Settings
# Main configuration file for the YUEUPLOAD system

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Flask Configuration
class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'yueupload-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Upload settings
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024 * 1024  # 10GB max file size
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    TEMP_FOLDER = os.path.join(BASE_DIR, 'uploads', 'temp')
    PROCESSING_FOLDER = os.path.join(BASE_DIR, 'uploads', 'processing')
    COMPLETED_FOLDER = os.path.join(BASE_DIR, 'uploads', 'completed')
    
    # Allowed file extensions for DICOM
    ALLOWED_EXTENSIONS = {
        'dcm', 'dicom', 'DCM', 'DICOM',  # Standard DICOM extensions
        'nii', 'nii.gz', 'NII', 'NII.GZ',  # NIfTI extensions
        '',  # Files without extensions (common for DICOM)
    }
    
    # Preview settings
    PREVIEW_SIZES = {
        'small': (128, 128),
        'medium': (256, 256),
        'large': (512, 512)
    }
    DEFAULT_PREVIEW_SIZE = 'medium'
    
    # Performance settings
    CHUNK_SIZE = 1024 * 1024  # 1MB chunks for large file uploads
    MAX_CONCURRENT_UPLOADS = 5
    UPLOAD_TIMEOUT = 3600  # 1 hour timeout
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'yueupload.log')
    ERROR_LOG_FILE = os.path.join(BASE_DIR, 'logs', 'error.log')
    ACCESS_LOG_FILE = os.path.join(BASE_DIR, 'logs', 'access.log')
    
    # Security settings
    CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database settings (for metadata storage)
    DATABASE_URL = os.environ.get('DATABASE_URL') or f'sqlite:///{BASE_DIR}/yueupload.db'
    
    # Cache settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # File organization settings
    ORGANIZATION_STRUCTURE = {
        'project': 'projects',
        'patient': 'patients', 
        'study': 'studies',
        'series': 'series',
        'preview': 'previews',
        'metadata': 'metadata'
    }
    
    # Duplicate detection settings
    DUPLICATE_CHECK_METHOD = 'name_size'  # 'name_size', 'hash', 'content'
    DUPLICATE_RESOLUTION = 'rename'  # 'rename', 'skip', 'overwrite', 'ask_user'
    
    # Compression settings
    COMPRESSION_ENABLED = True
    COMPRESSION_ALGORITHM = 'gzip'  # 'gzip', 'bzip2', 'lzma'
    COMPRESSION_LEVEL = 6  # 1-9, higher = better compression but slower
    
    # Backup settings
    BACKUP_ENABLED = True
    BACKUP_RETENTION_DAYS = 30
    BACKUP_LOCATION = os.path.join(BASE_DIR, 'backups')

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Environment-specific settings
def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])

# Create necessary directories
def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        Config.UPLOAD_FOLDER,
        Config.TEMP_FOLDER,
        Config.PROCESSING_FOLDER,
        Config.COMPLETED_FOLDER,
        os.path.dirname(Config.LOG_FILE),
        os.path.dirname(Config.ERROR_LOG_FILE),
        os.path.dirname(Config.ACCESS_LOG_FILE),
        Config.BACKUP_LOCATION
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Initialize directories on import
create_directories()