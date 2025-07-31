# YUETransfer Integration Configuration
# Configuration for communicating with the YUETransfer system

import os
from pathlib import Path

# YUETransfer system configuration
class YUETransferConfig:
    # YUETransfer server settings
    YUETRANSFER_URL = os.environ.get('YUETRANSFER_URL', 'http://localhost:5000')
    YUETRANSFER_HOST = os.environ.get('YUETRANSFER_HOST', 'localhost')
    YUETRANSFER_PORT = int(os.environ.get('YUETRANSFER_PORT', 5000))
    
    # API endpoints for YUETransfer communication
    YUETRANSFER_ENDPOINTS = {
        'auth': {
            'login': '/login',
            'logout': '/logout',
            'check_auth': '/api/auth/check',
            'user_info': '/api/auth/user'
        },
        'files': {
            'browse': '/files',
            'create_folder': '/create_folder',
            'delete': '/bulk_operations',
            'rename': '/rename_item',
            'upload': '/upload'
        },
        'dashboard': {
            'main': '/dashboard',
            'file_browser': '/files'
        }
    }
    
    # Authentication settings
    AUTH_METHOD = 'session'  # 'session', 'token', 'oauth'
    SESSION_COOKIE_NAME = 'session'
    AUTH_TIMEOUT = 3600  # 1 hour
    
    # File system integration
    USER_FILES_ROOT = os.environ.get('USER_FILES_ROOT', '../yuetransfer/user_files')
    USER_FILES_STRUCTURE = {
        'uploads': 'uploads',
        'projects': 'projects',
        'patients': 'patients',
        'studies': 'studies',
        'previews': 'previews',
        'metadata': 'metadata',
        'backups': 'backups'
    }
    
    # Navigation integration
    NAVIGATION_INTEGRATION = {
        'add_to_dashboard': True,
        'add_to_file_browser': True,
        'custom_menu_item': True,
        'breadcrumb_integration': True
    }
    
    # User session sharing
    SESSION_SHARING = {
        'enabled': True,
        'cookie_domain': None,  # Set to domain for cross-subdomain sharing
        'cookie_path': '/',
        'session_key_prefix': 'yueupload_'
    }
    
    # File operation permissions
    PERMISSIONS = {
        'read_files': True,
        'write_files': True,
        'delete_files': True,
        'create_folders': True,
        'access_uploads': True,
        'admin_access': False  # Set to True for admin users
    }
    
    # Integration settings
    INTEGRATION_SETTINGS = {
        'auto_redirect': True,
        'shared_styles': True,
        'shared_scripts': True,
        'cross_origin_requests': False
    }
    
    # Error handling
    ERROR_HANDLING = {
        'fallback_to_local_auth': True,
        'retry_attempts': 3,
        'retry_delay': 1,  # seconds
        'timeout': 30  # seconds
    }

# YUETransfer API client configuration
class YUETransferAPIConfig:
    # HTTP client settings
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 1
    
    # Headers for API requests
    DEFAULT_HEADERS = {
        'User-Agent': 'YUEUPLOAD/1.0',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Authentication headers
    AUTH_HEADERS = {
        'session': 'Cookie',
        'token': 'Authorization',
        'oauth': 'Authorization'
    }

# File system integration helpers
def get_user_files_path(username):
    """Get the user files path for a given username"""
    return Path(YUETransferConfig.USER_FILES_ROOT) / username

def get_user_uploads_path(username):
    """Get the user uploads path for a given username"""
    return get_user_files_path(username) / YUETransferConfig.USER_FILES_STRUCTURE['uploads']

def get_user_project_path(username, project_name):
    """Get the user project path for a given username and project"""
    return get_user_files_path(username) / YUETransferConfig.USER_FILES_STRUCTURE['projects'] / project_name

def get_user_patient_path(username, project_name, patient_id):
    """Get the user patient path for a given username, project, and patient"""
    return get_user_project_path(username, project_name) / YUETransferConfig.USER_FILES_STRUCTURE['patients'] / patient_id

def get_user_study_path(username, project_name, patient_id, study_date):
    """Get the user study path for a given username, project, patient, and study"""
    return get_user_patient_path(username, project_name, patient_id) / YUETransferConfig.USER_FILES_STRUCTURE['studies'] / study_date

# URL helpers
def get_yuetransfer_url(endpoint):
    """Get full YUETransfer URL for an endpoint"""
    return f"{YUETransferConfig.YUETRANSFER_URL.rstrip('/')}/{endpoint.lstrip('/')}"

def get_auth_url():
    """Get YUETransfer authentication URL"""
    return get_yuetransfer_url(YUETransferConfig.YUETRANSFER_ENDPOINTS['auth']['login'])

def get_dashboard_url():
    """Get YUETransfer dashboard URL"""
    return get_yuetransfer_url(YUETransferConfig.YUETRANSFER_ENDPOINTS['dashboard']['main'])

def get_file_browser_url():
    """Get YUETransfer file browser URL"""
    return get_yuetransfer_url(YUETransferConfig.YUETRANSFER_ENDPOINTS['dashboard']['file_browser'])

# Permission helpers
def check_user_permission(username, permission):
    """Check if user has specific permission"""
    # This would typically check against user roles/permissions
    # For now, return True for basic permissions
    return YUETransferConfig.PERMISSIONS.get(permission, False)

def is_admin_user(username):
    """Check if user is an admin"""
    # This would typically check against user roles
    # For now, return False
    return YUETransferConfig.PERMISSIONS.get('admin_access', False)

# Integration status
def is_yuetransfer_available():
    """Check if YUETransfer is available"""
    try:
        import requests
        response = requests.get(get_yuetransfer_url('/'), timeout=5)
        return response.status_code == 200
    except:
        return False

# Configuration validation
def validate_config():
    """Validate YUETransfer configuration"""
    errors = []
    
    # Check if user_files directory exists
    if not Path(YUETransferConfig.USER_FILES_ROOT).exists():
        errors.append(f"USER_FILES_ROOT does not exist: {YUETransferConfig.USER_FILES_ROOT}")
    
    # Check if YUETransfer is accessible
    if not is_yuetransfer_available():
        errors.append(f"YUETransfer is not accessible at: {YUETransferConfig.YUETRANSFER_URL}")
    
    return errors