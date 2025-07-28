"""
YueTransfer File Manager Utility
Handles all file operations for users
"""

import os
import shutil
import mimetypes
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from app.config import Config

class FileManager:
    """File management utility for user files"""
    
    def __init__(self, username):
        self.username = username
        self.config = Config()
        self.upload_path = self.config.get_upload_path(username)
        self.results_path = self.config.get_results_path(username)
        
        # Ensure user directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
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
    
    def list_directory(self, directory_path):
        """List contents of a directory"""
        try:
            if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
                return []
            
            contents = []
            
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                
                try:
                    stat_info = os.stat(item_path)
                    is_directory = os.path.isdir(item_path)
                    
                    # Get file type and icon
                    file_type = self._get_file_type(item) if not is_directory else 'folder'
                    icon = self._get_file_icon(file_type)
                    
                    # Format file size
                    size = 0 if is_directory else stat_info.st_size
                    size_formatted = self._format_file_size(size)
                    
                    # Format modification time
                    modified_time = datetime.fromtimestamp(stat_info.st_mtime)
                    modified_formatted = modified_time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    contents.append({
                        'name': item,
                        'type': file_type,
                        'icon': icon,
                        'is_directory': is_directory,
                        'size': size,
                        'size_formatted': size_formatted,
                        'modified': modified_time,
                        'modified_formatted': modified_formatted,
                        'path': os.path.relpath(item_path, self.upload_path).replace('\\', '/'),
                        'can_preview': self._can_preview(item) if not is_directory else False
                    })
                    
                except (OSError, IOError):
                    continue
            
            # Sort: directories first, then files, both alphabetically
            contents.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))
            
            return contents
            
        except Exception as e:
            print(f"Error listing directory {directory_path}: {e}")
            return []
    
    def save_uploaded_file(self, file):
        """Save an uploaded file"""
        try:
            if not file or not file.filename:
                raise ValueError("No file provided")
            
            # Secure the filename
            filename = secure_filename(file.filename)
            if not filename:
                raise ValueError("Invalid filename")
            
            # Determine target directory based on file type
            file_type = self._get_file_type(filename)
            target_dir = self._get_target_directory(file_type)
            
            # Ensure target directory exists
            os.makedirs(target_dir, exist_ok=True)
            
            # Handle duplicate filenames
            file_path = os.path.join(target_dir, filename)
            if os.path.exists(file_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(file_path):
                    new_filename = f"{base}_{counter}{ext}"
                    file_path = os.path.join(target_dir, new_filename)
                    counter += 1
                filename = os.path.basename(file_path)
            
            # Save the file
            file.save(file_path)
            
            # Get file information
            stat_info = os.stat(file_path)
            
            return {
                'filename': filename,
                'original_filename': file.filename,
                'path': os.path.relpath(file_path, self.upload_path).replace('\\', '/'),
                'size': stat_info.st_size,
                'size_formatted': self._format_file_size(stat_info.st_size),
                'type': file_type,
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Failed to save uploaded file: {str(e)}")
    
    def get_processable_files(self):
        """Get files that can be processed by TotalSegmentator"""
        processable_files = []
        processable_extensions = ['.nii', '.nii.gz', '.dcm']
        
        try:
            for root, dirs, files in os.walk(self.upload_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check if file has processable extension
                    is_processable = any(file.lower().endswith(ext) for ext in processable_extensions)
                    
                    if is_processable:
                        try:
                            stat_info = os.stat(file_path)
                            relative_path = os.path.relpath(file_path, self.upload_path).replace('\\', '/')
                            
                            processable_files.append({
                                'name': file,
                                'path': relative_path,
                                'size': stat_info.st_size,
                                'size_formatted': self._format_file_size(stat_info.st_size),
                                'type': self._get_file_type(file),
                                'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                            })
                        except OSError:
                            continue
            
            return processable_files
            
        except Exception as e:
            print(f"Error getting processable files: {e}")
            return []
    
    def get_file_tree(self, max_depth=3):
        """Get file tree structure for navigation"""
        try:
            return self._build_tree(self.upload_path, '', max_depth, 0)
        except Exception as e:
            print(f"Error building file tree: {e}")
            return []
    
    def _build_tree(self, current_path, relative_path, max_depth, current_depth):
        """Recursively build file tree"""
        if current_depth >= max_depth:
            return []
        
        try:
            items = []
            
            if not os.path.exists(current_path) or not os.path.isdir(current_path):
                return items
            
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                item_relative_path = os.path.join(relative_path, item).replace('\\', '/') if relative_path else item
                
                if os.path.isdir(item_path):
                    # Directory
                    children = self._build_tree(item_path, item_relative_path, max_depth, current_depth + 1)
                    
                    items.append({
                        'name': item,
                        'type': 'folder',
                        'path': item_relative_path,
                        'is_directory': True,
                        'children': children,
                        'has_children': len(children) > 0
                    })
                else:
                    # File
                    file_type = self._get_file_type(item)
                    
                    items.append({
                        'name': item,
                        'type': file_type,
                        'path': item_relative_path,
                        'is_directory': False,
                        'icon': self._get_file_icon(file_type)
                    })
            
            # Sort: directories first, then files
            items.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))
            
            return items
            
        except Exception as e:
            print(f"Error building tree for {current_path}: {e}")
            return []
    
    def search_files(self, query, file_type=None):
        """Search for files by name or type"""
        results = []
        
        try:
            for root, dirs, files in os.walk(self.upload_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check if file matches search criteria
                    matches_query = query.lower() in file.lower() if query else True
                    matches_type = (self._get_file_type(file) == file_type) if file_type else True
                    
                    if matches_query and matches_type:
                        try:
                            stat_info = os.stat(file_path)
                            relative_path = os.path.relpath(file_path, self.upload_path).replace('\\', '/')
                            directory = os.path.dirname(relative_path)
                            
                            results.append({
                                'name': file,
                                'path': relative_path,
                                'directory': directory if directory != '.' else '',
                                'size': stat_info.st_size,
                                'size_formatted': self._format_file_size(stat_info.st_size),
                                'type': self._get_file_type(file),
                                'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                            })
                        except OSError:
                            continue
            
            return results
            
        except Exception as e:
            print(f"Error searching files: {e}")
            return []
    
    def get_storage_breakdown(self):
        """Get storage usage breakdown by file type"""
        breakdown = {
            'dicom': {'count': 0, 'size': 0},
            'nifti': {'count': 0, 'size': 0},
            'archive': {'count': 0, 'size': 0},
            'image': {'count': 0, 'size': 0},
            'other': {'count': 0, 'size': 0}
        }
        
        try:
            for root, dirs, files in os.walk(self.upload_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    try:
                        file_size = os.path.getsize(file_path)
                        file_type = self._get_file_type(file)
                        
                        if file_type in breakdown:
                            breakdown[file_type]['count'] += 1
                            breakdown[file_type]['size'] += file_size
                        else:
                            breakdown['other']['count'] += 1
                            breakdown['other']['size'] += file_size
                            
                    except OSError:
                        continue
            
            # Format sizes
            for file_type in breakdown:
                breakdown[file_type]['size_formatted'] = self._format_file_size(breakdown[file_type]['size'])
            
            return breakdown
            
        except Exception as e:
            print(f"Error getting storage breakdown: {e}")
            return breakdown
    
    def _get_target_directory(self, file_type):
        """Get target directory based on file type"""
        type_directories = {
            'dicom': 'dicom_datasets',
            'nifti': 'nifti_files',
            'archive': 'archives',
            'image': 'images'
        }
        
        subdir = type_directories.get(file_type, 'other')
        return os.path.join(self.upload_path, subdir)
    
    def _get_file_type(self, filename):
        """Determine file type based on extension"""
        if not filename:
            return 'unknown'
        
        filename_lower = filename.lower()
        
        # Medical imaging formats
        if filename_lower.endswith('.dcm'):
            return 'dicom'
        elif filename_lower.endswith(('.nii', '.nii.gz')):
            return 'nifti'
        
        # Archive formats
        elif filename_lower.endswith(('.zip', '.tar', '.tar.gz', '.rar', '.7z')):
            return 'archive'
        
        # Image formats
        elif filename_lower.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif')):
            return 'image'
        
        # Document formats
        elif filename_lower.endswith(('.pdf', '.doc', '.docx', '.txt', '.rtf')):
            return 'document'
        
        # Data formats
        elif filename_lower.endswith(('.csv', '.xlsx', '.xls', '.json', '.xml')):
            return 'data'
        
        # Code formats
        elif filename_lower.endswith(('.py', '.js', '.html', '.css', '.sql', '.sh')):
            return 'code'
        
        else:
            return 'unknown'
    
    def _get_file_icon(self, file_type):
        """Get Font Awesome icon class for file type"""
        icons = {
            'folder': 'fas fa-folder',
            'dicom': 'fas fa-x-ray',
            'nifti': 'fas fa-brain',
            'archive': 'fas fa-archive',
            'image': 'fas fa-image',
            'document': 'fas fa-file-alt',
            'data': 'fas fa-table',
            'code': 'fas fa-code',
            'unknown': 'fas fa-file'
        }
        
        return icons.get(file_type, icons['unknown'])
    
    def _can_preview(self, filename):
        """Check if file can be previewed"""
        preview_types = ['image']
        file_type = self._get_file_type(filename)
        return file_type in preview_types
    
    def _format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        
        return f"{s} {size_names[i]}"

# Utility functions for use in routes
def get_file_stats(directory_path):
    """Get statistics for a directory"""
    try:
        total_files = 0
        total_size = 0
        file_types = {}
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    total_files += 1
                    total_size += file_size
                    
                    # Count by file type
                    file_manager = FileManager('')
                    file_type = file_manager._get_file_type(file)
                    file_types[file_type] = file_types.get(file_type, 0) + 1
                    
                except OSError:
                    continue
        
        return {
            'total_files': total_files,
            'total_size': total_size,
            'file_types': file_types
        }
        
    except Exception as e:
        print(f"Error getting file stats: {e}")
        return {'total_files': 0, 'total_size': 0, 'file_types': {}}

def get_recent_files(directory_path, limit=10):
    """Get recently uploaded files"""
    try:
        recent_files = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    stat_info = os.stat(file_path)
                    recent_files.append({
                        'name': file,
                        'path': os.path.relpath(file_path, directory_path).replace('\\', '/'),
                        'size': stat_info.st_size,
                        'modified': stat_info.st_mtime,
                        'modified_formatted': datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')
                    })
                    
                except OSError:
                    continue
        
        # Sort by modification time (newest first) and limit
        recent_files.sort(key=lambda x: x['modified'], reverse=True)
        return recent_files[:limit]
        
    except Exception as e:
        print(f"Error getting recent files: {e}")
        return [] 