"""
YueTransfer Context Processors
Provides common template variables
"""

from flask import current_app
from flask_login import current_user
from datetime import datetime

def register_context_processors(app):
    """Register context processors for templates"""
    
    @app.context_processor
    def inject_config():
        """Inject configuration variables into templates"""
        return {
            'config': current_app.config,
            'app_name': 'YueTransfer',
            'app_version': '1.0.0'
        }
    
    @app.context_processor
    def inject_user_info():
        """Inject user information into templates"""
        if current_user.is_authenticated:
            from app.utils.auth import get_user_permissions
            return {
                'user_permissions': get_user_permissions(current_user)
            }
        return {}
    
    @app.context_processor
    def inject_utils():
        """Inject utility functions into templates"""
        def format_datetime(dt, format='%Y-%m-%d %H:%M'):
            """Format datetime for templates"""
            if dt:
                return dt.strftime(format)
            return ''
        
        def format_file_size(size_bytes):
            """Format file size for templates"""
            if size_bytes == 0:
                return "0 B"
            
            size_names = ["B", "KB", "MB", "GB", "TB"]
            import math
            i = int(math.floor(math.log(size_bytes, 1024)))
            p = math.pow(1024, i)
            s = round(size_bytes / p, 2)
            
            return f"{s} {size_names[i]}"
        
        def time_ago(dt):
            """Get time ago string for templates"""
            if not dt:
                return ''
            
            now = datetime.utcnow()
            diff = now - dt
            
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                return "Just now"
        
        return {
            'format_datetime': format_datetime,
            'format_file_size': format_file_size,
            'time_ago': time_ago,
            'now': datetime.utcnow()
        } 