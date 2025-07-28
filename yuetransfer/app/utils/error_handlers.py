"""
YueTransfer Error Handlers
Custom error pages and handlers
"""

from flask import render_template, request, jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'error': 'Resource not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors"""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'error': 'Access forbidden'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle file too large errors"""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'error': 'File too large'}), 413
        return render_template('errors/413.html'), 413
    
    @app.errorhandler(CSRFError)
    def csrf_error(error):
        """Handle CSRF errors"""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'error': 'CSRF token missing or invalid'}), 400
        return render_template('errors/csrf.html'), 400
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle uncaught exceptions"""
        # Log the error
        app.logger.error(f'Unhandled exception: {error}', exc_info=True)
        
        # Return appropriate response
        if isinstance(error, HTTPException):
            return error
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        
        return render_template('errors/500.html'), 500

# Import CSRFError if available
try:
    from flask_wtf.csrf import CSRFError
except ImportError:
    class CSRFError(Exception):
        pass 