#!/usr/bin/env python3
"""
YUEUPLOAD - Flask Application Initialization
"""

from flask import Flask, render_template # render_template added for error handlers
from flask_cors import CORS
import os
from pathlib import Path

def create_app(config_name=None):
    """Create and configure the Flask application"""
    
    # Get configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Set up template and static folders
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Load configuration
    from config.settings import get_config
    app.config.from_object(get_config())
    
    # Configure for large file uploads
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 * 1024  # 50GB max
    app.config['MAX_CONTENT_PATH'] = None  # No path length limit
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for uploads
    
    # Enable CORS for development with more permissive settings
    if app.config.get('DEBUG', True):
        CORS(app, resources={
            r"/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
            }
        })
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register context processors
    register_context_processors(app)
    
    return app

def init_extensions(app):
    """Initialize Flask extensions"""
    # This will be implemented as we add extensions
    pass

def register_blueprints(app):
    """Register Flask blueprints"""
    from app.routes.upload import upload_bp
    from app.routes.main import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp, url_prefix='/upload')

def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

def register_context_processors(app):
    """Register context processors"""
    @app.context_processor
    def inject_config():
        """Inject configuration into templates"""
        return dict(
            app_name="YUEUPLOAD",
            app_version="1.0.0",
            max_file_size=app.config.get('MAX_CONTENT_LENGTH', 0) // (1024**3)
        )