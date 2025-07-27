#!/usr/bin/env python3
"""
YueTransfer - Medical Imaging Transfer & Processing Platform
Main application entry point
"""

import os
import sys
import argparse
import logging
import threading
import signal
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app import create_app
from app.sftp_server import SFTPServer
from app.config import Config
from app.utils.logger import setup_logging

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\n🛑 Shutting down YueTransfer...")
    sys.exit(0)

def start_sftp_server(config):
    """Start the SFTP server in a separate thread"""
    try:
        sftp_server = SFTPServer(
            host=config.SFTP_HOST,
            port=config.SFTP_PORT,
            root_dir=config.UPLOAD_FOLDER
        )
        sftp_server.start()
    except Exception as e:
        logging.error(f"Failed to start SFTP server: {e}")
        raise

def start_web_server(config, debug=False):
    """Start the Flask web server"""
    try:
        app = create_app(config)
        
        if debug:
            app.run(
                host=config.WEB_HOST,
                port=config.WEB_PORT,
                debug=True,
                use_reloader=False  # Disable reloader when running with threads
            )
        else:
            # Use production WSGI server
            from waitress import serve
            serve(app, host=config.WEB_HOST, port=config.WEB_PORT)
            
    except Exception as e:
        logging.error(f"Failed to start web server: {e}")
        raise

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        "app/uploads",
        "app/results", 
        "app/logs",
        "app/static/uploads",
        "app/static/thumbnails",
        "users",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import paramiko
        import sqlalchemy
        print("✅ All core dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="YueTransfer - Medical Imaging Transfer Platform")
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    parser.add_argument("--production", action="store_true", help="Run in production mode")
    parser.add_argument("--port", type=int, default=8080, help="Web server port")
    parser.add_argument("--sftp-port", type=int, default=2222, help="SFTP server port")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--config", default="config/config.yaml", help="Configuration file path")
    
    args = parser.parse_args()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create necessary directories
    create_directories()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Load configuration
    try:
        config = Config()
        config.WEB_HOST = args.host
        config.WEB_PORT = args.port
        config.SFTP_HOST = args.host
        config.SFTP_PORT = args.sftp_port
        
        if args.dev:
            config.DEBUG = True
            config.ENV = "development"
        elif args.production:
            config.DEBUG = False
            config.ENV = "production"
            
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        sys.exit(1)
    
    # Setup logging
    setup_logging(config)
    
    # Print startup banner
    print("=" * 60)
    print("🎯 YueTransfer - Medical Imaging Transfer Platform")
    print("=" * 60)
    print(f"🌐 Web Interface: http://{config.WEB_HOST}:{config.WEB_PORT}")
    print(f"🔐 SFTP Server: {config.SFTP_HOST}:{config.SFTP_PORT}")
    print(f"📁 Upload Folder: {config.UPLOAD_FOLDER}")
    print(f"🔧 Environment: {config.ENV}")
    print("=" * 60)
    
    try:
        # Start SFTP server in a separate thread
        sftp_thread = threading.Thread(
            target=start_sftp_server,
            args=(config,),
            daemon=True
        )
        sftp_thread.start()
        print("✅ SFTP server started")
        
        # Start web server in main thread
        print("✅ Web server starting...")
        start_web_server(config, debug=config.DEBUG)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down YueTransfer...")
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"❌ Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 