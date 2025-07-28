"""
YueTransfer Main Routes
"""

import os
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.models.user import UserManager, ProcessingJob
from app.utils.auth import get_user_permissions
from app.utils.file_manager import FileManager, get_file_stats, get_recent_files
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    try:
        # Get user statistics
        user_manager = UserManager()
        user_stats = user_manager.get_user_stats(current_user.id)
        
        # Get recent files
        recent_files = get_recent_files(current_user.get_upload_path(), limit=5)
        
        # Format stats for display
        if user_stats:
            user_stats['storage_used'] = format_file_size(user_stats['storage_used'])
            user_stats['storage_quota'] = format_file_size(user_stats['storage_quota'])
        
        # Get processing jobs
        processing_jobs = ProcessingJob.query.filter_by(user_id=current_user.id).filter(
            ProcessingJob.status.in_(['pending', 'processing'])
        ).count()
        
        user_stats['processing_jobs'] = processing_jobs
        
        return render_template('main/dashboard.html', 
                             stats=user_stats,
                             recent_files=recent_files,
                             config=current_app.config)
    
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('main/dashboard.html', 
                             stats={}, 
                             recent_files=[],
                             config=current_app.config)

@main_bp.route('/files')
@main_bp.route('/files/<path:path>')
@login_required
def file_browser(path=''):
    """File browser interface"""
    try:
        file_manager = FileManager(current_user.username)
        
        # Get current directory contents
        current_path = os.path.join(current_user.get_upload_path(), path) if path else current_user.get_upload_path()
        
        if not os.path.exists(current_path) or not current_path.startswith(current_user.get_upload_path()):
            flash('Directory not found or access denied.', 'error')
            return redirect(url_for('main.file_browser'))
        
        # Get directory contents
        contents = file_manager.list_directory(current_path)
        breadcrumbs = _get_breadcrumbs(path)
        
        return render_template('main/file_browser.html',
                             contents=contents,
                             current_path=path,
                             breadcrumbs=breadcrumbs)
    
    except Exception as e:
        flash(f'Error browsing files: {str(e)}', 'error')
        return render_template('main/file_browser.html',
                             contents=[],
                             current_path='',
                             breadcrumbs=[])

@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """File upload interface"""
    if request.method == 'POST':
        try:
            # Handle file uploads
            uploaded_files = request.files.getlist('files[]')
            
            if not uploaded_files or not uploaded_files[0].filename:
                flash('No files selected for upload.', 'error')
                return redirect(url_for('main.upload'))
            
            file_manager = FileManager(current_user.username)
            upload_results = []
            
            for file in uploaded_files:
                if file.filename:
                    try:
                        result = file_manager.save_uploaded_file(file)
                        upload_results.append(result)
                    except Exception as e:
                        flash(f'Error uploading {file.filename}: {str(e)}', 'error')
            
            if upload_results:
                flash(f'Successfully uploaded {len(upload_results)} file(s).', 'success')
                return redirect(url_for('main.file_browser'))
        
        except Exception as e:
            flash(f'Upload error: {str(e)}', 'error')
    
    # Get user storage info
    user_manager = UserManager()
    user_stats = user_manager.get_user_stats(current_user.id)
    
    return render_template('main/upload.html', user_stats=user_stats)

@main_bp.route('/process-files')
@login_required
def process_files():
    """TotalSegmentator processing interface"""
    try:
        # Get user's files that can be processed
        file_manager = FileManager(current_user.username)
        processable_files = file_manager.get_processable_files()
        
        # Get processing jobs
        processing_jobs = ProcessingJob.query.filter_by(user_id=current_user.id).order_by(
            ProcessingJob.created_at.desc()
        ).limit(20).all()
        
        return render_template('main/process_files.html',
                             processable_files=processable_files,
                             processing_jobs=processing_jobs)
    
    except Exception as e:
        flash(f'Error loading processing interface: {str(e)}', 'error')
        return render_template('main/process_files.html',
                             processable_files=[],
                             processing_jobs=[])

@main_bp.route('/results')
@main_bp.route('/results/<path:path>')
@login_required
def results(path=''):
    """View processing results"""
    try:
        results_path = os.path.join(current_user.get_results_path(), path) if path else current_user.get_results_path()
        
        if not os.path.exists(results_path) or not results_path.startswith(current_user.get_results_path()):
            flash('Results directory not found or access denied.', 'error')
            return redirect(url_for('main.results'))
        
        file_manager = FileManager(current_user.username)
        contents = file_manager.list_directory(results_path)
        breadcrumbs = _get_breadcrumbs(path, base_url='main.results')
        
        return render_template('main/results.html',
                             contents=contents,
                             current_path=path,
                             breadcrumbs=breadcrumbs)
    
    except Exception as e:
        flash(f'Error browsing results: {str(e)}', 'error')
        return render_template('main/results.html',
                             contents=[],
                             current_path='',
                             breadcrumbs=[])

