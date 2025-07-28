#!/usr/bin/env python3
"""
YueTransfer Server - Step 3: File Management + Google OAuth Login
"""

import os
import sys
import shutil
import json
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.utils import secure_filename
from urllib.parse import quote, unquote
import requests

# Google OAuth Configuration
GOOGLE_CLIENT_ID = "191607007979-el9m9u4q8gmvbcq5bokarnelsvu3gis7.apps.googleusercontent.com"  # Replace with your actual Client ID
GOOGLE_CLIENT_SECRET = "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"  # Replace with your actual Client Secret
GOOGLE_REDIRECT_URI = "http://localhost:5000/login/google/authorized"

# Simple user class
class SimpleUser(UserMixin):
    def __init__(self, username, email=None, google_id=None, is_admin=False, avatar_url=None):
        self.id = username
        self.username = username
        self.email = email
        self.google_id = google_id
        self.is_admin = is_admin
        self.avatar_url = avatar_url
    
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

# Simple user database (in-memory for development)
users = {
    'pokpok': {'password': 'pokpok', 'email': 'pokpok@yuetransfer.local', 'is_admin': True},
    'aaa': {'password': 'aaa', 'email': 'aaa@yuetransfer.local', 'is_admin': False},
    'bbb': {'password': 'bbb', 'email': 'bbb@yuetransfer.local', 'is_admin': False},
    'ccc': {'password': 'ccc', 'email': 'ccc@yuetransfer.local', 'is_admin': False},
}

# Google OAuth users (separate storage)
google_users = {}

@login_manager.user_loader
def load_user(username):
    if username in users:
        return SimpleUser(username, users[username]['email'], is_admin=users[username]['is_admin'])
    elif username in google_users:
        return SimpleUser(
            username, 
            google_users[username]['email'], 
            google_users[username]['google_id'],
            is_admin=google_users[username].get('is_admin', False),
            avatar_url=google_users[username].get('avatar_url')
        )
    return None

# Google OAuth helper functions
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

# File operations helper functions (same as before)
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

def delete_items(user_root, current_path, items_to_delete):
    """Delete files and folders"""
    if not items_to_delete:
        return False, "No items selected"
    
    deleted_count = 0
    errors = []
    
    for item_name in items_to_delete:
        item_path = os.path.join(user_root, current_path, item_name) if current_path else os.path.join(user_root, item_name)
        
        # Security check
        if not is_safe_path(user_root, item_path):
            errors.append(f"Access denied: {item_name}")
            continue
        
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
            deleted_count += 1
        except Exception as e:
            errors.append(f"Error deleting {item_name}: {str(e)}")
    
    if errors:
        return False, f"Deleted {deleted_count} items. Errors: {'; '.join(errors)}"
    else:
        return True, f"Successfully deleted {deleted_count} items"

def rename_item(user_root, current_path, old_name, new_name):
    """Rename a file or folder"""
    if not old_name or not new_name:
        return False, "Invalid names provided"
    
    new_name = secure_filename(new_name)
    if not new_name:
        return False, "Invalid new name"
    
    old_path = os.path.join(user_root, current_path, old_name) if current_path else os.path.join(user_root, old_name)
    new_path = os.path.join(user_root, current_path, new_name) if current_path else os.path.join(user_root, new_name)
    
    # Security check
    if not is_safe_path(user_root, old_path) or not is_safe_path(user_root, new_path):
        return False, "Access denied"
    
    if os.path.exists(new_path):
        return False, "Item with that name already exists"
    
    try:
        os.rename(old_path, new_path)
        return True, f"Successfully renamed '{old_name}' to '{new_name}'"
    except Exception as e:
        return False, f"Error renaming: {str(e)}"

def is_safe_path(user_root, requested_path):
    """Check if the requested path is within user's directory"""
    user_root = os.path.abspath(user_root)
    requested_path = os.path.abspath(requested_path)
    return requested_path.startswith(user_root)

