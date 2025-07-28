"""
YueTransfer Flask Application Factory
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config=None):
    """Application factory pattern"""
    
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Load configuration
    if config:
        app.config.from_object(config)
    else:
        app.config.from_object('app.config.Config')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Initialize login manager with user loader
    from app.utils.auth import init_login_manager
    init_login_manager(login_manager)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        from app.models.user import User
        from app.utils.auth import create_default_admin
        
        if not User.query.filter_by(username='admin').first():
            create_default_admin()
    
    # Register error handlers
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # Register context processors
    from app.utils.context_processors import register_context_processors
    register_context_processors(app)
    
    return app 