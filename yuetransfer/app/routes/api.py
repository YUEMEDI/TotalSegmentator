"""
YueTransfer API Routes
Handles AJAX requests and API endpoints
"""

import os
import json
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.models.user import UserManager, ProcessingJob
from app.utils.file_manager import FileManager
from app.utils.totalsegmentator_integration import start_segmentation_job
from app import db

api_bp = Blueprint('api', __name__)

@api_bp.route('/stats')
@login_required
def get_stats():
    """Get user statistics for dashboard"""
    try:
        user_manager = UserManager()
        stats = user_manager.get_user_stats(current_user.id)
        
        # Format for JSON response
        if stats:
            stats['storage_used_formatted'] = format_file_size(stats['storage_used'])
            stats['storage_quota_formatted'] = format_file_size(stats['storage_quota'])
        
        return jsonify(stats or {})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/files')
@login_required
def get_files():
    """Get file list for AJAX requests"""
    try:
        path = request.args.get('path', '')
        file_manager = FileManager(current_user.username)
        
        # Get current directory
        current_path = os.path.join(current_user.get_upload_path(), path) if path else current_user.get_upload_path()
        
        if not os.path.exists(current_path) or not current_path.startswith(current_user.get_upload_path()):
            return jsonify({'error': 'Directory not found or access denied'}), 404
        
        contents = file_manager.list_directory(current_path)
        
        return jsonify({
            'contents': contents,
            'current_path': path
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/file-tree')
@login_required
def get_file_tree():
    """Get file tree structure for dashboard"""
    try:
        file_manager = FileManager(current_user.username)
        tree = file_manager.get_file_tree(max_depth=3)
        
        return jsonify(tree)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/upload', methods=['POST'])
@login_required
def upload_files():
    """Handle file upload via AJAX"""
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files[]')
        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': 'No files selected'}), 400
        
        file_manager = FileManager(current_user.username)
        uploaded_files = []
        total_size = 0
        
        # Check total size first
        for file in files:
            if file and file.filename:
                file.seek(0, 2)  # Seek to end
                file_size = file.tell()
                file.seek(0)  # Reset to beginning
                total_size += file_size
        
        # Check if user can upload all files
        if not current_user.can_upload_file(total_size):
            return jsonify({'error': 'Storage quota exceeded'}), 400
        
        # Upload files
        for file in files:
            if file and file.filename:
                try:
                    result = file_manager.save_uploaded_file(file)
                    uploaded_files.append(result)
                    
                    # Update user storage usage
                    current_user.add_storage_usage(result['size'])
                    
                except Exception as e:
                    return jsonify({'error': f'Failed to upload {file.filename}: {str(e)}'}), 500
        
        return jsonify({
            'message': f'Successfully uploaded {len(uploaded_files)} file(s)',
            'files': uploaded_files
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/delete-files', methods=['DELETE'])
@login_required
def delete_files():
    """Delete selected files"""
    try:
        data = request.get_json()
        if not data or 'files' not in data:
            return jsonify({'error': 'No files specified'}), 400
        
        file_manager = FileManager(current_user.username)
        deleted_files = []
        total_freed_space = 0
        
        for file_path in data['files']:
            try:
                full_path = os.path.join(current_user.get_upload_path(), file_path)
                
                # Security check
                if not full_path.startswith(current_user.get_upload_path()):
                    continue
                
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path) if os.path.isfile(full_path) else 0
                    
                    if os.path.isfile(full_path):
                        os.remove(full_path)
                    elif os.path.isdir(full_path):
                        import shutil
                        shutil.rmtree(full_path)
                    
                    deleted_files.append(file_path)
                    total_freed_space += file_size
                    
            except Exception as e:
                return jsonify({'error': f'Failed to delete {file_path}: {str(e)}'}), 500
        
        # Update user storage usage
        if total_freed_space > 0:
            current_user.remove_storage_usage(total_freed_space)
        
        return jsonify({
            'message': f'Successfully deleted {len(deleted_files)} item(s)',
            'deleted_files': deleted_files,
            'freed_space': format_file_size(total_freed_space)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/create-folder', methods=['POST'])
@login_required
def create_folder():
    """Create a new folder via AJAX"""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Folder name required'}), 400
        
        folder_name = secure_filename(data['name'].strip())
        current_path = data.get('path', '')
        
        if not folder_name:
            return jsonify({'error': 'Invalid folder name'}), 400
        
        # Create folder path
        base_path = os.path.join(current_user.get_upload_path(), current_path) if current_path else current_user.get_upload_path()
        new_folder_path = os.path.join(base_path, folder_name)
        
        # Security check
        if not new_folder_path.startswith(current_user.get_upload_path()):
            return jsonify({'error': 'Access denied'}), 403
        
        if os.path.exists(new_folder_path):
            return jsonify({'error': 'Folder already exists'}), 400
        
        os.makedirs(new_folder_path)
        
        return jsonify({
            'message': f'Folder "{folder_name}" created successfully',
            'folder_name': folder_name,
            'path': os.path.join(current_path, folder_name).replace('\\', '/') if current_path else folder_name
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/rename', methods=['POST'])
@login_required
def rename_item():
    """Rename a file or folder"""
    try:
        data = request.get_json()
        if not data or 'old_name' not in data or 'new_name' not in data:
            return jsonify({'error': 'Old and new names required'}), 400
        
        old_name = data['old_name']
        new_name = secure_filename(data['new_name'].strip())
        current_path = data.get('path', '')
        
        if not new_name:
            return jsonify({'error': 'Invalid new name'}), 400
        
        # Construct paths
        base_path = os.path.join(current_user.get_upload_path(), current_path) if current_path else current_user.get_upload_path()
        old_path = os.path.join(base_path, old_name)
        new_path = os.path.join(base_path, new_name)
        
        # Security checks
        if not old_path.startswith(current_user.get_upload_path()) or not new_path.startswith(current_user.get_upload_path()):
            return jsonify({'error': 'Access denied'}), 403
        
        if not os.path.exists(old_path):
            return jsonify({'error': 'Item not found'}), 404
        
        if os.path.exists(new_path):
            return jsonify({'error': 'An item with that name already exists'}), 400
        
        os.rename(old_path, new_path)
        
        return jsonify({
            'message': f'Renamed "{old_name}" to "{new_name}"',
            'old_name': old_name,
            'new_name': new_name
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/move', methods=['POST'])
@login_required
def move_items():
    """Move files or folders"""
    try:
        data = request.get_json()
        if not data or 'items' not in data or 'destination' not in data:
            return jsonify({'error': 'Items and destination required'}), 400
        
        items = data['items']
        destination = data['destination']
        
        destination_path = os.path.join(current_user.get_upload_path(), destination) if destination else current_user.get_upload_path()
        
        # Security check for destination
        if not destination_path.startswith(current_user.get_upload_path()):
            return jsonify({'error': 'Invalid destination'}), 403
        
        if not os.path.exists(destination_path) or not os.path.isdir(destination_path):
            return jsonify({'error': 'Destination directory not found'}), 404
        
        moved_items = []
        
        for item in items:
            try:
                # Construct source path
                source_path = os.path.join(current_user.get_upload_path(), item)
                
                # Security check for source
                if not source_path.startswith(current_user.get_upload_path()):
                    continue
                
                if not os.path.exists(source_path):
                    continue
                
                # Construct destination path
                item_name = os.path.basename(source_path)
                dest_item_path = os.path.join(destination_path, item_name)
                
                if os.path.exists(dest_item_path):
                    return jsonify({'error': f'Item "{item_name}" already exists in destination'}), 400
                
                import shutil
                shutil.move(source_path, dest_item_path)
                moved_items.append(item)
                
            except Exception as e:
                return jsonify({'error': f'Failed to move {item}: {str(e)}'}), 500
        
        return jsonify({
            'message': f'Successfully moved {len(moved_items)} item(s)',
            'moved_items': moved_items
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/process-files', methods=['POST'])
@login_required
def process_files():
    """Send files to TotalSegmentator for processing"""
    try:
        data = request.get_json()
        if not data or 'files' not in data:
            return jsonify({'error': 'No files specified'}), 400
        
        files = data['files']
        task = data.get('task', 'total')  # Default to 'total' task
        fast_mode = data.get('fast_mode', False)
        preview = data.get('preview', False)
        job_name = data.get('job_name', f'Segmentation_{len(files)}_files')
        
        # Validate files exist and are accessible
        valid_files = []
        for file_path in files:
            full_path = os.path.join(current_user.get_upload_path(), file_path)
            
            # Security check
            if not full_path.startswith(current_user.get_upload_path()):
                continue
            
            if os.path.exists(full_path) and os.path.isfile(full_path):
                # Check if file is a valid format for TotalSegmentator
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext in ['.nii', '.gz', '.dcm']:
                    valid_files.append(file_path)
        
        if not valid_files:
            return jsonify({'error': 'No valid files found for processing'}), 400
        
        # Create processing job
        job = ProcessingJob(
            user_id=current_user.id,
            job_name=job_name,
            input_files=json.dumps(valid_files),
            task=task,
            fast_mode=fast_mode,
            preview=preview,
            status='pending'
        )
        
        db.session.add(job)
        db.session.commit()
        
        # Start background processing
        try:
            job_started = start_segmentation_job(job.id)
            
            if job_started:
                return jsonify({
                    'message': f'Started processing {len(valid_files)} file(s)',
                    'job_id': job.id,
                    'job_name': job_name,
                    'files_count': len(valid_files)
                })
            else:
                job.status = 'failed'
                job.error_message = 'Failed to start background processing'
                db.session.commit()
                return jsonify({'error': 'Failed to start processing job'}), 500
                
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            db.session.commit()
            return jsonify({'error': f'Failed to start processing: {str(e)}'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/processing-jobs')
@login_required
def get_processing_jobs():
    """Get user's processing jobs"""
    try:
        jobs = ProcessingJob.query.filter_by(user_id=current_user.id).order_by(
            ProcessingJob.created_at.desc()
        ).limit(50).all()
        
        jobs_data = [job.to_dict() for job in jobs]
        
        return jsonify({
            'jobs': jobs_data,
            'total_jobs': len(jobs_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/processing-jobs/<int:job_id>')
@login_required
def get_processing_job(job_id):
    """Get specific processing job details"""
    try:
        job = ProcessingJob.query.filter_by(id=job_id, user_id=current_user.id).first()
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify(job.to_dict())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/processing-jobs/<int:job_id>/cancel', methods=['POST'])
@login_required
def cancel_processing_job(job_id):
    """Cancel a processing job"""
    try:
        job = ProcessingJob.query.filter_by(id=job_id, user_id=current_user.id).first()
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if job.status not in ['pending', 'processing']:
            return jsonify({'error': 'Job cannot be cancelled'}), 400
        
        # Update job status
        job.status = 'cancelled'
        db.session.commit()
        
        # TODO: Cancel actual background process if running
        
        return jsonify({
            'message': 'Job cancelled successfully',
            'job_id': job_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/search', methods=['GET'])
@login_required
def search_files():
    """Search files by name or type"""
    try:
        query = request.args.get('q', '').strip().lower()
        file_type = request.args.get('type', '').strip().lower()
        
        if not query and not file_type:
            return jsonify({'error': 'Search query or file type required'}), 400
        
        file_manager = FileManager(current_user.username)
        results = file_manager.search_files(query, file_type)
        
        return jsonify({
            'results': results,
            'query': query,
            'file_type': file_type,
            'count': len(results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/storage-usage')
@login_required
def get_storage_usage():
    """Get detailed storage usage information"""
    try:
        user_manager = UserManager()
        
        # Recalculate storage usage
        current_usage = user_manager.calculate_storage_usage(current_user.id)
        
        # Get breakdown by file type
        file_manager = FileManager(current_user.username)
        usage_breakdown = file_manager.get_storage_breakdown()
        
        return jsonify({
            'current_usage': current_usage,
            'current_usage_formatted': format_file_size(current_usage),
            'quota': current_user.storage_quota,
            'quota_formatted': format_file_size(current_user.storage_quota),
            'usage_percentage': (current_usage / current_user.storage_quota) * 100 if current_user.storage_quota > 0 else 0,
            'breakdown': usage_breakdown
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Utility function
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