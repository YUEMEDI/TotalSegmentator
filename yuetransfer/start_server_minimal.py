#!/usr/bin/env python3
"""
YueTransfer Server - Minimal Version
"""

import os
import sys
from flask import Flask, render_template_string, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from werkzeug.security import check_password_hash

# Simple user class
class SimpleUser(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-for-testing-only'
app.config['WTF_CSRF_ENABLED'] = False

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
        return SimpleUser(username)
    return None

# Simple login template
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

# Simple dashboard template
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>YueTransfer Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between">
                        <h3>Welcome {{ current_user.username }}!</h3>
                        <a href="{{ url_for('logout') }}" class="btn btn-outline-secondary">Logout</a>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-success">
                            <h4>✅ Login Successful!</h4>
                            <p>YueTransfer server is working properly.</p>
                        </div>
                        <div class="row">
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-body text-center">
                                        <h5>🗂️ File Browser</h5>
                                        <p>Browse and manage your files</p>
                                        <button class="btn btn-primary" disabled>Coming Soon</button>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-body text-center">
                                        <h5>📤 Upload Files</h5>
                                        <p>Upload DICOM and NIfTI files</p>
                                        <button class="btn btn-primary" disabled>Coming Soon</button>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-body text-center">
                                        <h5>🧠 TotalSegmentator</h5>
                                        <p>Process medical images</p>
                                        <button class="btn btn-primary" disabled>Coming Soon</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password:
            user = SimpleUser(username)
            login_user(user)
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
    from flask_login import current_user
    return render_template_string(DASHBOARD_TEMPLATE, current_user=current_user)

if __name__ == '__main__':
    print("🚀 Starting YueTransfer Server (Minimal)")
    print("=" * 50)
    print("🌐 Web Interface: http://localhost:5000")
    print("🔑 Login Credentials:")
    print("   - pokpok / pokpok (Admin)")
    print("   - aaa / aaa (User)")
    print("   - bbb / bbb (User)")
    print("   - ccc / ccc (User)")
    print("=" * 50)
    print("⚠️  CSRF Protection: DISABLED (Development Only)")
    print("=" * 50)
    
    app.run(host='127.0.0.1', port=5000, debug=True) 