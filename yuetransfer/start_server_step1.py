#!/usr/bin/env python3
"""
YueTransfer Server - Step 1: Basic File Structure
"""

import os
import sys
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.utils import secure_filename

# Simple user class
class SimpleUser(UserMixin):
    def __init__(self, username, is_admin=False):
        self.id = username
        self.username = username
        self.is_admin = is_admin
    
    def get_user_directory(self):
        """Get user's root directory"""
        base_dir = os.path.join(os.getcwd(), 'user_data')
        user_dir = os.path.join(base_dir, self.username)
        return user_dir
    
    def ensure_user_directories(self):
        """Create user directory structure"""
        user_dir = self.get_user_directory()
        directories = [
            user_dir,
            os.path.join(user_dir, 'uploads'),
            os.path.join(user_dir, 'dicom'),
            os.path.join(user_dir, 'nifti'),
            os.path.join(user_dir, 'results'),
            os.path.join(user_dir, 'temp')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        return user_dir

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-for-testing-only'
app.config['WTF_CSRF_ENABLED'] = False
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB max file size

# Setup login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simple user database
users = {
    'pokpok': {'password': 'pokpok', 'is_admin': True},
    'aaa': {'password': 'aaa', 'is_admin': False},
    'bbb': {'password': 'bbb', 'is_admin': False},
    'ccc': {'password': 'ccc', 'is_admin': False},
}

@login_manager.user_loader
def load_user(username):
    if username in users:
        return SimpleUser(username, users[username]['is_admin'])
    return None

# File operations helper functions
def get_directory_contents(path):
    """Get contents of a directory"""
    if not os.path.exists(path):
        return []
    
    contents = []
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            is_dir = os.path.isdir(item_path)
            
            # Get file stats
            stat = os.stat(item_path)
            size = stat.st_size if not is_dir else 0
            modified = datetime.fromtimestamp(stat.st_mtime)
            
            contents.append({
                'name': item,
                'is_directory': is_dir,
                'size': size,
                'modified': modified.strftime('%Y-%m-%d %H:%M:%S'),
                'path': item_path
            })
    except PermissionError:
        pass
    
    # Sort: directories first, then files
    contents.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))
    return contents

def format_file_size(size):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def create_folder(path, folder_name):
    """Create a new folder"""
    folder_name = secure_filename(folder_name)
    if not folder_name:
        return False, "Invalid folder name"
    
    new_folder_path = os.path.join(path, folder_name)
    if os.path.exists(new_folder_path):
        return False, "Folder already exists"
    
    try:
        os.makedirs(new_folder_path)
        return True, "Folder created successfully"
    except Exception as e:
        return False, f"Error creating folder: {str(e)}"

# Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>YueTransfer Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h3>YueTransfer Login</h3>
                    </div>
                    <div class="card-body">
                        {% with messages = get_flashed_messages() %}
                            {% if messages %}
                                <div class="alert alert-danger">{{ messages[0] }}</div>
                            {% endif %}
                        {% endwith %}
                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label">Username</label>
                                <input type="text" name="username" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password</label>
                                <input type="password" name="password" class="form-control" required>
                            </div>
                            <button type="submit" class="btn btn-primary">Login</button>
                        </form>
                        <div class="mt-3">
                            <small>Available users: pokpok/pokpok, aaa/aaa, bbb/bbb, ccc/ccc</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>YueTransfer Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">🧠 YueTransfer</a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text me-3">Welcome {{ current_user.username }}!</span>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h4><i class="fas fa-tachometer-alt"></i> Dashboard</h4>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="card border-primary">
                                    <div class="card-body text-center">
                                        <i class="fas fa-folder fa-3x text-primary mb-3"></i>
                                        <h5>File Browser</h5>
                                        <p>Browse your files and folders</p>
                                        <a href="{{ url_for('file_browser') }}" class="btn btn-primary">
                                            <i class="fas fa-eye"></i> Browse Files
                                        </a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card border-success">
                                    <div class="card-body text-center">
                                        <i class="fas fa-upload fa-3x text-success mb-3"></i>
                                        <h5>Upload Files</h5>
                                        <p>Upload DICOM and NIfTI files</p>
                                        <button class="btn btn-success" disabled>
                                            <i class="fas fa-upload"></i> Coming Soon
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card border-info">
                                    <div class="card-body text-center">
                                        <i class="fas fa-brain fa-3x text-info mb-3"></i>
                                        <h5>TotalSegmentator</h5>
                                        <p>Process medical images</p>
                                        <button class="btn btn-info" disabled>
                                            <i class="fas fa-cogs"></i> Coming Soon
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row mt-4">
                            <div class="col-12">
                                <div class="card">
                                    <div class="card-header">
                                        <h5><i class="fas fa-info-circle"></i> User Directory Structure</h5>
                                    </div>
                                    <div class="card-body">
                                        <p><strong>Your files are stored in:</strong></p>
                                        <code>{{ user_directory }}</code>
                                        <div class="mt-3">
                                            <h6>Directory Structure:</h6>
                                            <ul>
                                                <li><code>uploads/</code> - General file uploads</li>
                                                <li><code>dicom/</code> - DICOM medical images</li>
                                                <li><code>nifti/</code> - NIfTI format files</li>
                                                <li><code>results/</code> - TotalSegmentator results</li>
                                                <li><code>temp/</code> - Temporary files</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

