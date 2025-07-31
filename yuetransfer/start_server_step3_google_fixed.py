import os
import json
import requests
from flask import Flask, render_template_string, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import shutil

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Google OAuth Configuration
GOOGLE_CLIENT_ID = '191607007979-el9m9u4q8gmvbcq5bokarnelsvu3gis7.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
GOOGLE_REDIRECT_URI = 'http://localhost:5000/login/google/authorized'

# User storage (in production, use a database)
users = {
    'pokpok': {'password': generate_password_hash('pokpok'), 'is_admin': True},
    'aaa': {'password': generate_password_hash('aaa'), 'is_admin': False},
    'bbb': {'password': generate_password_hash('bbb'), 'is_admin': False},
    'ccc': {'password': generate_password_hash('ccc'), 'is_admin': False}
}

# Google OAuth users storage - store by username for easier lookup
google_users = {}

class SimpleUser(UserMixin):
    def __init__(self, username, email=None, google_id=None, is_admin=False, avatar_url=None):
        self.id = username
        self.username = username
        self.email = email
        self.google_id = google_id
        self.is_admin = is_admin
        self.avatar_url = avatar_url

    def get_user_directory(self):
        return os.path.join('user_files', self.username)
    
    def ensure_user_directories(self):
        user_dir = self.get_user_directory()
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return user_dir

@login_manager.user_loader
def load_user(username):
    # Check traditional users first
    if username in users:
        user_data = users[username]
        return SimpleUser(username, is_admin=user_data['is_admin'])
    
    # Check Google users (stored by username)
    if username in google_users:
        user_data = google_users[username]
        return SimpleUser(
            username=user_data['username'],
            email=user_data['email'],
            google_id=user_data['google_id'],
            is_admin=user_data.get('is_admin', False),
            avatar_url=user_data.get('avatar_url')
        )
    
    return None

def get_google_user_info(access_token):
    """Get user info from Google using access token"""
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def exchange_code_for_token(code):
    """Exchange authorization code for access token"""
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': GOOGLE_REDIRECT_URI
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json()
    return None

def get_directory_contents(path):
    """Get directory contents with file/folder information"""
    if not os.path.exists(path):
        return []
    
    contents = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        is_dir = os.path.isdir(item_path)
        
        if is_dir:
            size = '--'
            file_type = 'folder'
        else:
            size = os.path.getsize(item_path)
            file_type = 'file'
        
        contents.append({
            'name': item,
            'is_dir': is_dir,
            'size': size,
            'type': file_type
        })
    
    # Sort: folders first, then files, both alphabetically
    contents.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
    return contents

def format_file_size(size):
    """Format file size in human readable format"""
    if size == '--':
        return '--'
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def create_folder(path, folder_name):
    """Create a new folder"""
    try:
        folder_path = os.path.join(path, folder_name)
        if os.path.exists(folder_path):
            return False, f"Folder '{folder_name}' already exists"
        
        os.makedirs(folder_path)
        return True, f"Folder '{folder_name}' created successfully"
    except Exception as e:
        return False, f"Error creating folder: {str(e)}"

def delete_items(user_root, current_path, items_to_delete):
    """Delete multiple items (files/folders)"""
    try:
        target_dir = user_root
        if current_path:
            target_dir = os.path.join(user_root, current_path)
        
        # Security check
        if not is_safe_path(user_root, target_dir):
            return False, "Access denied: Invalid path"
        
        deleted_count = 0
        for item_name in items_to_delete:
            item_path = os.path.join(target_dir, item_name)
            if os.path.exists(item_path):
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                deleted_count += 1
        
        if deleted_count == 1:
            return True, f"1 item deleted successfully"
        else:
            return True, f"{deleted_count} items deleted successfully"
    except Exception as e:
        return False, f"Error deleting items: {str(e)}"

