#!/usr/bin/env python3
"""
YUEUPLOAD - Advanced DICOM Upload System
Main application entry point
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_python_version():
    """Check if we're using the correct Python version (3.10.x)"""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ is required for compatibility with YUETransfer and TotalSegmentator")
        print(f"   Current version: {sys.version}")
        print("   Please use the totalsegmentator conda environment:")
        print("   C:\\Users\\ZERO\\.conda\\envs\\totalsegmentator\\python.exe run.py")
        return False
    elif sys.version_info >= (3, 12):
        print("⚠️  Warning: Python 3.12 detected. For best compatibility, use Python 3.10.x")
        print(f"   Current version: {sys.version}")
        print("   Recommended: Use totalsegmentator conda environment (Python 3.10.13)")
        print("   C:\\Users\\ZERO\\.conda\\envs\\totalsegmentator\\python.exe run.py")
        return True  # Still allow it to run, but warn
    else:
        print(f"✅ Python version: {sys.version} (compatible)")
        return True

def suggest_conda_environment():
    """Suggest the correct conda environment to use"""
    print("\n🔧 Environment Setup:")
    print("   For best compatibility, use the totalsegmentator conda environment:")
    print("   C:\\Users\\ZERO\\.conda\\envs\\totalsegmentator\\python.exe run.py")
    print("   Or activate the environment first:")
    print("   conda activate totalsegmentator")
    print("   python run.py")

try:
    from app import create_app
    from config.settings import get_config
    from config.yuetransfer import validate_config as validate_yuetransfer
    from config.totalsegmentator import is_totalsegmentator_available
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   This usually means you're not using the correct Python environment.")
    suggest_conda_environment()
    sys.exit(1)

def check_system_requirements():
    """Check if all system requirements are met"""
    print("🔍 Checking YUEUPLOAD system requirements...")
    
    # Check Python version first
    if not check_python_version():
        return False
    
    # Check required packages with correct import names
    required_packages = [
        ('flask', 'flask'),
        ('pydicom', 'pydicom'),
        ('nibabel', 'nibabel'),
        ('PIL', 'pillow'),  # PIL is the correct import name for pillow
        ('requests', 'requests')
    ]
    
    missing_packages = []
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name} is available")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name} is missing")
    
    if missing_packages:
        print(f"\n📦 Install missing packages:")
        print(f"   pip install {' '.join(missing_packages)}")
        print(f"   Or use the totalsegmentator environment which has most packages:")
        print(f"   C:\\Users\\ZERO\\.conda\\envs\\totalsegmentator\\python.exe -m pip install {' '.join(missing_packages)}")
        return False
    
    # Check YUETransfer integration
    print("\n🔗 Checking YUETransfer integration...")
    yuetransfer_errors = validate_yuetransfer()
    if yuetransfer_errors:
        print("❌ YUETransfer configuration errors:")
        for error in yuetransfer_errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ YUETransfer integration is configured")
    
    # Check TotalSegmentator integration
    print("\n🔗 Checking TotalSegmentator integration...")
    if is_totalsegmentator_available():
        print("✅ TotalSegmentator is available")
    else:
        print("⚠️  TotalSegmentator is not available (will be configured later)")
    
    print("\n✅ All system requirements are met!")
    return True

def main():
    """Main application entry point"""
    print("🚀 Starting YUEUPLOAD - Advanced DICOM Upload System")
    print("=" * 60)
    
    # Check system requirements
    if not check_system_requirements():
        print("\n❌ System requirements not met. Please fix the issues above.")
        suggest_conda_environment()
        sys.exit(1)
    
    # Create Flask app
    app = create_app()
    
    # Get configuration
    config = app.config
    
    # Print startup information
    print(f"\n📋 Configuration:")
    print(f"   - Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"   - Python Version: {sys.version}")
    print(f"   - Debug Mode: {config.get('DEBUG', False)}")
    print(f"   - Upload Folder: {config.get('UPLOAD_FOLDER', 'Not set')}")
    print(f"   - Max File Size: {config.get('MAX_CONTENT_LENGTH', 0) // (1024**3)}GB")
    
    print(f"\n🌐 Server Information:")
    print(f"   - YUEUPLOAD: http://localhost:5001")
    print(f"   - YUETransfer: {config.get('YUETRANSFER_URL', 'http://localhost:5000')}")
    print(f"   - TotalSegmentator: {config.get('TOTALSEGMENTATOR_URL', 'http://localhost:8000')}")
    
    print(f"\n📁 File Structure:")
    print(f"   - User Files: {config.get('USER_FILES_ROOT', '../user_files')}")
    print(f"   - Uploads: {config.get('UPLOAD_FOLDER', 'uploads/')}")
    print(f"   - Logs: {config.get('LOG_FILE', 'logs/')}")
    
    print(f"\n🎯 Ready to start Sprint 1 implementation!")
    print("=" * 60)
    
    # Run the application
    try:
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=config.get('DEBUG', True),
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 YUEUPLOAD stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting YUEUPLOAD: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()