@main_bp.route('/sftp-info')
@login_required
def sftp_info():
    """SFTP connection information"""
    sftp_config = {
        'host': current_app.config.get('SFTP_HOST', 'localhost'),
        'port': current_app.config.get('SFTP_PORT', 2222),
        'username': current_user.username,
        'protocol': 'SFTP (SSH File Transfer Protocol)'
    }
    
    # Generate connection strings for different clients
    connection_strings = {
        'command_line': f'sftp -P {sftp_config["port"]} {sftp_config["username"]}@{sftp_config["host"]}',
        'filezilla': f'sftp://{sftp_config["username"]}@{sftp_config["host"]}:{sftp_config["port"]}',
        'winscp': f'{sftp_config["host"]}:{sftp_config["port"]}',
    }
    
    return render_template('main/sftp_info.html',
                         sftp_config=sftp_config,
                         connection_strings=connection_strings)

@main_bp.route('/download/<path:filepath>')
@login_required
def download_file(filepath):
    """Download a file"""
    try:
        # Construct full file path
        full_path = os.path.join(current_user.get_upload_path(), filepath)
        
        # Security check: ensure file is within user's directory
        if not full_path.startswith(current_user.get_upload_path()):
            flash('Access denied.', 'error')
            return redirect(url_for('main.file_browser'))
        
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            flash('File not found.', 'error')
            return redirect(url_for('main.file_browser'))
        
        return send_file(full_path, as_attachment=True)
    
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('main.file_browser'))

@main_bp.route('/download-results/<path:filepath>')
@login_required
def download_results(filepath):
    """Download a results file"""
    try:
        # Construct full file path
        full_path = os.path.join(current_user.get_results_path(), filepath)
        
        # Security check: ensure file is within user's results directory
        if not full_path.startswith(current_user.get_results_path()):
            flash('Access denied.', 'error')
            return redirect(url_for('main.results'))
        
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            flash('File not found.', 'error')
            return redirect(url_for('main.results'))
        
        return send_file(full_path, as_attachment=True)
    
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('main.results'))

@main_bp.route('/create-folder', methods=['POST'])
@login_required
def create_folder():
    """Create a new folder"""
    try:
        folder_name = request.form.get('folder_name', '').strip()
        current_path = request.form.get('current_path', '')
        
        if not folder_name:
            flash('Folder name is required.', 'error')
            return redirect(url_for('main.file_browser', path=current_path))
        
        # Sanitize folder name
        folder_name = secure_filename(folder_name)
        
        if not folder_name:
            flash('Invalid folder name.', 'error')
            return redirect(url_for('main.file_browser', path=current_path))
        
        # Create folder path
        base_path = os.path.join(current_user.get_upload_path(), current_path) if current_path else current_user.get_upload_path()
        new_folder_path = os.path.join(base_path, folder_name)
        
        # Security check
        if not new_folder_path.startswith(current_user.get_upload_path()):
            flash('Access denied.', 'error')
            return redirect(url_for('main.file_browser', path=current_path))
        
        if os.path.exists(new_folder_path):
            flash('Folder already exists.', 'error')
            return redirect(url_for('main.file_browser', path=current_path))
        
        os.makedirs(new_folder_path)
        flash(f'Folder "{folder_name}" created successfully.', 'success')
        
        return redirect(url_for('main.file_browser', path=current_path))
    
    except Exception as e:
        flash(f'Error creating folder: {str(e)}', 'error')
        return redirect(url_for('main.file_browser'))

# Utility functions
def _get_breadcrumbs(path, base_url='main.file_browser'):
    """Generate breadcrumb navigation"""
    breadcrumbs = [{'name': 'Home', 'path': '', 'url': url_for(base_url)}]
    
    if path:
        parts = path.split('/')
        current_path = ''
        
        for part in parts:
            if part:
                current_path = os.path.join(current_path, part).replace('\\', '/')
                breadcrumbs.append({
                    'name': part,
                    'path': current_path,
                    'url': url_for(base_url, path=current_path)
                })
    
    return breadcrumbs

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}" 