def rename_item(user_root, current_path, old_name, new_name):
    """Rename a file or folder"""
    try:
        target_dir = user_root
        if current_path:
            target_dir = os.path.join(user_root, current_path)
        
        # Security check
        if not is_safe_path(user_root, target_dir):
            return False, "Access denied: Invalid path"
        
        old_path = os.path.join(target_dir, old_name)
        new_path = os.path.join(target_dir, new_name)
        
        if not os.path.exists(old_path):
            return False, f"Item '{old_name}' not found"
        
        if os.path.exists(new_path):
            return False, f"Item '{new_name}' already exists"
        
        os.rename(old_path, new_path)
        return True, f"'{old_name}' renamed to '{new_name}' successfully"
    except Exception as e:
        return False, f"Error renaming item: {str(e)}"

def is_safe_path(user_root, requested_path):
    """Check if the requested path is within the user's directory"""
    return os.path.abspath(requested_path).startswith(os.path.abspath(user_root))

def get_breadcrumbs(user_root, current_path):
    """Generate breadcrumb navigation"""
    breadcrumbs = [{'name': 'Root', 'path': None}]
    
    if current_path:
        path_parts = current_path.split('/')
        for i, part in enumerate(path_parts):
            if part:
                path = '/'.join(path_parts[:i+1])
                breadcrumbs.append({'name': part, 'path': path})
    
    return breadcrumbs

# HTML Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YueTransfer - Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            padding: 40px;
            width: 100%;
            max-width: 400px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .login-header h1 {
            color: #333;
            font-weight: 700;
            margin-bottom: 10px;
            font-size: 2.2rem;
        }
        .login-header p {
            color: #666;
            font-size: 1.1rem;
        }
        .form-control {
            border-radius: 10px;
            border: 2px solid #e1e5e9;
            padding: 12px 15px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 12px;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-google {
            background: #4285f4;
            border: none;
            border-radius: 10px;
            padding: 12px;
            font-weight: 600;
            font-size: 1.1rem;
            color: white;
            width: 100%;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }
        .btn-google:hover {
            background: #357abd;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(66, 133, 244, 0.4);
        }
        .divider {
            text-align: center;
            margin: 20px 0;
            position: relative;
        }
        .divider::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 1px;
            background: #e1e5e9;
        }
        .divider span {
            background: rgba(255, 255, 255, 0.95);
            padding: 0 15px;
            color: #666;
            font-weight: 500;
        }
        .alert {
            border-radius: 10px;
            border: none;
        }
        .input-group-text {
            background: #f8f9fa;
            border: 2px solid #e1e5e9;
            border-right: none;
            border-radius: 10px 0 0 10px;
        }
        .input-group .form-control {
            border-left: none;
            border-radius: 0 10px 10px 0;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1><i class="fas fa-cloud-upload-alt"></i> YueTransfer</h1>
            <p>Secure File Transfer & Management</p>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <!-- Google OAuth Button -->
        <a href="{{ url_for('google_login') }}" class="btn btn-google">
            <i class="fab fa-google"></i> Sign in with Google
        </a>
        
        <!-- Divider -->
        <div class="divider">
            <span>or</span>
        </div>
        
        <!-- Traditional Login Form -->
        <form method="POST">
            <div class="mb-3">
                <div class="input-group">
                    <span class="input-group-text">
                        <i class="fas fa-user"></i>
                    </span>
                    <input type="text" class="form-control" name="username" placeholder="Username" required autofocus>
                </div>
            </div>
            <div class="mb-4">
                <div class="input-group">
                    <span class="input-group-text">
                        <i class="fas fa-lock"></i>
                    </span>
                    <input type="password" class="form-control" name="password" placeholder="Password" required>
                </div>
            </div>
            <button type="submit" class="btn btn-primary w-100">
                <i class="fas fa-sign-in-alt"></i> Sign In
            </button>
        </form>
        
        <div class="text-center mt-4">
            <small class="text-muted">
                <i class="fas fa-shield-alt"></i> Secure authentication powered by YueTransfer
            </small>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YueTransfer - Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
        }
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .stats-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-cloud-upload-alt"></i> YueTransfer
            </a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text me-3">
                    <i class="fas fa-user"></i> Welcome, {{ current_user.username }}
                    {% if current_user.email %}
                        ({{ current_user.email }})
                    {% endif %}
                </span>
                <a class="nav-link" href="{{ url_for('logout') }}">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-md-4">
                <div class="card stats-card mb-4">
                    <div class="card-body text-center">
                        <i class="fas fa-folder fa-3x mb-3"></i>
                        <h4>File Management</h4>
                        <p class="mb-0">Browse and manage your files</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card stats-card mb-4">
                    <div class="card-body text-center">
                        <i class="fas fa-upload fa-3x mb-3"></i>
                        <h4>Upload Files</h4>
                        <p class="mb-0">Upload large files securely</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card stats-card mb-4">
                    <div class="card-body text-center">
                        <i class="fas fa-cogs fa-3x mb-3"></i>
                        <h4>Processing</h4>
                        <p class="mb-0">Process files with TotalSegmentator</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="fas fa-tachometer-alt"></i> Quick Actions
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <a href="{{ url_for('file_browser') }}" class="btn btn-primary btn-lg w-100 mb-3">
                                    <i class="fas fa-folder-open"></i> Browse Files
                                </a>
                            </div>
                            <div class="col-md-6">
                                <a href="#" class="btn btn-outline-primary btn-lg w-100 mb-3">
                                    <i class="fas fa-upload"></i> Upload Files
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