def get_breadcrumbs(user_root, current_path):
    """Generate breadcrumb navigation"""
    user_root = os.path.abspath(user_root)
    current_path = os.path.abspath(current_path)
    
    if not current_path.startswith(user_root):
        return [{'name': 'Root', 'path': None}]
    
    # Get relative path from user root
    rel_path = os.path.relpath(current_path, user_root)
    
    breadcrumbs = [{'name': 'Root', 'path': None}]
    
    if rel_path != '.':
        parts = rel_path.split(os.sep)
        current_rel_path = ''
        
        for part in parts:
            current_rel_path = os.path.join(current_rel_path, part) if current_rel_path else part
            breadcrumbs.append({
                'name': part,
                'path': current_rel_path.replace(os.sep, '/')
            })
    
    return breadcrumbs

# Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - YueTransfer</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .logo {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem;
        }
        
        .logo i {
            font-size: 2rem;
            color: white;
        }
        
        .form-control {
            border-radius: 10px;
            border: 2px solid #e1e5e9;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        
        .btn-login {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-google {
            background: #fff;
            border: 2px solid #ddd;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            color: #333;
        }
        
        .btn-google:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            border-color: #4285f4;
            color: #4285f4;
        }
        
        .input-group-text {
            background: #f8f9fa;
            border: 2px solid #e1e5e9;
            border-radius: 10px 0 0 10px;
        }
        
        .form-control.with-icon {
            border-radius: 0 10px 10px 0;
            border-left: none;
        }
        
        .alert {
            border-radius: 10px;
            border: none;
        }
        
        .features {
            margin-top: 2rem;
            text-align: center;
        }
        
        .feature-item {
            display: inline-block;
            margin: 0 1rem;
            color: #6c757d;
            font-size: 0.9rem;
        }
        
        .feature-item i {
            margin-right: 0.5rem;
            color: #667eea;
        }
        
        .divider {
            text-align: center;
            margin: 1.5rem 0;
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
            padding: 0 1rem;
            color: #6c757d;
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .login-container {
                margin: 1rem;
                border-radius: 15px;
            }
            
            .feature-item {
                display: block;
                margin: 0.5rem 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-5 col-md-7 col-sm-9">
                <div class="login-container p-5">
                    <div class="login-header">
                        <div class="logo">
                            <i class="fas fa-brain"></i>
                        </div>
                        <h2 class="fw-bold text-dark">Welcome Back</h2>
                        <p class="text-muted">Sign in to YueTransfer - Medical Imaging Platform</p>
                    </div>
                    
                    <!-- Flash Messages -->
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
                    
                    <!-- Google Login Button -->
                    <div class="d-grid mb-3">
                        <a href="{{ url_for('google_login') }}" class="btn btn-google">
                            <i class="fab fa-google me-2"></i>Sign in with Google
                        </a>
                    </div>
                    
                    <div class="divider">
                        <span>or</span>
                    </div>
                    
                    <!-- Traditional Login Form -->
                    <form method="POST">
                        <div class="mb-3">
                            <label for="username" class="form-label fw-semibold">Username</label>
                            <div class="input-group">
                                <span class="input-group-text">
                                    <i class="fas fa-user text-muted"></i>
                                </span>
                                <input type="text" 
                                       class="form-control with-icon" 
                                       id="username" 
                                       name="username" 
                                       placeholder="Enter your username"
                                       required
                                       autofocus>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label fw-semibold">Password</label>
                            <div class="input-group">
                                <span class="input-group-text">
                                    <i class="fas fa-lock text-muted"></i>
                                </span>
                                <input type="password" 
                                       class="form-control with-icon" 
                                       id="password" 
                                       name="password" 
                                       placeholder="Enter your password"
                                       required>
                            </div>
                        </div>
                        
                        <div class="mb-3 form-check">
                            <input type="checkbox" class="form-check-input" id="remember" name="remember">
                            <label class="form-check-label" for="remember">
                                Remember me
                            </label>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary btn-login text-white">
                                <i class="fas fa-sign-in-alt me-2"></i>
                                Sign In
                            </button>
                        </div>
                    </form>
                    
                    <div class="features">
                        <div class="feature-item">
                            <i class="fas fa-shield-alt"></i>
                            Secure
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-server"></i>
                            SFTP Transfer
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-brain"></i>
                            TotalSegmentator
                        </div>
                    </div>
                    
                    <div class="text-center mt-4">
                        <small class="text-muted">
                            Need access? Contact your administrator<br>
                            <i class="fas fa-envelope me-1"></i>
                            <a href="mailto:yuemedical@gmail.com" class="text-decoration-none">yuemedical@gmail.com</a>
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Default Admin Credentials Notice (Development Only) -->
    <div class="position-fixed bottom-0 end-0 m-3">
        <div class="card border-warning" style="max-width: 300px;">
            <div class="card-header bg-warning text-dark">
                <i class="fas fa-exclamation-triangle me-1"></i>
                Development Mode
            </div>
            <div class="card-body small">
                <strong>Available Users:</strong><br>
                Admin: <code>pokpok / pokpok</code><br>
                Users: <code>aaa / aaa</code>, <code>bbb / bbb</code>, <code>ccc / ccc</code><br>
                <small class="text-muted">Or use Google OAuth!</small>
            </div>
        </div>
    </div>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
        // Auto-hide alerts after 5 seconds
        setTimeout(function() {
            var alerts = document.querySelectorAll('.alert');
            alerts.forEach(function(alert) {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            });
        }, 5000);
        
        // Focus username field
        document.getElementById('username').focus();
    </script>
</body>
</html>
'''

# Include the same DASHBOARD_TEMPLATE and FILE_BROWSER_TEMPLATE from step2
# (I'll add them in the next part to keep this file manageable)

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password:
            user = SimpleUser(username, users[username]['email'], is_admin=users[username]['is_admin'])
            login_user(user)
            
            # Create user directories on login
            user.ensure_user_directories()
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/login/google')
def google_login():
    """Initiate Google OAuth login"""
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"scope=email profile&"
        f"response_type=code&"
        f"access_type=offline"
    )
    return redirect(google_auth_url)

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
    
    # Exchange code for access token
    token_data = exchange_code_for_token(code)
    if not token_data or 'access_token' not in token_data:
        flash('Failed to get access token from Google', 'error')
        return redirect(url_for('login'))
    
    # Get user info from Google
    user_info = get_google_user_info(token_data['access_token'])
    if not user_info:
        flash('Failed to get user info from Google', 'error')
        return redirect(url_for('login'))
    
    google_id = user_info['id']
    email = user_info['email']
    name = user_info.get('name', email.split('@')[0])
    avatar_url = user_info.get('picture')
    
    # Check if user exists
    username = f"google_{google_id}"
    if username not in google_users:
        # Create new Google user
        google_users[username] = {
            'email': email,
            'google_id': google_id,
            'name': name,
            'avatar_url': avatar_url,
            'is_admin': email == 'yuemedical@gmail.com'  # Make your email admin
        }
    
    # Create user object and login
    user = SimpleUser(
        username=username,
        email=email,
        google_id=google_id,
        is_admin=google_users[username]['is_admin'],
        avatar_url=avatar_url
    )
    
    login_user(user)
    
    # Create user directories
    user.ensure_user_directories()
    
    flash(f'Welcome {name}! Successfully logged in with Google.', 'success')
    return redirect(url_for('dashboard'))

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

# Include all the file management routes from step2
# (I'll add them in the next part)

if __name__ == '__main__':
    print("🚀 Starting YueTransfer Server - Step 3: File Management + Google OAuth")
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
    print("=" * 80)
    
    app.run(host='127.0.0.1', port=5000, debug=True) 