"""
YueTransfer Admin Routes
Administrative interface for user and system management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from app.models.user import User, UserManager, ProcessingJob
from app.utils.auth import require_admin
from app.utils.totalsegmentator_integration import get_system_status
from app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@require_admin
def dashboard():
    """Admin dashboard"""
    try:
        # Get system statistics
        user_manager = UserManager()
        
        # User statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(is_admin=True).count()
        
        # Storage statistics
        total_storage_used = db.session.query(db.func.sum(User.storage_used)).scalar() or 0
        total_storage_quota = db.session.query(db.func.sum(User.storage_quota)).scalar() or 0
        
        # Processing statistics
        pending_jobs = ProcessingJob.query.filter_by(status='pending').count()
        processing_jobs = ProcessingJob.query.filter_by(status='processing').count()
        completed_jobs_today = ProcessingJob.query.filter(
            ProcessingJob.completed_at >= db.func.date('now'),
            ProcessingJob.status == 'completed'
        ).count()
        
        # Recent activity
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_jobs = ProcessingJob.query.order_by(ProcessingJob.created_at.desc()).limit(10).all()
        
        # System status
        system_status = get_system_status()
        
        stats = {
            'users': {
                'total': total_users,
                'active': active_users,
                'admins': admin_users,
                'inactive': total_users - active_users
            },
            'storage': {
                'used': total_storage_used,
                'quota': total_storage_quota,
                'used_formatted': format_file_size(total_storage_used),
                'quota_formatted': format_file_size(total_storage_quota),
                'usage_percentage': (total_storage_used / total_storage_quota * 100) if total_storage_quota > 0 else 0
            },
            'jobs': {
                'pending': pending_jobs,
                'processing': processing_jobs,
                'completed_today': completed_jobs_today
            },
            'system': system_status
        }
        
        return render_template('admin/dashboard.html',
                             stats=stats,
                             recent_users=recent_users,
                             recent_jobs=recent_jobs)
    
    except Exception as e:
        flash(f'Error loading admin dashboard: {str(e)}', 'error')
        return render_template('admin/dashboard.html',
                             stats={},
                             recent_users=[],
                             recent_jobs=[])

@admin_bp.route('/users')
@login_required
@require_admin
def users():
    """User management"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Search and filter
        search = request.args.get('search', '')
        status_filter = request.args.get('status', 'all')
        role_filter = request.args.get('role', 'all')
        
        # Build query
        query = User.query
        
        if search:
            query = query.filter(
                db.or_(
                    User.username.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%')
                )
            )
        
        if status_filter == 'active':
            query = query.filter_by(is_active=True)
        elif status_filter == 'inactive':
            query = query.filter_by(is_active=False)
        
        if role_filter == 'admin':
            query = query.filter_by(is_admin=True)
        elif role_filter == 'user':
            query = query.filter_by(is_admin=False)
        
        users_pagination = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('admin/users.html',
                             users=users_pagination,
                             search=search,
                             status_filter=status_filter,
                             role_filter=role_filter)
    
    except Exception as e:
        flash(f'Error loading users: {str(e)}', 'error')
        return render_template('admin/users.html',
                             users=None,
                             search='',
                             status_filter='all',
                             role_filter='all')

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@require_admin
def create_user():
    """Create new user"""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            is_admin = bool(request.form.get('is_admin'))
            storage_quota = int(request.form.get('storage_quota', 107374182400))  # 100GB default
            
            # Validation
            if not username or not password:
                flash('Username and password are required.', 'error')
                return render_template('admin/create_user.html')
            
            if len(username) < 3:
                flash('Username must be at least 3 characters long.', 'error')
                return render_template('admin/create_user.html')
            
            if len(password) < 8:
                flash('Password must be at least 8 characters long.', 'error')
                return render_template('admin/create_user.html')
            
            # Create user
            user_manager = UserManager()
            user = user_manager.create_user(
                username=username,
                password=password,
                email=email if email else None,
                is_admin=is_admin
            )
            
            # Update storage quota
            user.storage_quota = storage_quota
            db.session.commit()
            
            flash(f'User "{username}" created successfully.', 'success')
            return redirect(url_for('admin.users'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error creating user: {str(e)}', 'error')
    
    return render_template('admin/create_user.html')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@require_admin
def edit_user(user_id):
    """Edit user"""
    try:
        user = User.query.get_or_404(user_id)
        
        if request.method == 'POST':
            # Get form data
            email = request.form.get('email', '').strip()
            is_admin = bool(request.form.get('is_admin'))
            is_active = bool(request.form.get('is_active'))
            storage_quota = int(request.form.get('storage_quota', user.storage_quota))
            
            # Prevent admin from deactivating themselves
            if user.id == current_user.id and not is_active:
                flash('You cannot deactivate your own account.', 'error')
                return render_template('admin/edit_user.html', user=user)
            
            # Update user
            user.email = email if email else None
            user.is_admin = is_admin
            user.is_active = is_active
            user.storage_quota = storage_quota
            
            db.session.commit()
            
            flash(f'User "{user.username}" updated successfully.', 'success')
            return redirect(url_for('admin.users'))
        
        # Calculate user statistics
        user_manager = UserManager()
        user_stats = user_manager.get_user_stats(user.id)
        
        return render_template('admin/edit_user.html', user=user, user_stats=user_stats)
    
    except Exception as e:
        flash(f'Error editing user: {str(e)}', 'error')
        return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@require_admin
def delete_user(user_id):
    """Delete user"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent admin from deleting themselves
        if user.id == current_user.id:
            flash('You cannot delete your own account.', 'error')
            return redirect(url_for('admin.users'))
        
        username = user.username
        
        # Delete user (this will also delete their files)
        user_manager = UserManager()
        user_manager.delete_user(user.id)
        
        flash(f'User "{username}" deleted successfully.', 'success')
        
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'error')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@require_admin
def reset_password(user_id):
    """Reset user password"""
    try:
        user = User.query.get_or_404(user_id)
        new_password = request.form.get('new_password', '').strip()
        
        if not new_password or len(new_password) < 8:
            flash('New password must be at least 8 characters long.', 'error')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        flash(f'Password for user "{user.username}" has been reset.', 'success')
        
    except Exception as e:
        flash(f'Error resetting password: {str(e)}', 'error')
    
    return redirect(url_for('admin.edit_user', user_id=user_id))

@admin_bp.route('/jobs')
@login_required
@require_admin
def jobs():
    """Processing jobs management"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Filters
        status_filter = request.args.get('status', 'all')
        user_filter = request.args.get('user', 'all')
        
        # Build query
        query = ProcessingJob.query
        
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)
        
        if user_filter != 'all':
            query = query.filter_by(user_id=int(user_filter))
        
        jobs_pagination = query.order_by(ProcessingJob.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get users for filter dropdown
        users = User.query.order_by(User.username).all()
        
        return render_template('admin/jobs.html',
                             jobs=jobs_pagination,
                             users=users,
                             status_filter=status_filter,
                             user_filter=user_filter)
    
    except Exception as e:
        flash(f'Error loading jobs: {str(e)}', 'error')
        return render_template('admin/jobs.html',
                             jobs=None,
                             users=[],
                             status_filter='all',
                             user_filter='all')

@admin_bp.route('/jobs/<int:job_id>')
@login_required
@require_admin
def job_details(job_id):
    """Job details"""
    try:
        job = ProcessingJob.query.get_or_404(job_id)
        
        # Get job files
        input_files = json.loads(job.input_files) if job.input_files else []
        
        # Get output files if available
        output_files = []
        if job.output_path and os.path.exists(job.output_path):
            for root, dirs, files in os.walk(job.output_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, job.output_path)
                    output_files.append({
                        'name': file,
                        'path': relative_path,
                        'size': os.path.getsize(file_path),
                        'size_formatted': format_file_size(os.path.getsize(file_path))
                    })
        
        return render_template('admin/job_details.html',
                             job=job,
                             input_files=input_files,
                             output_files=output_files)
    
    except Exception as e:
        flash(f'Error loading job details: {str(e)}', 'error')
        return redirect(url_for('admin.jobs'))

@admin_bp.route('/system')
@login_required
@require_admin
def system():
    """System status and configuration"""
    try:
        import psutil
        import sys
        from app.config import Config
        
        config = Config()
        
        # System information
        system_info = {
            'python_version': sys.version,
            'platform': sys.platform,
            'cpu_count': psutil.cpu_count(),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'used': psutil.virtual_memory().used,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
            }
        }
        
        # Application configuration
        app_config = {
            'debug': config.DEBUG,
            'environment': config.ENV,
            'upload_folder': config.UPLOAD_FOLDER,
            'results_folder': config.RESULTS_FOLDER,
            'sftp_host': config.SFTP_HOST,
            'sftp_port': config.SFTP_PORT,
            'web_port': config.WEB_PORT,
            'max_content_length': config.MAX_CONTENT_LENGTH
        }
        
        # TotalSegmentator status
        totalseg_status = get_system_status()
        
        return render_template('admin/system.html',
                             system_info=system_info,
                             app_config=app_config,
                             totalseg_status=totalseg_status)
    
    except Exception as e:
        flash(f'Error loading system information: {str(e)}', 'error')
        return render_template('admin/system.html',
                             system_info={},
                             app_config={},
                             totalseg_status={})

@admin_bp.route('/logs')
@login_required
@require_admin
def logs():
    """View application logs"""
    try:
        from app.config import Config
        config = Config()
        
        log_file = config.LOG_FILE
        log_lines = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Get last 100 lines
                log_lines = lines[-100:] if len(lines) > 100 else lines
                log_lines.reverse()  # Show newest first
        
        return render_template('admin/logs.html', log_lines=log_lines)
    
    except Exception as e:
        flash(f'Error loading logs: {str(e)}', 'error')
        return render_template('admin/logs.html', log_lines=[])

# API endpoints for admin
@admin_bp.route('/api/stats')
@login_required
@require_admin
def api_stats():
    """Get admin statistics"""
    try:
        stats = {
            'users': {
                'total': User.query.count(),
                'active': User.query.filter_by(is_active=True).count(),
                'admins': User.query.filter_by(is_admin=True).count()
            },
            'jobs': {
                'pending': ProcessingJob.query.filter_by(status='pending').count(),
                'processing': ProcessingJob.query.filter_by(status='processing').count(),
                'completed': ProcessingJob.query.filter_by(status='completed').count(),
                'failed': ProcessingJob.query.filter_by(status='failed').count()
            },
            'storage': {
                'total_used': db.session.query(db.func.sum(User.storage_used)).scalar() or 0,
                'total_quota': db.session.query(db.func.sum(User.storage_quota)).scalar() or 0
            }
        }
        
        # Format storage sizes
        stats['storage']['total_used_formatted'] = format_file_size(stats['storage']['total_used'])
        stats['storage']['total_quota_formatted'] = format_file_size(stats['storage']['total_quota'])
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@require_admin
def toggle_user_status(user_id):
    """Toggle user active status"""
    try:
        user = User.query.get_or_404(user_id)
        
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot modify your own status'}), 400
        
        user.is_active = not user.is_active
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_active': user.is_active,
            'message': f'User "{user.username}" {"activated" if user.is_active else "deactivated"}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/jobs/<int:job_id>/cancel', methods=['POST'])
@login_required
@require_admin
def cancel_job(job_id):
    """Cancel a processing job"""
    try:
        from app.utils.totalsegmentator_integration import cancel_job
        
        success = cancel_job(job_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Job cancelled successfully'})
        else:
            return jsonify({'error': 'Failed to cancel job'}), 400
    
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