FILE_BROWSER_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YueTransfer - File Browser</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        .breadcrumb {
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .file-item {
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            border: 1px solid #e9ecef;
            transition: all 0.3s ease;
        }
        .file-item:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .file-item.selected {
            background: #e3f2fd;
            border-color: #2196f3;
        }
        .btn-group-sm .btn {
            padding: 0.25rem 0.5rem;
            font-size: 0.875rem;
        }
        .bulk-actions {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid #dee2e6;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                <i class="fas fa-cloud-upload-alt"></i> YueTransfer
            </a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text me-3">
                    <i class="fas fa-user"></i> {{ current_user.username }}
                </span>
                <a class="nav-link" href="{{ url_for('logout') }}">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">
                            <i class="fas fa-folder-open"></i> File Browser
                        </h5>
                        <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createFolderModal">
                            <i class="fas fa-folder-plus"></i> New Folder
                        </button>
                    </div>
                    <div class="card-body">
                        <!-- Breadcrumbs -->
                        <nav aria-label="breadcrumb">
                            <ol class="breadcrumb">
                                {% for breadcrumb in breadcrumbs %}
                                    <li class="breadcrumb-item">
                                        {% if breadcrumb.path is none %}
                                            <a href="{{ url_for('file_browser') }}">{{ breadcrumb.name }}</a>
                                        {% else %}
                                            <a href="{{ url_for('file_browser', path=breadcrumb.path) }}">{{ breadcrumb.name }}</a>
                                        {% endif %}
                                    </li>
                                {% endfor %}
                            </ol>
                        </nav>

                        <!-- Bulk Actions Panel -->
                        <div class="bulk-actions" id="bulkActions" style="display: none;">
                            <div class="row align-items-center">
                                <div class="col-md-6">
                                    <span id="selectedCount">0 items selected</span>
                                </div>
                                <div class="col-md-6 text-end">
                                    <button class="btn btn-danger btn-sm" onclick="deleteSelected()">
                                        <i class="fas fa-trash"></i> Delete Selected
                                    </button>
                                    <button class="btn btn-secondary btn-sm" onclick="clearSelection()">
                                        <i class="fas fa-times"></i> Clear
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- File List -->
                        <div id="fileList">
                            {% for item in files %}
                                <div class="file-item d-flex align-items-center">
                                    <div class="form-check me-3">
                                        <input class="form-check-input file-checkbox" type="checkbox" value="{{ item.name }}" onchange="updateSelection()">
                                    </div>
                                    <div class="flex-grow-1">
                                        <div class="d-flex align-items-center">
                                            <i class="fas fa-{{ 'folder' if item.is_dir else 'file' }} me-2 text-{{ 'warning' if item.is_dir else 'primary' }}"></i>
                                            {% if item.is_dir %}
                                                <a href="{{ url_for('file_browser', path=current_path + '/' + item.name if current_path else item.name) }}" class="text-decoration-none">
                                                    {{ item.name }}
                                                </a>
                                            {% else %}
                                                <span>{{ item.name }}</span>
                                            {% endif %}
                                        </div>
                                        <small class="text-muted">
                                            {{ format_file_size(item.size) }}
                                        </small>
                                    </div>
                                    <div class="btn-group btn-group-sm">
                                        {% if not item.is_dir %}
                                            <button class="btn btn-outline-primary" onclick="renameItem('{{ item.name }}')">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                        {% endif %}
                                        <button class="btn btn-outline-danger" onclick="deleteItem('{{ item.name }}')">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </div>
                            {% else %}
                                <div class="text-center text-muted py-5">
                                    <i class="fas fa-folder-open fa-3x mb-3"></i>
                                    <p>No files or folders found</p>
                                </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Create Folder Modal -->
    <div class="modal fade" id="createFolderModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-folder-plus"></i> Create New Folder
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form method="POST" action="{{ url_for('create_folder_route') }}">
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="folderName" class="form-label">Folder Name</label>
                            <input type="text" class="form-control" id="folderName" name="folder_name" required autofocus>
                        </div>
                        <input type="hidden" name="current_path" value="{{ current_path }}">
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="submit" class="btn btn-primary">Create Folder</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Rename Modal -->
    <div class="modal fade" id="renameModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-edit"></i> Rename Item
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form method="POST" action="{{ url_for('rename_item_route') }}">
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="oldName" class="form-label">Current Name</label>
                            <input type="text" class="form-control" id="oldName" name="old_name" readonly>
                        </div>
                        <div class="mb-3">
                            <label for="newName" class="form-label">New Name</label>
                            <input type="text" class="form-control" id="newName" name="new_name" required autofocus>
                        </div>
                        <input type="hidden" name="current_path" value="{{ current_path }}">
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="submit" class="btn btn-primary">Rename</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Auto-focus on folder name input
        document.getElementById('createFolderModal').addEventListener('shown.bs.modal', function () {
            document.getElementById('folderName').focus();
        });

        // Auto-focus on new name input
        document.getElementById('renameModal').addEventListener('shown.bs.modal', function () {
            document.getElementById('newName').focus();
        });

        function updateSelection() {
            const checkboxes = document.querySelectorAll('.file-checkbox:checked');
            const bulkActions = document.getElementById('bulkActions');
            const selectedCount = document.getElementById('selectedCount');
            
            if (checkboxes.length > 0) {
                bulkActions.style.display = 'block';
                selectedCount.textContent = `${checkboxes.length} item${checkboxes.length > 1 ? 's' : ''} selected`;
            } else {
                bulkActions.style.display = 'none';
            }
        }

        function clearSelection() {
            document.querySelectorAll('.file-checkbox').forEach(checkbox => {
                checkbox.checked = false;
            });
            updateSelection();
        }

        function deleteSelected() {
            const checkboxes = document.querySelectorAll('.file-checkbox:checked');
            const selectedItems = Array.from(checkboxes).map(cb => cb.value);
            
            if (selectedItems.length > 0 && confirm(`Are you sure you want to delete ${selectedItems.length} item(s)?`)) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '{{ url_for("bulk_operations") }}';
                
                const actionInput = document.createElement('input');
                actionInput.type = 'hidden';
                actionInput.name = 'action';
                actionInput.value = 'delete';
                form.appendChild(actionInput);
                
                const pathInput = document.createElement('input');
                pathInput.type = 'hidden';
                pathInput.name = 'current_path';
                pathInput.value = '{{ current_path }}';
                form.appendChild(pathInput);
                
                selectedItems.forEach(item => {
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'selected_items';
                    input.value = item;
                    form.appendChild(input);
                });
                
                document.body.appendChild(form);
                form.submit();
            }
        }

        function deleteItem(itemName) {
            if (confirm(`Are you sure you want to delete "${itemName}"?`)) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '{{ url_for("bulk_operations") }}';
                
                const actionInput = document.createElement('input');
                actionInput.type = 'hidden';
                actionInput.name = 'action';
                actionInput.value = 'delete';
                form.appendChild(actionInput);
                
                const pathInput = document.createElement('input');
                pathInput.type = 'hidden';
                pathInput.name = 'current_path';
                pathInput.value = '{{ current_path }}';
                form.appendChild(pathInput);
                
                const itemInput = document.createElement('input');
                itemInput.type = 'hidden';
                itemInput.name = 'selected_items';
                itemInput.value = itemName;
                form.appendChild(itemInput);
                
                document.body.appendChild(form);
                form.submit();
            }
        }

        function renameItem(itemName) {
            document.getElementById('oldName').value = itemName;
            document.getElementById('newName').value = itemName;
            new bootstrap.Modal(document.getElementById('renameModal')).show();
        }

        // Select all functionality
        function selectAll() {
            const checkboxes = document.querySelectorAll('.file-checkbox');
            const selectAllCheckbox = document.getElementById('selectAll');
            
            checkboxes.forEach(checkbox => {
                checkbox.checked = selectAllCheckbox.checked;
            });
            updateSelection();
        }
    </script>
