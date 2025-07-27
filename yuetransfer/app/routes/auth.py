"""
YueTransfer Authentication Routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
import logging

from app.models.user import UserManager, get_user_by_id
from app import login_manager

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return get_user_by_id(user_id)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('auth/login.html')
        
        try:
            user_manager = UserManager()
            user = user_manager.authenticate_user(username, password)
            
            if user:
                login_user(user, remember=remember)
                flash(f'Welcome back, {user.username}!', 'success')
                
                # Redirect to intended page or dashboard
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('main.dashboard'))
            else:
                flash('Invalid username or password', 'error')
                
        except Exception as e:
            logging.error(f"Login error: {e}")
            flash('An error occurred during login', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('auth/register.html')
        
        try:
            user_manager = UserManager()
            user = user_manager.create_user(username=username, password=password, email=email)
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            logging.error(f"Registration error: {e}")
            flash('An error occurred during registration', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    if request.method == 'POST':
        email = request.form.get('email')
        theme = request.form.get('theme', 'light')
        language = request.form.get('language', 'en')
        timezone = request.form.get('timezone', 'UTC')
        
        try:
            user_manager = UserManager()
            user_manager.update_user(
                current_user.id,
                email=email,
                theme=theme,
                language=language,
                timezone=timezone
            )
            
            flash('Profile updated successfully', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            flash(f'Failed to update profile: {str(e)}', 'error')
    
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not current_password or not new_password:
            flash('All password fields are required', 'error')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('auth/change_password.html')
        
        if len(new_password) < 8:
            flash('New password must be at least 8 characters long', 'error')
            return render_template('auth/change_password.html')
        
        try:
            user_manager = UserManager()
            user_manager.change_password(
                current_user.id,
                current_password,
                new_password
            )
            
            flash('Password changed successfully', 'success')
            return redirect(url_for('auth.profile'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Failed to change password: {str(e)}', 'error')
    
    return render_template('auth/change_password.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Please enter your email address', 'error')
            return render_template('auth/forgot_password.html')
        
        try:
            user_manager = UserManager()
            user = user_manager.get_user_by_email(email)
            
            if user:
                # In a real application, you would send a password reset email here
                # For now, we'll just show a message
                flash('If an account with that email exists, a password reset link has been sent.', 'info')
            else:
                # Don't reveal if email exists or not for security
                flash('If an account with that email exists, a password reset link has been sent.', 'info')
            
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # In a real application, you would validate the token here
    # For now, we'll just show the form
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password:
            flash('New password is required', 'error')
            return render_template('auth/reset_password.html')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/reset_password.html')
        
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('auth/reset_password.html')
        
        try:
            # In a real application, you would update the user's password here
            flash('Password has been reset successfully. Please log in with your new password.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            flash('An error occurred while resetting the password', 'error')
    
    return render_template('auth/reset_password.html')

# Admin-only routes
@auth_bp.route('/admin/users')
@login_required
def admin_users():
    """Admin: List all users"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        user_manager = UserManager()
        users = user_manager.get_all_users(include_inactive=True)
        stats = user_manager.get_user_stats()
        
        return render_template('admin/users.html', users=users, stats=stats)
    except Exception as e:
        flash(f'Error loading users: {str(e)}', 'error')
        return render_template('admin/users.html', users=[], stats={})

@auth_bp.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
def admin_create_user():
    """Admin: Create new user"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin', False) == 'on'
        storage_quota = request.form.get('storage_quota', 107374182400)  # 100GB default
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('admin/create_user.html')
        
        try:
            user_manager = UserManager()
            user = user_manager.create_user(
                username=username,
                password=password,
                email=email,
                is_admin=is_admin
            )
            
            # Update storage quota
            user_manager.update_user(user.id, storage_quota=int(storage_quota))
            
            flash(f'User "{username}" created successfully', 'success')
            return redirect(url_for('auth.admin_users'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Failed to create user: {str(e)}', 'error')
    
    return render_template('admin/create_user.html')

@auth_bp.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    """Admin: Edit user"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        user_manager = UserManager()
        user = user_manager.get_user_by_id(user_id)
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth.admin_users'))
        
        if request.method == 'POST':
            email = request.form.get('email')
            is_admin = request.form.get('is_admin', False) == 'on'
            is_active = request.form.get('is_active', False) == 'on'
            storage_quota = request.form.get('storage_quota', user.storage_quota)
            
            user_manager.update_user(
                user.id,
                email=email,
                storage_quota=int(storage_quota)
            )
            
            # Update boolean fields
            user.is_admin = is_admin
            user.is_active = is_active
            user_manager.db.session.commit()
            
            flash(f'User "{user.username}" updated successfully', 'success')
            return redirect(url_for('auth.admin_users'))
        
        return render_template('admin/edit_user.html', user=user)
        
    except Exception as e:
        flash(f'Error editing user: {str(e)}', 'error')
        return redirect(url_for('auth.admin_users'))

@auth_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    """Admin: Delete user"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        user_manager = UserManager()
        user = user_manager.get_user_by_id(user_id)
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth.admin_users'))
        
        if user.id == current_user.id:
            flash('You cannot delete your own account', 'error')
            return redirect(url_for('auth.admin_users'))
        
        username = user.username
        user_manager.delete_user(user.id)
        
        flash(f'User "{username}" deleted successfully', 'success')
        return redirect(url_for('auth.admin_users'))
        
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'error')
        return redirect(url_for('auth.admin_users'))

@auth_bp.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
def admin_reset_user_password(user_id):
    """Admin: Reset user password"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        new_password = request.form.get('new_password')
        
        if not new_password or len(new_password) < 8:
            flash('New password must be at least 8 characters long', 'error')
            return redirect(url_for('auth.admin_edit_user', user_id=user_id))
        
        user_manager = UserManager()
        user = user_manager.get_user_by_id(user_id)
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth.admin_users'))
        
        user.set_password(new_password)
        user_manager.db.session.commit()
        
        flash(f'Password for user "{user.username}" has been reset', 'success')
        return redirect(url_for('auth.admin_edit_user', user_id=user_id))
        
    except Exception as e:
        flash(f'Error resetting password: {str(e)}', 'error')
        return redirect(url_for('auth.admin_users')) 