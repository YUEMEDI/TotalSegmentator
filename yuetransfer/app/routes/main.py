"""
YueTransfer Main Routes
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

from app.models.user import UserManager
from app.utils.file_manager import FileManager
from app.utils.stats import get_user_stats, get_system_stats

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    """Main dashboard page"""
    try:
        # Get user statistics
        stats = get_user_stats(current_user.id)
        
        # Get recent files
        file_manager = FileManager(current_user.username)
        recent_files = file_manager.get_recent_files(limit=10)
        
        # Get system statistics
        system_stats = get_system_stats()
        
        return render_template('dashboard.html', 
                             stats=stats,
                             recent_files=recent_files,
                             system_stats=system_stats)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', 
                             stats={},
                             recent_files=[],
                             system_stats={})

@main_bp.route('/files')
@login_required
def file_browser():
    """File browser page"""
    try:
        path = request.args.get('path', '')
        file_manager = FileManager(current_user.username)
        
        # Get files and directories
        files = file_manager.list_files(path)
        
        # Get breadcrumb navigation
        breadcrumbs = file_manager.get_breadcrumbs(path)
        
        return render_template('file_browser.html',
                             files=files,
                             current_path=path,
                             breadcrumbs=breadcrumbs)
    except Exception as e:
        flash(f'Error loading file browser: {str(e)}', 'error')
        return render_template('file_browser.html',
                             files=[],
                             current_path='',
                             breadcrumbs=[])

@main_bp.route('/upload')
@login_required
def upload():
    """File upload page"""
    try:
        # Get user storage info
        user_stats = get_user_stats(current_user.id)
        
        return render_template('upload.html', user_stats=user_stats)
    except Exception as e:
        flash(f'Error loading upload page: {str(e)}', 'error')
        return render_template('upload.html', user_stats={})

@main_bp.route('/sftp-info')
@login_required
def sftp_info():
    """SFTP connection information page"""
    try:
        from app.config import Config
        config = Config()
        
        sftp_info = {
            'host': config.SFTP_HOST,
            'port': config.SFTP_PORT,
            'username': current_user.username,
            'protocol': 'SFTP (SSH File Transfer Protocol)'
        }
        
        return render_template('sftp_info.html', sftp_info=sftp_info)
    except Exception as e:
        flash(f'Error loading SFTP info: {str(e)}', 'error')
        return render_template('sftp_info.html', sftp_info={})

@main_bp.route('/process-files')
@login_required
def process_files():
    """File processing page for TotalSegmentator integration"""
    try:
        file_manager = FileManager(current_user.username)
        
        # Get files that can be processed
        processable_files = file_manager.get_processable_files()
        
        # Get processing history
        processing_history = file_manager.get_processing_history()
        
        return render_template('process_files.html',
                             processable_files=processable_files,
                             processing_history=processing_history)
    except Exception as e:
        flash(f'Error loading process files page: {str(e)}', 'error')
        return render_template('process_files.html',
                             processable_files=[],
                             processing_history=[])

@main_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    try:
        user_manager = UserManager()
        user_data = current_user.to_dict()
        
        return render_template('profile.html', user=user_data)
    except Exception as e:
        flash(f'Error loading profile: {str(e)}', 'error')
        return render_template('profile.html', user={})

@main_bp.route('/results')
@login_required
def results():
    """Processing results page"""
    try:
        file_manager = FileManager(current_user.username)
        
        # Get processing results
        results = file_manager.get_processing_results()
        
        return render_template('results.html', results=results)
    except Exception as e:
        flash(f'Error loading results: {str(e)}', 'error')
        return render_template('results.html', results=[])

# API Routes
@main_bp.route('/api/stats')
@login_required
def api_stats():
    """Get user statistics"""
    try:
        stats = get_user_stats(current_user.id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/files')
@login_required
def api_files():
    """Get file list for AJAX requests"""
    try:
        path = request.args.get('path', '')
        file_manager = FileManager(current_user.username)
        files = file_manager.list_files(path)
        
        return render_template('partials/file_list.html', files=files, current_path=path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/file-tree')
@login_required
def api_file_tree():
    """Get file tree for dashboard"""
    try:
        file_manager = FileManager(current_user.username)
        file_tree = file_manager.get_file_tree(depth=3)
        
        return render_template('partials/file_tree.html', file_tree=file_tree)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/upload', methods=['POST'])
@login_required
def api_upload():
    """Handle file upload"""
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files[]')
        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': 'No files selected'}), 400
        
        file_manager = FileManager(current_user.username)
        uploaded_files = []
        
        for file in files:
            if file and file.filename:
                try:
                    # Check file size
                    file.seek(0, 2)  # Seek to end
                    file_size = file.tell()
                    file.seek(0)  # Reset to beginning
                    
                    if not current_user.can_upload_file(file_size):
                        return jsonify({'error': f'Storage quota exceeded for file {file.filename}'}), 400
                    
                    # Upload file
                    result = file_manager.upload_file(file)
                    uploaded_files.append(result)
                    
                    # Update user storage usage
                    current_user.add_storage_usage(file_size)
                    
                except Exception as e:
                    return jsonify({'error': f'Failed to upload {file.filename}: {str(e)}'}), 500
        
        return jsonify({
            'message': f'Successfully uploaded {len(uploaded_files)} files',
            'files': uploaded_files
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/delete-files', methods=['DELETE'])
@login_required
def api_delete_files():
    """Delete selected files"""
    try:
        data = request.get_json()
        if not data or 'files' not in data:
            return jsonify({'error': 'No files specified'}), 400
        
        file_manager = FileManager(current_user.username)
        deleted_files = []
        
        for file_path in data['files']:
            try:
                file_size = file_manager.get_file_size(file_path)
                file_manager.delete_file(file_path)
                deleted_files.append(file_path)
                
                # Update user storage usage
                if file_size:
                    current_user.remove_storage_usage(file_size)
                    
            except Exception as e:
                return jsonify({'error': f'Failed to delete {file_path}: {str(e)}'}), 500
        
        return jsonify({
            'message': f'Successfully deleted {len(deleted_files)} files',
            'deleted_files': deleted_files
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/process-files', methods=['POST'])
@login_required
def api_process_files():
    """Send files to TotalSegmentator for processing"""
    try:
        data = request.get_json()
        if not data or 'files' not in data:
            return jsonify({'error': 'No files specified'}), 400
        
        file_manager = FileManager(current_user.username)
        
        # Move files to processing directory
        processed_files = []
        for file_path in data['files']:
            try:
                result = file_manager.move_to_processing(file_path)
                processed_files.append(result)
            except Exception as e:
                return jsonify({'error': f'Failed to process {file_path}: {str(e)}'}), 500
        
        # Start TotalSegmentator processing (background task)
        try:
            from app.utils.totalsegmentator import start_processing
            job_id = start_processing(current_user.username, processed_files)
            
            return jsonify({
                'message': f'Started processing {len(processed_files)} files',
                'job_id': job_id,
                'processed_files': processed_files
            })
            
        except Exception as e:
            return jsonify({'error': f'Failed to start processing: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/download/<path:file_path>')
@login_required
def api_download(file_path):
    """Download a file"""
    try:
        file_manager = FileManager(current_user.username)
        return file_manager.download_file(file_path)
    except Exception as e:
        flash(f'Download failed: {str(e)}', 'error')
        return redirect(url_for('main.file_browser'))

@main_bp.route('/api/preview/<path:file_path>')
@login_required
def api_preview(file_path):
    """Preview a file (if supported)"""
    try:
        file_manager = FileManager(current_user.username)
        return file_manager.preview_file(file_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/create-folder', methods=['POST'])
@login_required
def api_create_folder():
    """Create a new folder"""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Folder name required'}), 400
        
        folder_name = data['name']
        current_path = data.get('path', '')
        
        file_manager = FileManager(current_user.username)
        result = file_manager.create_folder(folder_name, current_path)
        
        return jsonify({
            'message': f'Folder "{folder_name}" created successfully',
            'folder': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/rename', methods=['POST'])
@login_required
def api_rename():
    """Rename a file or folder"""
    try:
        data = request.get_json()
        if not data or 'old_name' not in data or 'new_name' not in data:
            return jsonify({'error': 'Old and new names required'}), 400
        
        old_name = data['old_name']
        new_name = data['new_name']
        current_path = data.get('path', '')
        
        file_manager = FileManager(current_user.username)
        result = file_manager.rename_file(old_name, new_name, current_path)
        
        return jsonify({
            'message': f'Renamed "{old_name}" to "{new_name}"',
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/copy', methods=['POST'])
@login_required
def api_copy():
    """Copy files"""
    try:
        data = request.get_json()
        if not data or 'files' not in data or 'destination' not in data:
            return jsonify({'error': 'Files and destination required'}), 400
        
        files = data['files']
        destination = data['destination']
        
        file_manager = FileManager(current_user.username)
        copied_files = []
        
        for file_path in files:
            try:
                result = file_manager.copy_file(file_path, destination)
                copied_files.append(result)
            except Exception as e:
                return jsonify({'error': f'Failed to copy {file_path}: {str(e)}'}), 500
        
        return jsonify({
            'message': f'Successfully copied {len(copied_files)} files',
            'copied_files': copied_files
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/move', methods=['POST'])
@login_required
def api_move():
    """Move files"""
    try:
        data = request.get_json()
        if not data or 'files' not in data or 'destination' not in data:
            return jsonify({'error': 'Files and destination required'}), 400
        
        files = data['files']
        destination = data['destination']
        
        file_manager = FileManager(current_user.username)
        moved_files = []
        
        for file_path in files:
            try:
                result = file_manager.move_file(file_path, destination)
                moved_files.append(result)
            except Exception as e:
                return jsonify({'error': f'Failed to move {file_path}: {str(e)}'}), 500
        
        return jsonify({
            'message': f'Successfully moved {len(moved_files)} files',
            'moved_files': moved_files
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 