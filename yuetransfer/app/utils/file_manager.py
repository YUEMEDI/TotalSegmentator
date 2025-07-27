"""
YueTransfer File Manager Utility
"""

import os
import shutil
import zipfile
import tarfile
import magic
import mimetypes
from datetime import datetime, timedelta
from pathlib import Path
from werkzeug.utils import secure_filename
import logging

from app.config import Config

class FileManager:
    """File management utility for user files"""
    
    def __init__(self, username):
        self.username = username
        self.config = Config()
        self.upload_path = self.config.get_upload_path(username)
        self.results_path = self.config.get_results_path(username)
        
        # Ensure user directories exist
        self._ensure_user_directories()
    
    def _ensure_user_directories(self):
        """Ensure user directories exist"""
        directories = [
            self.upload_path,
            self.results_path,
            os.path.join(self.upload_path, 'dicom_datasets'),
            os.path.join(self.upload_path, 'nifti_files'),
            os.path.join(self.upload_path, 'archives'),
            os.path.join(self.upload_path, 'selected_for_processing')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def upload_file(self, file):
        """Upload a file to user's directory"""
        try:
            filename = secure_filename(file.filename)
            if not filename:
                raise ValueError("Invalid filename")
            
            # Determine target directory based on file type
            target_dir = self._get_target_directory(filename)
            target_path = os.path.join(target_dir, filename)
            
            # Handle duplicate filenames
            target_path = self._get_unique_filename(target_path)
            
            # Save file
            file.save(target_path)
            
            # Get file info
            file_info = self._get_file_info(target_path)
            
            logging.info(f"File uploaded: {target_path} by user {self.username}")
            return file_info
            
        except Exception as e:
            logging.error(f"Upload failed for user {self.username}: {e}")
            raise
    
    def _get_target_directory(self, filename):
        """Get target directory based on file type"""
        ext = filename.lower().split('.')[-1]
        
        if ext in ['dcm']:
            return os.path.join(self.upload_path, 'dicom_datasets')
        elif ext in ['nii', 'gz']:
            return os.path.join(self.upload_path, 'nifti_files')
        elif ext in ['zip', 'tar', 'gz']:
            return os.path.join(self.upload_path, 'archives')
        else:
            return self.upload_path
    
    def _get_unique_filename(self, filepath):
        """Get unique filename if file already exists"""
        if not os.path.exists(filepath):
            return filepath
        
        base, ext = os.path.splitext(filepath)
        counter = 1
        
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        
        return f"{base}_{counter}{ext}"
    
    def _get_file_info(self, filepath):
        """Get file information"""
        try:
            stat = os.stat(filepath)
            filename = os.path.basename(filepath)
            file_type = self._get_file_type(filename)
            
            return {
                'name': filename,
                'path': os.path.relpath(filepath, self.upload_path),
                'size': stat.st_size,
                'size_formatted': self._format_file_size(stat.st_size),
                'type': file_type,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'modified_ago': self._time_ago(stat.st_mtime),
                'is_directory': os.path.isdir(filepath),
                'mime_type': self._get_mime_type(filepath)
            }
        except Exception as e:
            logging.error(f"Error getting file info for {filepath}: {e}")
            return None
    
    def _get_file_type(self, filename):
        """Get file type based on extension"""
        ext = filename.lower().split('.')[-1]
        
        if ext in ['dcm']:
            return 'dicom'
        elif ext in ['nii', 'gz']:
            return 'nifti'
        elif ext in ['zip', 'tar', 'gz']:
            return 'archive'
        elif ext in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']:
            return 'image'
        else:
            return 'unknown'
    
    def _get_mime_type(self, filepath):
        """Get MIME type of file"""
        try:
            if os.path.isdir(filepath):
                return 'inode/directory'
            
            # Try using python-magic
            mime = magic.from_file(filepath, mime=True)
            if mime:
                return mime
            
            # Fallback to mimetypes
            return mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
        except:
            return 'application/octet-stream'
    
    def _format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def _time_ago(self, timestamp):
        """Get time ago string"""
        now = datetime.now()
        file_time = datetime.fromtimestamp(timestamp)
        diff = now - file_time
        
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
    
    def list_files(self, path=''):
        """List files in a directory"""
        try:
            full_path = os.path.join(self.upload_path, path)
            
            if not os.path.exists(full_path):
                return []
            
            if not os.path.isdir(full_path):
                return []
            
            files = []
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                file_info = self._get_file_info(item_path)
                if file_info:
                    files.append(file_info)
            
            # Sort: directories first, then by name
            files.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))
            
            return files
            
        except Exception as e:
            logging.error(f"Error listing files for user {self.username}: {e}")
            return []
    
    def get_file_tree(self, depth=3, path=''):
        """Get file tree structure"""
        try:
            full_path = os.path.join(self.upload_path, path)
            
            if not os.path.exists(full_path) or not os.path.isdir(full_path):
                return []
            
            if depth <= 0:
                return []
            
            tree = []
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                rel_path = os.path.join(path, item)
                
                if os.path.isdir(item_path):
                    children = self.get_file_tree(depth - 1, rel_path)
                    tree.append({
                        'name': item,
                        'path': rel_path,
                        'type': 'directory',
                        'children': children,
                        'file_count': len([f for f in children if not f.get('is_directory', True)])
                    })
                else:
                    file_info = self._get_file_info(item_path)
                    if file_info:
                        tree.append(file_info)
            
            return tree
            
        except Exception as e:
            logging.error(f"Error getting file tree for user {self.username}: {e}")
            return []
    
    def get_breadcrumbs(self, path):
        """Get breadcrumb navigation"""
        breadcrumbs = [{'name': 'Home', 'path': ''}]
        
        if not path:
            return breadcrumbs
        
        parts = path.split('/')
        current_path = ''
        
        for part in parts:
            if part:
                current_path = os.path.join(current_path, part) if current_path else part
                breadcrumbs.append({
                    'name': part,
                    'path': current_path
                })
        
        return breadcrumbs
    
    def get_recent_files(self, limit=10):
        """Get recent files"""
        try:
            all_files = []
            
            # Walk through all user directories
            for root, dirs, files in os.walk(self.upload_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_info = self._get_file_info(file_path)
                    if file_info:
                        all_files.append(file_info)
            
            # Sort by modification time (newest first)
            all_files.sort(key=lambda x: x['modified'], reverse=True)
            
            return all_files[:limit]
            
        except Exception as e:
            logging.error(f"Error getting recent files for user {self.username}: {e}")
            return []
    
    def delete_file(self, file_path):
        """Delete a file or directory"""
        try:
            full_path = os.path.join(self.upload_path, file_path)
            
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Ensure path is within user's directory
            if not os.path.abspath(full_path).startswith(os.path.abspath(self.upload_path)):
                raise ValueError("Access denied: Path outside user directory")
            
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)
            
            logging.info(f"File deleted: {full_path} by user {self.username}")
            return True
            
        except Exception as e:
            logging.error(f"Error deleting file {file_path} for user {self.username}: {e}")
            raise
    
    def get_file_size(self, file_path):
        """Get file size"""
        try:
            full_path = os.path.join(self.upload_path, file_path)
            
            if not os.path.exists(full_path):
                return None
            
            if os.path.isdir(full_path):
                return self._get_directory_size(full_path)
            else:
                return os.path.getsize(full_path)
                
        except Exception as e:
            logging.error(f"Error getting file size for {file_path}: {e}")
            return None
    
    def _get_directory_size(self, directory):
        """Get total size of directory"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except:
            pass
        return total_size
    
    def rename_file(self, old_name, new_name, current_path=''):
        """Rename a file or directory"""
        try:
            old_path = os.path.join(self.upload_path, current_path, old_name)
            new_path = os.path.join(self.upload_path, current_path, new_name)
            
            if not os.path.exists(old_path):
                raise FileNotFoundError(f"File not found: {old_name}")
            
            if os.path.exists(new_path):
                raise FileExistsError(f"File already exists: {new_name}")
            
            os.rename(old_path, new_path)
            
            logging.info(f"File renamed: {old_path} -> {new_path} by user {self.username}")
            return self._get_file_info(new_path)
            
        except Exception as e:
            logging.error(f"Error renaming file {old_name} to {new_name}: {e}")
            raise
    
    def create_folder(self, folder_name, current_path=''):
        """Create a new folder"""
        try:
            folder_path = os.path.join(self.upload_path, current_path, folder_name)
            
            if os.path.exists(folder_path):
                raise FileExistsError(f"Folder already exists: {folder_name}")
            
            os.makedirs(folder_path)
            
            logging.info(f"Folder created: {folder_path} by user {self.username}")
            return self._get_file_info(folder_path)
            
        except Exception as e:
            logging.error(f"Error creating folder {folder_name}: {e}")
            raise
    
    def copy_file(self, source_path, destination_path):
        """Copy a file or directory"""
        try:
            source_full = os.path.join(self.upload_path, source_path)
            dest_full = os.path.join(self.upload_path, destination_path)
            
            if not os.path.exists(source_full):
                raise FileNotFoundError(f"Source file not found: {source_path}")
            
            if os.path.isdir(source_full):
                shutil.copytree(source_full, dest_full)
            else:
                shutil.copy2(source_full, dest_full)
            
            logging.info(f"File copied: {source_full} -> {dest_full} by user {self.username}")
            return self._get_file_info(dest_full)
            
        except Exception as e:
            logging.error(f"Error copying file {source_path} to {destination_path}: {e}")
            raise
    
    def move_file(self, source_path, destination_path):
        """Move a file or directory"""
        try:
            source_full = os.path.join(self.upload_path, source_path)
            dest_full = os.path.join(self.upload_path, destination_path)
            
            if not os.path.exists(source_full):
                raise FileNotFoundError(f"Source file not found: {source_path}")
            
            shutil.move(source_full, dest_full)
            
            logging.info(f"File moved: {source_full} -> {dest_full} by user {self.username}")
            return self._get_file_info(dest_full)
            
        except Exception as e:
            logging.error(f"Error moving file {source_path} to {destination_path}: {e}")
            raise
    
    def download_file(self, file_path):
        """Download a file"""
        try:
            full_path = os.path.join(self.upload_path, file_path)
            
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            from flask import send_file
            return send_file(full_path, as_attachment=True)
            
        except Exception as e:
            logging.error(f"Error downloading file {file_path}: {e}")
            raise
    
    def preview_file(self, file_path):
        """Preview a file (if supported)"""
        try:
            full_path = os.path.join(self.upload_path, file_path)
            
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file_info = self._get_file_info(full_path)
            
            # For now, return file info as JSON
            # In the future, this could generate thumbnails for images
            from flask import jsonify
            return jsonify(file_info)
            
        except Exception as e:
            logging.error(f"Error previewing file {file_path}: {e}")
            raise
    
    def move_to_processing(self, file_path):
        """Move file to processing directory"""
        try:
            source_path = os.path.join(self.upload_path, file_path)
            dest_path = os.path.join(self.upload_path, 'selected_for_processing', os.path.basename(file_path))
            
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            shutil.move(source_path, dest_path)
            
            logging.info(f"File moved to processing: {source_path} -> {dest_path}")
            return self._get_file_info(dest_path)
            
        except Exception as e:
            logging.error(f"Error moving file to processing: {e}")
            raise
    
    def get_processable_files(self):
        """Get files that can be processed by TotalSegmentator"""
        try:
            processable_files = []
            
            # Look for DICOM and NIfTI files
            for root, dirs, files in os.walk(self.upload_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_info = self._get_file_info(file_path)
                    
                    if file_info and file_info['type'] in ['dicom', 'nifti']:
                        processable_files.append(file_info)
            
            return processable_files
            
        except Exception as e:
            logging.error(f"Error getting processable files: {e}")
            return []
    
    def get_processing_history(self):
        """Get processing history"""
        try:
            # This would typically come from a database
            # For now, return empty list
            return []
        except Exception as e:
            logging.error(f"Error getting processing history: {e}")
            return []
    
    def get_processing_results(self):
        """Get processing results"""
        try:
            results = []
            
            if os.path.exists(self.results_path):
                for root, dirs, files in os.walk(self.results_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_info = self._get_file_info(file_path)
                        if file_info:
                            results.append(file_info)
            
            return results
            
        except Exception as e:
            logging.error(f"Error getting processing results: {e}")
            return [] 