</body>
</html>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and check_password_hash(users[username]['password'], password):
            user = SimpleUser(username, is_admin=users[username]['is_admin'])
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/login/google')
def google_login():
    """Redirect to Google OAuth"""
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'scope': 'openid email profile',
        'response_type': 'code',
        'access_type': 'offline'
    }
    
    auth_url = f"{google_auth_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    return redirect(auth_url)

@app.route('/login/google/authorized')
def google_authorized():
    """Handle Google OAuth callback"""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        flash(f'Google OAuth error: {error}', 'error')
        return redirect(url_for('login'))
    
    if not code:
        flash('No authorization code received from Google', 'error')
        return redirect(url_for('login'))
    
    # Exchange code for token
    token_data = exchange_code_for_token(code)
    if not token_data:
        flash('Failed to exchange code for token', 'error')
        return redirect(url_for('login'))
    
    access_token = token_data.get('access_token')
    if not access_token:
        flash('No access token received from Google', 'error')
        return redirect(url_for('login'))
    
    # Get user info from Google
    user_info = get_google_user_info(access_token)
    if not user_info:
        flash('Failed to get user info from Google', 'error')
        return redirect(url_for('login'))
    
    # Extract user data
    google_id = user_info.get('id')
    email = user_info.get('email')
    name = user_info.get('name', email)
    avatar_url = user_info.get('picture')
    
    # Create username from email or Google ID
    username = f"google_{email.split('@')[0]}" if email else f"google_{google_id[:8]}"
    
    # Create or get user (store by username)
    if username in google_users:
        user_data = google_users[username]
    else:
        # Create new Google user
        user_data = {
            'username': username,
            'email': email,
            'google_id': google_id,
            'is_admin': False,  # Default to regular user
            'avatar_url': avatar_url
        }
        google_users[username] = user_data
    
    # Create user object and login
    user = SimpleUser(
        username=user_data['username'],
        email=user_data['email'],
        google_id=user_data['google_id'],
        is_admin=user_data.get('is_admin', False),
        avatar_url=user_data.get('avatar_url')
    )
    
    login_user(user)
    flash(f'Welcome, {name}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    current_user.ensure_user_directories()
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/files')
@app.route('/files/<path:path>')
@login_required
def file_browser(path=''):
    current_user.ensure_user_directories()
    user_root = current_user.get_user_directory()
    
    # Build target directory
    if path:
        target_dir = os.path.join(user_root, path)
    else:
        target_dir = user_root
    
    # Security check
    if not is_safe_path(user_root, target_dir):
        flash('Access denied: Invalid path', 'error')
        return redirect(url_for('file_browser'))
    
    # Get directory contents
    files = get_directory_contents(target_dir)
    
    # Generate breadcrumbs
    breadcrumbs = get_breadcrumbs(user_root, path)
    
    return render_template_string(
        FILE_BROWSER_TEMPLATE,
        files=files,
        current_path=path,
        breadcrumbs=breadcrumbs,
        format_file_size=format_file_size
    )

@app.route('/create_folder', methods=['POST'])
@login_required
def create_folder_route():
    folder_name = request.form.get('folder_name', '').strip()
    current_path = request.form.get('current_path', '')
    
    if not folder_name:
        flash('Folder name is required', 'error')
        if current_path:
            return redirect(url_for('file_browser', path=current_path))
        else:
            return redirect(url_for('file_browser'))
    
    user_root = current_user.get_user_directory()
    
    # Build target directory
    if current_path:
        target_dir = os.path.join(user_root, current_path)
    else:
        target_dir = user_root
    
    # Security check
    if not is_safe_path(user_root, target_dir):
        flash('Access denied: Invalid path', 'error')
        return redirect(url_for('file_browser'))
    
    success, message = create_folder(target_dir, folder_name)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    # Handle redirect properly based on current_path
    if current_path:
        return redirect(url_for('file_browser', path=current_path))
    else:
        return redirect(url_for('file_browser'))

@app.route('/bulk_operations', methods=['POST'])
@login_required
def bulk_operations():
    action = request.form.get('action')
    current_path = request.form.get('current_path', '')
    selected_items = request.form.getlist('selected_items')
    
    if not selected_items:
        flash('No items selected', 'error')
        if current_path:
            return redirect(url_for('file_browser', path=current_path))
        else:
            return redirect(url_for('file_browser'))
    
    user_root = current_user.get_user_directory()
    
    if action == 'delete':
        success, message = delete_items(user_root, current_path, selected_items)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
    
    # Handle redirect properly based on current_path
    if current_path:
        return redirect(url_for('file_browser', path=current_path))
    else:
        return redirect(url_for('file_browser'))

@app.route('/rename_item', methods=['POST'])
@login_required
def rename_item_route():
    old_name = request.form.get('old_name', '').strip()
    new_name = request.form.get('new_name', '').strip()
    current_path = request.form.get('current_path', '')
    
    if not old_name or not new_name:
        flash('Both old and new names are required', 'error')
        if current_path:
            return redirect(url_for('file_browser', path=current_path))
        else:
            return redirect(url_for('file_browser'))
    
    user_root = current_user.get_user_directory()
    
    success, message = rename_item(user_root, current_path, old_name, new_name)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    # Handle redirect properly based on current_path
    if current_path:
        return redirect(url_for('file_browser', path=current_path))
    else:
        return redirect(url_for('file_browser'))

if __name__ == '__main__':
    print("🚀 Starting YueTransfer Server - Step 3: File Management + Google OAuth (Fixed)")
    print("=" * 80)
    print("🌐 Web Interface: http://localhost:5000")
    print("🔑 Login Methods:")
    print("   - Traditional: pokpok/pokpok, aaa/aaa, bbb/bbb, ccc/ccc")
    print("   - Google OAuth: Click 'Sign in with Google' button")
    print("=" * 80)
    print("⚠️  IMPORTANT: Configure Google OAuth credentials!")
    print("   1. Replace GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
    print("   2. Set up Google Cloud Console project")
    print("   3. Add authorized redirect URI: http://localhost:5000/login/google/authorized")
    print("=" * 80)
    print("✅ Features:")
    print("   - Beautiful login page with Google OAuth")
    print("   - File/folder checkboxes for selection")
    print("   - Bulk delete operations")
    print("   - Rename files and folders")
    print("   - Auto-focus on input fields")
    print("   - Select all functionality")
    print("   - Enhanced UI with bulk actions panel")
    print("   - CSRF disabled (as in step2)")
    print("   - Port 5000 (as in step2)")
    print("=" * 80)
    
    app.run(host='127.0.0.1', port=5000, debug=True)