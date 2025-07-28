#!/usr/bin/env python3
"""
Test script to verify TotalSegmentator installation
"""

import sys
import os

def test_installation():
    print("🧪 Testing TotalSegmentator Installation")
    print("=" * 50)
    
    # Test Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Test PyTorch
    try:
        import torch
        print(f"🔥 PyTorch version: {torch.__version__}")
        print(f"🎮 CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"🎮 CUDA version: {torch.version.cuda}")
            print(f"🎮 GPU count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"🎮 GPU {i}: {torch.cuda.get_device_name(i)}")
        else:
            print("⚠️  CUDA not available - will use CPU")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    # Test TensorFlow
    try:
        import tensorflow as tf
        print(f"🧠 TensorFlow version: {tf.__version__}")
        gpus = tf.config.list_physical_devices('GPU')
        print(f"🎮 TensorFlow GPU devices: {len(gpus)}")
        for gpu in gpus:
            print(f"🎮 GPU: {gpu.name}")
    except ImportError as e:
        print(f"❌ TensorFlow import failed: {e}")
        return False
    
    # Test TotalSegmentator
    try:
        import totalsegmentator
        print(f"🏥 TotalSegmentator version: {totalsegmentator.__version__}")
        print("✅ TotalSegmentator import successful!")
    except ImportError as e:
        print(f"❌ TotalSegmentator import failed: {e}")
        return False
    
    # Test other key packages
    packages = ['numpy', 'scipy', 'nibabel', 'SimpleITK', 'nnunetv2']
    for pkg in packages:
        try:
            module = __import__(pkg)
            version = getattr(module, '__version__', 'Unknown')
            print(f"✅ {pkg}: {version}")
        except ImportError:
            print(f"❌ {pkg}: Not found")
    
    print("\n" + "=" * 50)
    print("🎉 Installation test completed!")
    return True

if __name__ == "__main__":
    success = test_installation()
    if success:
        print("✅ All tests passed! TotalSegmentator is ready to use.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the installation.")
        sys.exit(1) 