#!/usr/bin/env python3
"""
YUEUPLOAD - Upload Routes
"""

from flask import Blueprint, request, jsonify, current_app, render_template
import os
import uuid
import gc
import psutil
from pathlib import Path
from werkzeug.utils import secure_filename
import time

upload_bp = Blueprint('upload', __name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', set())
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def is_dicom_file(filename):
    """Check if file is likely a DICOM file"""
    # DICOM files can have various extensions or no extension
    dicom_extensions = {'dcm', 'dicom', 'DCM', 'DICOM', ''}
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return file_ext in dicom_extensions

def log_memory_usage():
    """Log current memory usage"""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)
        current_app.logger.info(f"Memory usage: {memory_mb:.2f} MB")
        return memory_mb
    except Exception as e:
        current_app.logger.warning(f"Could not get memory usage: {e}")
        return 0

@upload_bp.route('/')
def upload_index():
    """Upload interface"""
    return render_template('upload/index.html')

@upload_bp.route('/test')
def test_upload():
    """Test endpoint to verify server is working"""
    memory_mb = log_memory_usage()
    return jsonify({
        'status': 'success',
        'message': 'Upload server is working',
        'timestamp': time.time(),
        'memory_usage_mb': memory_mb
    })

@upload_bp.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    start_time = time.time()
    initial_memory = log_memory_usage()
    
    # Add CORS headers
    response_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
    }
    
    try:
        current_app.logger.info("Upload request received")
        
        # Check if files were uploaded
        if 'files' not in request.files:
            current_app.logger.error("No files in request")
            return jsonify({'error': 'No files provided'}), 400, response_headers
        
        files = request.files.getlist('files')
        current_app.logger.info(f"Found {len(files)} files in request")
        
        if not files or files[0].filename == '':
            current_app.logger.error("No files selected")
            return jsonify({'error': 'No files selected'}), 400
        
        # Check total upload size
        total_size = 0
        for file in files:
            if file and file.filename:
                # Get file size from content length header if available
                content_length = request.content_length
                if content_length:
                    total_size = content_length
                    break
                # Otherwise estimate from individual files
                file.seek(0, 2)  # Seek to end
                total_size += file.tell()
                file.seek(0)  # Reset to beginning
        
        current_app.logger.info(f"Total upload size: {total_size} bytes ({total_size / (1024**3):.2f} GB)")
        
        # Check if total size exceeds limit
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 50 * 1024**3)
        if total_size > max_size:
            current_app.logger.error(f"Upload size {total_size} exceeds limit {max_size}")
            return jsonify({'error': f'Upload size too large. Maximum allowed: {max_size / (1024**3):.1f} GB'}), 413
        
        uploaded_files = []
        errors = []
        
        # Get upload directory from config
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        temp_folder = current_app.config.get('TEMP_FOLDER', os.path.join(upload_folder, 'temp'))
        
        # Create base upload directory
        upload_dir = Path(temp_folder)
        current_app.logger.info(f"Creating upload directory: {upload_dir}")
        
        try:
            upload_dir.mkdir(parents=True, exist_ok=True)
            current_app.logger.info(f"Upload directory created/verified: {upload_dir}")
        except Exception as dir_error:
            current_app.logger.error(f"Failed to create upload directory: {str(dir_error)}")
            return jsonify({'error': f'Failed to create upload directory: {str(dir_error)}'}), 500
        
        # Process files in batches to avoid memory issues
        batch_size = 25  # Reduced batch size for better memory management
        for batch_start in range(0, len(files), batch_size):
            batch_end = min(batch_start + batch_size, len(files))
            batch_files = files[batch_start:batch_end]
            
            current_app.logger.info(f"Processing batch {batch_start//batch_size + 1}: files {batch_start+1}-{batch_end}")
            batch_memory = log_memory_usage()
            
            for i, file in enumerate(batch_files):
                if file and file.filename:
                    try:
                        original_filename = file.filename
                        current_app.logger.info(f"Processing file {batch_start + i + 1}/{len(files)}: {original_filename}")
                        
                        # Extract just the filename (without path) for saving
                        filename_only = original_filename.split('/')[-1] if '/' in original_filename else original_filename
                        filename_only = filename_only.split('\\')[-1] if '\\' in filename_only else filename_only
                        
                        # Extract folder structure from webkitRelativePath using the full path as key
                        relative_path = request.form.get(f'path_{original_filename}', '')
                        if not relative_path:
                            # Fallback to filename-only lookup for single files
                            relative_path = request.form.get(f'path_{filename_only}', '')
                        if not relative_path:
                            # Try to get from headers or other sources
                            relative_path = request.headers.get(f'X-Relative-Path-{i}', '')
                        
                        # Debug logging to see what we're getting
                        current_app.logger.info(f"DEBUG: File {original_filename} - filename_only: '{filename_only}' - relative_path: '{relative_path}'")
                        current_app.logger.info(f"DEBUG: Available form keys: {list(request.form.keys())}")
                        
                        # Determine file path and create directories if needed
                        if relative_path:
                            # Clean the relative path
                            relative_path = relative_path.replace('\\', '/').strip('/')
                            path_parts = relative_path.split('/')
                            
                            current_app.logger.info(f"DEBUG: path_parts: {path_parts}")
                            
                            if len(path_parts) > 1:
                                # Create folder structure (sanitize folder names for security)
                                folder_parts = [secure_filename(part) for part in path_parts[:-1]]
                                folder_path = upload_dir
                                for folder in folder_parts:
                                    folder_path = folder_path / folder
                                
                                current_app.logger.info(f"DEBUG: About to create folder: {folder_path}")
                                
                                # Create directories BEFORE trying to save the file
                                try:
                                    folder_path.mkdir(parents=True, exist_ok=True)
                                    current_app.logger.info(f"Created folder structure: {folder_path}")
                                except Exception as dir_error:
                                    current_app.logger.error(f"Failed to create directory {folder_path}: {str(dir_error)}")
                                    raise Exception(f"Failed to create directory: {str(dir_error)}")
                                
                                # Save file with original filename in the correct folder
                                file_path = folder_path / filename_only
                                current_app.logger.info(f"DEBUG: Constructed file_path: {file_path}")
                            else:
                                # Single file (no folder structure), save in root with original filename
                                file_path = upload_dir / filename_only
                        else:
                            # No relative path info, save in root with original filename
                            file_path = upload_dir / filename_only
                        
                        # Check if file already exists and handle conflicts
                        if file_path.exists():
                            # Add a number suffix to avoid conflicts
                            counter = 1
                            name_parts = filename_only.rsplit('.', 1)
                            base_name = name_parts[0]
                            extension = '.' + name_parts[1] if len(name_parts) > 1 else ''
                            
                            while file_path.exists():
                                new_filename = f"{base_name}_{counter}{extension}"
                                file_path = file_path.parent / new_filename
                                counter += 1
                        
                        current_app.logger.info(f"Saving file to: {file_path}")
                        
                        # Use streaming save for large files
                        file.save(str(file_path))
                        current_app.logger.info(f"File saved successfully: {file_path}")
                        
                        # Check if it's a DICOM file
                        is_dicom = is_dicom_file(original_filename)
                        
                        # Calculate relative path for display
                        display_path = str(file_path.relative_to(upload_dir))
                        
                        uploaded_files.append({
                            'original_name': original_filename,
                            'saved_name': file_path.name,
                            'file_path': str(file_path),
                            'relative_path': display_path,
                            'file_size': file_path.stat().st_size,
                            'is_dicom': is_dicom,
                            'upload_time': time.time()
                        })
                        
                        current_app.logger.info(f"Successfully uploaded: {original_filename} -> {display_path}")
                        
                    except Exception as file_error:
                        current_app.logger.error(f"Error uploading file {file.filename}: {str(file_error)}")
                        errors.append(f"Failed to upload {file.filename}: {str(file_error)}")
            
            # Force garbage collection after each batch
            gc.collect()
            current_app.logger.info(f"Batch {batch_start//batch_size + 1} completed. Memory: {log_memory_usage():.2f} MB")
        
        final_memory = log_memory_usage()
        elapsed_time = time.time() - start_time
        
        current_app.logger.info(f"Upload completed in {elapsed_time:.2f}s. Success: {len(uploaded_files)}, Errors: {len(errors)}")
        current_app.logger.info(f"Memory: {initial_memory:.2f} MB -> {final_memory:.2f} MB (change: {final_memory - initial_memory:+.2f} MB)")
        
        return jsonify({
            'success': True,
            'uploaded_files': uploaded_files,
            'errors': errors,
            'total_files': len(files),
            'successful_uploads': len(uploaded_files),
            'failed_uploads': len(errors),
            'upload_time_seconds': elapsed_time,
            'memory_usage_mb': final_memory
        }), 200, response_headers
        
    except Exception as e:
        final_memory = log_memory_usage()
        elapsed_time = time.time() - start_time
        current_app.logger.error(f"Upload error after {elapsed_time:.2f}s: {str(e)}")
        current_app.logger.error(f"Memory usage: {final_memory:.2f} MB")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500, response_headers

@upload_bp.route('/api/upload', methods=['OPTIONS'])
def upload_options():
    """Handle CORS preflight requests"""
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@upload_bp.route('/api/progress/<task_id>')
def get_progress(task_id):
    """Get upload progress"""
    # This will be implemented with background tasks
    return jsonify({
        'task_id': task_id,
        'progress': 100,
        'status': 'completed'
    })

@upload_bp.route('/api/preview/<filename>')
def get_preview(filename):
    """Get DICOM preview"""
    # This will be implemented in Sprint 1 Day 3-4
    return jsonify({'preview_url': f'/static/previews/{filename}.png'})

@upload_bp.route('/api/metadata/<filename>')
def get_metadata(filename):
    """Get DICOM metadata"""
    # This will be implemented in Sprint 1 Day 3-4
    return jsonify({'metadata': {}})