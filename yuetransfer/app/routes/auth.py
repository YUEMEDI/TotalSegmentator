"""
YueTransfer Authentication Routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models.user import User, UserManager
from app.utils.auth import get_user_permissions

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('Please provide both username and password.', 'error')
            return render_template('auth/login.html')
        
        user_manager = UserManager()
        user = user_manager.authenticate_user(username, password)
        
        if user:
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            
            flash(f'Welcome back, {user.username}!', 'success')
            
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    username = current_user.username
    logout_user()
    flash(f'You have been logged out, {username}.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    if request.method == 'POST':
        user_manager = UserManager()
        
        try:
            # Update user information
            updates = {}
            
            if 'email' in request.form:
                email = request.form.get('email').strip()
                if email and email != current_user.email:
                    # Check if email is already taken
                    if user_manager.get_user_by_email(email):
                        flash('Email address is already in use.', 'error')
                        return render_template('auth/profile.html')
                    updates['email'] = email
            
            if 'theme' in request.form:
                theme = request.form.get('theme')
                if theme in ['light', 'dark']:
                    updates['theme'] = theme
            
            if 'language' in request.form:
                language = request.form.get('language')
                if language in ['en', 'zh', 'es', 'fr', 'de']:
                    updates['language'] = language
            
            if 'timezone' in request.form:
                timezone = request.form.get('timezone')
                if timezone:
                    updates['timezone'] = timezone
            
            # Update user
            if updates:
                user_manager.update_user(current_user.id, **updates)
                flash('Profile updated successfully.', 'success')
            
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'error')
        
        return redirect(url_for('auth.profile'))
    
    # Get user statistics
    user_manager = UserManager()
    user_stats = user_manager.get_user_stats(current_user.id)
    permissions = get_user_permissions(current_user)
    
    return render_template('auth/profile.html', 
                         user_stats=user_stats,
                         permissions=permissions)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([current_password, new_password, confirm_password]):
            flash('All password fields are required.', 'error')
            return render_template('auth/change_password.html')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'error')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return render_template('auth/change_password.html')
        
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('auth/change_password.html')
        
        try:
            # Update password
            current_user.set_password(new_password)
            from app import db
            db.session.commit()
            
            flash('Password changed successfully.', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            flash(f'Error changing password: {str(e)}', 'error')
    
    return render_template('auth/change_password.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration (if enabled)"""
    # For now, only admins can create users
    # This route can be enabled later if self-registration is needed
    flash('Registration is currently disabled. Please contact an administrator.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/api/check-username')
def check_username():
    """Check if username is available (AJAX)"""
    username = request.args.get('username', '').strip()
    
    if not username:
        return jsonify({'available': False, 'message': 'Username is required'})
    
    if len(username) < 3:
        return jsonify({'available': False, 'message': 'Username must be at least 3 characters'})
    
    user_manager = UserManager()
    existing_user = user_manager.get_user_by_username(username)
    
    if existing_user:
        return jsonify({'available': False, 'message': 'Username is already taken'})
    
    return jsonify({'available': True, 'message': 'Username is available'})

@auth_bp.route('/api/check-email')
def check_email():
    """Check if email is available (AJAX)"""
    email = request.args.get('email', '').strip()
    
    if not email:
        return jsonify({'available': False, 'message': 'Email is required'})
    
    # Basic email validation
    if '@' not in email or '.' not in email:
        return jsonify({'available': False, 'message': 'Invalid email format'})
    
    user_manager = UserManager()
    existing_user = user_manager.get_user_by_email(email)
    
    if existing_user and existing_user.id != current_user.id:
        return jsonify({'available': False, 'message': 'Email is already registered'})
    
    return jsonify({'available': True, 'message': 'Email is available'})

@auth_bp.route('/api/user-info')
@login_required
def user_info():
    """Get current user information (AJAX)"""
    user_manager = UserManager()
    user_stats = user_manager.get_user_stats(current_user.id)
    permissions = get_user_permissions(current_user)
    
    return jsonify({
        'user': current_user.to_dict(),
        'stats': user_stats,
        'permissions': permissions
    }) 