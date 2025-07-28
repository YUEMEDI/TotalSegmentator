"""
YueTransfer Authentication Utilities
"""

from flask_login import login_manager
from app.models.user import User, UserManager

def init_login_manager(login_manager):
    """Initialize login manager with user loader"""
    @login_manager.user_loader
    def load_user(user_id):
        """Load user for Flask-Login"""
        return User.query.get(int(user_id))

def create_default_admin():
    """Create default admin user if it doesn't exist"""
    try:
        user_manager = UserManager()
        
        # Check if admin user already exists
        admin_user = user_manager.get_user_by_username('admin')
        if admin_user:
            return admin_user
        
        # Create default admin user
        admin_user = user_manager.create_user(
            username='pokpok',
            password='pokpok',  # Should be changed immediately
            email='pokpok@yuetransfer.local',
            is_admin=True
        )
        
        print("✅ Default admin user created:")
        print(f"   Username: pokpok")
        print(f"   Password: pokpok")
        print(f"   ⚠️  Please change the password immediately!")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Failed to create default admin user: {e}")
        return None

def require_admin(f):
    """Decorator to require admin access"""
    from functools import wraps
    from flask_login import current_user
    from flask import abort
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def get_user_permissions(user):
    """Get user permissions"""
    permissions = {
        'can_upload': True,
        'can_download': True,
        'can_delete_own_files': True,
        'can_process_files': True,
        'can_view_admin': user.is_admin if user else False,
        'can_manage_users': user.is_admin if user else False,
        'can_view_all_files': user.is_admin if user else False
    }
    
    return permissions 