#!/usr/bin/env python3
"""
YUEUPLOAD - Main Routes
"""

from flask import Blueprint, render_template, request, jsonify, current_app
import os
from pathlib import Path

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main YUEUPLOAD interface"""
    return render_template('main/index.html')

@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'YUEUPLOAD',
        'version': '1.0.0'
    })

@main_bp.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'operational',
        'service': 'YUEUPLOAD',
        'version': '1.0.0',
        'upload_folder': current_app.config.get('UPLOAD_FOLDER', 'Not set'),
        'max_file_size': current_app.config.get('MAX_CONTENT_LENGTH', 0) // (1024**3),
        'debug_mode': current_app.config.get('DEBUG', False)
    })