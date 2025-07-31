# TotalSegmentator Integration Configuration
# Configuration for communicating with the TotalSegmentator system

import os
from pathlib import Path

# TotalSegmentator system configuration
class TotalSegmentatorConfig:
    # TotalSegmentator server settings
    TOTALSEGMENTATOR_URL = os.environ.get('TOTALSEGMENTATOR_URL', 'http://localhost:8000')
    TOTALSEGMENTATOR_HOST = os.environ.get('TOTALSEGMENTATOR_HOST', 'localhost')
    TOTALSEGMENTATOR_PORT = int(os.environ.get('TOTALSEGMENTATOR_PORT', 8000))
    
    # API endpoints for TotalSegmentator communication
    TOTALSEGMENTATOR_ENDPOINTS = {
        'upload': '/api/upload',
        'process': '/api/process',
        'status': '/api/status',
        'download': '/api/download',
        'jobs': '/api/jobs',
        'results': '/api/results'
    }
    
    # Authentication settings
    API_KEY = os.environ.get('TOTALSEGMENTATOR_API_KEY', 'your_api_key_here')
    AUTH_METHOD = 'api_key'  # 'api_key', 'token', 'oauth'
    
    # Job management settings
    JOB_SETTINGS = {
        'max_concurrent_jobs': 5,
        'job_timeout': 3600,  # 1 hour
        'retry_attempts': 3,
        'retry_delay': 60  # 1 minute
    }
    
    # File processing settings
    PROCESSING_SETTINGS = {
        'supported_formats': ['dcm', 'dicom', 'nii', 'nii.gz'],
        'max_file_size': 10 * 1024 * 1024 * 1024,  # 10GB
        'chunk_size': 1024 * 1024,  # 1MB
        'compression': True
    }
    
    # Results handling
    RESULTS_SETTINGS = {
        'output_format': 'nii.gz',
        'include_preview': True,
        'include_metadata': True,
        'auto_download': True
    }

# Integration helpers
def get_totalsegmentator_url(endpoint):
    """Get full TotalSegmentator URL for an endpoint"""
    return f"{TotalSegmentatorConfig.TOTALSEGMENTATOR_URL.rstrip('/')}/{endpoint.lstrip('/')}"

def is_totalsegmentator_available():
    """Check if TotalSegmentator is available"""
    try:
        import requests
        response = requests.get(get_totalsegmentator_url('/health'), timeout=5)
        return response.status_code == 200
    except:
        return False