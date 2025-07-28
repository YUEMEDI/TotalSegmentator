"""
YueTransfer TotalSegmentator Integration
Handles background processing of medical imaging files
"""

import os
import json
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path

from app.models.user import ProcessingJob
from app import db

def start_segmentation_job(job_id):
    """Start a segmentation job in the background"""
    try:
        # Start processing in a separate thread
        thread = threading.Thread(target=process_segmentation_job, args=(job_id,))
        thread.daemon = True
        thread.start()
        
        return True
    except Exception as e:
        print(f"Error starting segmentation job {job_id}: {e}")
        return False

def process_segmentation_job(job_id):
    """Process a segmentation job"""
    try:
        # Get job from database
        job = ProcessingJob.query.get(job_id)
        if not job:
            print(f"Job {job_id} not found")
            return
        
        # Update job status
        job.status = 'processing'
        job.started_at = datetime.utcnow()
        job.progress = 0.0
        db.session.commit()
        
        print(f"🔄 Starting TotalSegmentator job {job_id}: {job.job_name}")
        
        # Get input files
        input_files = json.loads(job.input_files)
        user = job.user
        
        # Create output directory
        output_dir = os.path.join(user.get_results_path(), f"job_{job_id}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Process each file
        for i, file_path in enumerate(input_files):
            try:
                # Update progress
                job.progress = (i / len(input_files)) * 0.9  # Reserve 10% for final steps
                db.session.commit()
                
                # Get full input path
                input_file_path = os.path.join(user.get_upload_path(), file_path)
                
                if not os.path.exists(input_file_path):
                    print(f"⚠️  Input file not found: {input_file_path}")
                    continue
                
                # Generate output filename
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                if base_name.endswith('.nii'):
                    base_name = os.path.splitext(base_name)[0]
                
                output_file_path = os.path.join(output_dir, f"{base_name}_segmentation")
                
                # Run TotalSegmentator
                success = run_totalsegmentator(
                    input_path=input_file_path,
                    output_path=output_file_path,
                    task=job.task,
                    fast_mode=job.fast_mode,
                    preview=job.preview
                )
                
                if not success:
                    print(f"❌ TotalSegmentator failed for file: {file_path}")
                    continue
                
                print(f"✅ Processed: {file_path}")
                
            except Exception as e:
                print(f"❌ Error processing file {file_path}: {e}")
                continue
        
        # Finalize job
        job.progress = 1.0
        job.status = 'completed'
        job.completed_at = datetime.utcnow()
        job.output_path = output_dir
        db.session.commit()
        
        print(f"🎉 TotalSegmentator job {job_id} completed successfully")
        
        # Create summary file
        create_job_summary(job, output_dir, input_files)
        
    except Exception as e:
        print(f"❌ Error in segmentation job {job_id}: {e}")
        
        # Update job with error
        try:
            job = ProcessingJob.query.get(job_id)
            if job:
                job.status = 'failed'
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                db.session.commit()
        except:
            pass

def run_totalsegmentator(input_path, output_path, task='total', fast_mode=False, preview=False):
    """Run TotalSegmentator command"""
    try:
        # Check if TotalSegmentator is available
        if not check_totalsegmentator_available():
            print("❌ TotalSegmentator not available")
            return False
        
        # Build command
        cmd = ['TotalSegmentator']
        
        # Input and output
        cmd.extend(['-i', input_path])
        cmd.extend(['-o', output_path])
        
        # Task
        if task != 'total':
            cmd.extend(['--task', task])
        
        # Options
        if fast_mode:
            cmd.append('--fast')
        
        if preview:
            cmd.append('--preview')
        
        # Add other useful options
        cmd.extend(['--ml'])  # Use machine learning
        cmd.extend(['--nr_thr_saving', '1'])  # Single thread for saving
        
        print(f"🔧 Running command: {' '.join(cmd)}")
        
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        if result.returncode == 0:
            print(f"✅ TotalSegmentator completed successfully")
            return True
        else:
            print(f"❌ TotalSegmentator failed with return code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ TotalSegmentator timed out")
        return False
    except Exception as e:
        print(f"❌ Error running TotalSegmentator: {e}")
        return False

def check_totalsegmentator_available():
    """Check if TotalSegmentator is available"""
    try:
        result = subprocess.run(
            ['TotalSegmentator', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False

def create_job_summary(job, output_dir, input_files):
    """Create a summary file for the job"""
    try:
        summary = {
            'job_id': job.id,
            'job_name': job.job_name,
            'user': job.user.username,
            'task': job.task,
            'fast_mode': job.fast_mode,
            'preview': job.preview,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'input_files': input_files,
            'output_directory': output_dir,
            'status': job.status,
            'error_message': job.error_message
        }
        
        # Count output files
        output_files = []
        if os.path.exists(output_dir):
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(('.nii', '.nii.gz')):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, output_dir)
                        output_files.append({
                            'filename': file,
                            'path': relative_path,
                            'size': os.path.getsize(file_path)
                        })
        
        summary['output_files'] = output_files
        summary['output_files_count'] = len(output_files)
        
        # Save summary
        summary_path = os.path.join(output_dir, 'job_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📄 Job summary saved: {summary_path}")
        
    except Exception as e:
        print(f"❌ Error creating job summary: {e}")

def get_available_tasks():
    """Get list of available TotalSegmentator tasks"""
    default_tasks = [
        {
            'name': 'total',
            'description': 'Total segmentation (117 classes)',
            'estimated_time': '2-5 minutes'
        },
        {
            'name': 'total_mr',
            'description': 'Total segmentation for MR images',
            'estimated_time': '2-5 minutes'
        },
        {
            'name': 'lung_vessels',
            'description': 'Lung vessel segmentation',
            'estimated_time': '1-2 minutes'
        },
        {
            'name': 'cerebral_bleed',
            'description': 'Cerebral bleeding detection',
            'estimated_time': '30 seconds'
        },
        {
            'name': 'hip_implant',
            'description': 'Hip implant detection',
            'estimated_time': '30 seconds'
        },
        {
            'name': 'coronary_arteries',
            'description': 'Coronary artery segmentation',
            'estimated_time': '1 minute'
        },
        {
            'name': 'body',
            'description': 'Body segmentation',
            'estimated_time': '30 seconds'
        },
        {
            'name': 'liver_vessels',
            'description': 'Liver vessel segmentation',
            'estimated_time': '1 minute'
        }
    ]
    
    return default_tasks

def estimate_processing_time(file_count, task='total', fast_mode=False):
    """Estimate processing time for a job"""
    # Base times in seconds
    base_times = {
        'total': 180,  # 3 minutes
        'total_mr': 180,
        'lung_vessels': 90,
        'cerebral_bleed': 30,
        'hip_implant': 30,
        'coronary_arteries': 60,
        'body': 30,
        'liver_vessels': 60
    }
    
    base_time = base_times.get(task, 180)
    
    # Adjust for fast mode
    if fast_mode:
        base_time *= 0.5
    
    # Multiply by file count
    total_time = base_time * file_count
    
    # Add some overhead
    total_time *= 1.2
    
    return int(total_time)

def format_processing_time(seconds):
    """Format processing time in human readable format"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}"
        else:
            return f"{hours} hour{'s' if hours != 1 else ''}"

def cancel_job(job_id):
    """Cancel a running job"""
    try:
        job = ProcessingJob.query.get(job_id)
        if not job:
            return False
        
        if job.status not in ['pending', 'processing']:
            return False
        
        # Update job status
        job.status = 'cancelled'
        job.completed_at = datetime.utcnow()
        db.session.commit()
        
        # TODO: Actually kill the running process
        # This would require tracking process IDs
        
        print(f"🛑 Job {job_id} cancelled")
        return True
        
    except Exception as e:
        print(f"❌ Error cancelling job {job_id}: {e}")
        return False

def cleanup_old_jobs(days_old=30):
    """Clean up old completed jobs"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        old_jobs = ProcessingJob.query.filter(
            ProcessingJob.completed_at < cutoff_date,
            ProcessingJob.status.in_(['completed', 'failed', 'cancelled'])
        ).all()
        
        for job in old_jobs:
            try:
                # Delete output files
                if job.output_path and os.path.exists(job.output_path):
                    import shutil
                    shutil.rmtree(job.output_path)
                
                # Delete job record
                db.session.delete(job)
                
            except Exception as e:
                print(f"❌ Error cleaning up job {job.id}: {e}")
                continue
        
        db.session.commit()
        print(f"🧹 Cleaned up {len(old_jobs)} old jobs")
        
    except Exception as e:
        print(f"❌ Error cleaning up old jobs: {e}")

def get_system_status():
    """Get TotalSegmentator system status"""
    status = {
        'totalsegmentator_available': check_totalsegmentator_available(),
        'pending_jobs': ProcessingJob.query.filter_by(status='pending').count(),
        'processing_jobs': ProcessingJob.query.filter_by(status='processing').count(),
        'completed_jobs_today': ProcessingJob.query.filter(
            ProcessingJob.completed_at >= datetime.utcnow().date(),
            ProcessingJob.status == 'completed'
        ).count()
    }
    
    return status 