FILE_BROWSER_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>File Browser - YueTransfer</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">🧠 YueTransfer</a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text me-3">{{ current_user.username }}</span>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h4><i class="fas fa-folder"></i> File Browser</h4>
                <div>
                    <button class="btn btn-success btn-sm" data-bs-toggle="modal" data-bs-target="#createFolderModal">
                        <i class="fas fa-plus"></i> New Folder
                    </button>
                    <a href="{{ url_for('dashboard') }}" class="btn btn-secondary btn-sm">
                        <i class="fas fa-arrow-left"></i> Back to Dashboard
                    </a>
                </div>
            </div>
            <div class="card-body">
                <div class="mb-3">
                    <nav aria-label="breadcrumb">
                        <ol class="breadcrumb">
                            <li class="breadcrumb-item">
                                <i class="fas fa-home"></i> {{ current_user.username }}
                            </li>
                            {% for part in breadcrumbs %}
                                <li class="breadcrumb-item">{{ part }}</li>
                            {% endfor %}
                        </ol>
                    </nav>
                </div>
                
                {% if contents %}
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Type</th>
                                    <th>Size</th>
                                    <th>Modified</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for item in contents %}
                                <tr>
                                    <td>
                                        {% if item.is_directory %}
                                            <i class="fas fa-folder text-warning"></i>
                                        {% else %}
                                            <i class="fas fa-file text-primary"></i>
                                        {% endif %}
                                        {{ item.name }}
                                    </td>
                                    <td>
                                        {% if item.is_directory %}
                                            <span class="badge bg-warning">Folder</span>
                                        {% else %}
                                            <span class="badge bg-primary">File</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        {% if not item.is_directory %}
                                            {{ item.size_formatted }}
                                        {% else %}
                                            -
                                        {% endif %}
                                    </td>
                                    <td>{{ item.modified }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <div class="text-center py-5">
                        <i class="fas fa-folder-open fa-4x text-muted mb-3"></i>
                        <h5 class="text-muted">This folder is empty</h5>
                        <p class="text-muted">Create a new folder or upload some files to get started.</p>
                    </div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <!-- Create Folder Modal -->
    <div class="modal fade" id="createFolderModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                                 <form method="POST" action="{{ url_for('create_folder_route') }}">
                    <div class="modal-header">
                        <h5 class="modal-title">Create New Folder</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="folderName" class="form-label">Folder Name</label>
                            <input type="text" class="form-control" id="folderName" name="folder_name" required>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="submit" class="btn btn-success">Create Folder</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password:
            user = SimpleUser(username, users[username]['is_admin'])
            login_user(user)
            
            # Create user directories on login
            user.ensure_user_directories()
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    user_directory = current_user.get_user_directory()
    return render_template_string(DASHBOARD_TEMPLATE, 
                                current_user=current_user, 
                                user_directory=user_directory)

@app.route('/files')
@login_required
def file_browser():
    user_dir = current_user.get_user_directory()
    contents = get_directory_contents(user_dir)
    
    # Format file sizes
    for item in contents:
        if not item['is_directory']:
            item['size_formatted'] = format_file_size(item['size'])
    
    breadcrumbs = ['Root']
    
    return render_template_string(FILE_BROWSER_TEMPLATE, 
                                current_user=current_user,
                                contents=contents,
                                breadcrumbs=breadcrumbs)

@app.route('/create_folder', methods=['POST'])
@login_required
def create_folder_route():
    folder_name = request.form.get('folder_name', '').strip()
    
    if not folder_name:
        flash('Folder name is required', 'error')
        return redirect(url_for('file_browser'))
    
    user_dir = current_user.get_user_directory()
    success, message = create_folder(user_dir, folder_name)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('file_browser'))

if __name__ == '__main__':
    print("🚀 Starting YueTransfer Server - Step 1: Basic File Structure")
    print("=" * 60)
    print("🌐 Web Interface: http://localhost:5000")
    print("🔑 Login Credentials:")
    print("   - pokpok / pokpok (Admin)")
    print("   - aaa / aaa (User)")
    print("   - bbb / bbb (User)")
    print("   - ccc / ccc (User)")
    print("=" * 60)
    print("✅ New Features:")
    print("   - User directory structure creation")
    print("   - Basic file browser")
    print("   - Create new folders")
    print("   - File/folder listing with details")
    print("=" * 60)
    
    app.run(host='127.0.0.1', port=5000, debug=True) 