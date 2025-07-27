"""
YueTransfer Statistics Utility
"""

import os
import psutil
from datetime import datetime, timedelta
from app.models.user import User, UserManager
from app.utils.file_manager import FileManager

def get_user_stats(user_id):
    """Get statistics for a specific user"""
    try:
        from app import db
        
        user = User.query.get(user_id)
        if not user:
            return {}
        
        file_manager = FileManager(user.username)
        
        # Get file counts by type
        all_files = []
        for root, dirs, files in os.walk(file_manager.upload_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_info = file_manager._get_file_info(file_path)
                if file_info:
                    all_files.append(file_info)
        
        # Count by type
        dicom_files = len([f for f in all_files if f['type'] == 'dicom'])
        nifti_files = len([f for f in all_files if f['type'] == 'nifti'])
        archive_files = len([f for f in all_files if f['type'] == 'archive'])
        image_files = len([f for f in all_files if f['type'] == 'image'])
        
        # Calculate total storage used
        total_storage = sum(f['size'] for f in all_files)
        storage_used = file_manager._format_file_size(total_storage)
        
        # Get processing jobs count (placeholder)
        processing_jobs = 0  # This would come from a job queue system
        
        return {
            'total_files': len(all_files),
            'dicom_files': dicom_files,
            'nifti_files': nifti_files,
            'archive_files': archive_files,
            'image_files': image_files,
            'storage_used': storage_used,
            'storage_used_bytes': total_storage,
            'storage_quota': user.storage_quota,
            'storage_quota_formatted': file_manager._format_file_size(user.storage_quota),
            'storage_usage_percentage': user.get_storage_usage_percentage(),
            'processing_jobs': processing_jobs,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'account_created': user.created_at.isoformat() if user.created_at else None
        }
        
    except Exception as e:
        print(f"Error getting user stats: {e}")
        return {}

def get_system_stats():
    """Get system-wide statistics"""
    try:
        # Get disk usage
        disk_usage = psutil.disk_usage('/')
        disk_total = disk_usage.total
        disk_used = disk_usage.used
        disk_free = disk_usage.free
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_total = memory.total
        memory_used = memory.used
        memory_free = memory.available
        
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Get user statistics
        user_manager = UserManager()
        user_stats = user_manager.get_user_stats()
        
        return {
            'disk': {
                'total': disk_total,
                'used': disk_used,
                'free': disk_free,
                'percent': (disk_used / disk_total) * 100 if disk_total > 0 else 0
            },
            'memory': {
                'total': memory_total,
                'used': memory_used,
                'free': memory_free,
                'percent': memory.percent
            },
            'cpu': {
                'percent': cpu_percent
            },
            'users': user_stats,
            'uptime': get_system_uptime()
        }
        
    except Exception as e:
        print(f"Error getting system stats: {e}")
        return {}

def get_system_uptime():
    """Get system uptime"""
    try:
        uptime_seconds = psutil.boot_time()
        uptime = datetime.now() - datetime.fromtimestamp(uptime_seconds)
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"
            
    except:
        return "Unknown"

def format_bytes(bytes_value):
    """Format bytes to human readable format"""
    if bytes_value == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while bytes_value >= 1024 and i < len(size_names) - 1:
        bytes_value /= 1024.0
        i += 1
    
    return f"{bytes_value:.1f} {size_names[i]}"

def get_storage_usage_by_user():
    """Get storage usage breakdown by user"""
    try:
        users = User.query.all()
        usage_data = []
        
        for user in users:
            file_manager = FileManager(user.username)
            
            # Calculate user's storage usage
            total_size = 0
            file_count = 0
            
            if os.path.exists(file_manager.upload_path):
                for root, dirs, files in os.walk(file_manager.upload_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.exists(file_path):
                            total_size += os.path.getsize(file_path)
                            file_count += 1
            
            usage_data.append({
                'username': user.username,
                'storage_used': total_size,
                'storage_used_formatted': format_bytes(total_size),
                'storage_quota': user.storage_quota,
                'storage_quota_formatted': format_bytes(user.storage_quota),
                'usage_percentage': (total_size / user.storage_quota) * 100 if user.storage_quota > 0 else 0,
                'file_count': file_count,
                'is_admin': user.is_admin,
                'is_active': user.is_active
            })
        
        # Sort by storage usage (highest first)
        usage_data.sort(key=lambda x: x['storage_used'], reverse=True)
        
        return usage_data
        
    except Exception as e:
        print(f"Error getting storage usage by user: {e}")
        return []

def get_file_type_distribution():
    """Get distribution of file types across all users"""
    try:
        users = User.query.all()
        type_counts = {
            'dicom': 0,
            'nifti': 0,
            'archive': 0,
            'image': 0,
            'unknown': 0
        }
        
        for user in users:
            file_manager = FileManager(user.username)
            
            if os.path.exists(file_manager.upload_path):
                for root, dirs, files in os.walk(file_manager.upload_path):
                    for file in files:
                        file_type = file_manager._get_file_type(file)
                        if file_type in type_counts:
                            type_counts[file_type] += 1
                        else:
                            type_counts['unknown'] += 1
        
        return type_counts
        
    except Exception as e:
        print(f"Error getting file type distribution: {e}")
        return {}

def get_upload_activity(days=30):
    """Get upload activity over the last N days"""
    try:
        # This would typically query a database table tracking uploads
        # For now, return placeholder data
        activity_data = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            activity_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'uploads': 0,  # This would be actual upload count
                'files': 0,    # This would be actual file count
                'size': 0      # This would be actual size uploaded
            })
        
        return list(reversed(activity_data))
        
    except Exception as e:
        print(f"Error getting upload activity: {e}")
        return []

def get_processing_stats():
    """Get TotalSegmentator processing statistics"""
    try:
        # This would query processing job history
        # For now, return placeholder data
        return {
            'total_jobs': 0,
            'completed_jobs': 0,
            'failed_jobs': 0,
            'pending_jobs': 0,
            'average_processing_time': 0,
            'total_processed_files': 0
        }
        
    except Exception as e:
        print(f"Error getting processing stats: {e}")
        return {} 