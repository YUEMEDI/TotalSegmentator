#!/usr/bin/env python3
"""
Fix NIfTI files for 3D Slicer compatibility
"""

import nibabel as nib
import numpy as np
import os

def fix_nifti_for_slicer(input_file, output_file=None):
    """
    Fix common NIfTI issues that prevent 3D Slicer from loading files
    """
    
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        if ext == '.gz':
            base, _ = os.path.splitext(base)
        output_file = f"{base}_fixed.nii.gz"
    
    print(f"Fixing {input_file} -> {output_file}")
    
    # Load the image
    img = nib.load(input_file)
    data = img.get_fdata()
    
    print(f"Original shape: {img.shape}")
    print(f"Original data type: {data.dtype}")
    print(f"Original value range: {data.min()} to {data.max()}")
    
    # Fix 1: Ensure proper data type for segmentations
    if data.max() <= 255:
        data_fixed = data.astype(np.uint8)
    elif data.max() <= 65535:
        data_fixed = data.astype(np.uint16)
    else:
        data_fixed = data.astype(np.uint32)
    
    # Fix 2: Ensure no NaN or infinite values
    data_fixed = np.nan_to_num(data_fixed, nan=0, posinf=0, neginf=0)
    
    # Fix 3: Create new header with proper settings
    new_header = img.header.copy()
    
    # Set proper datatype in header
    new_header.set_data_dtype(data_fixed.dtype)
    
    # Fix scaling parameters that often cause issues
    new_header['scl_slope'] = 1.0
    new_header['scl_inter'] = 0.0
    
    # Set proper intent for segmentation
    new_header['intent_code'] = 0  # No specific intent
    
    # Ensure proper orientation info
    new_header['qform_code'] = 1  # Scanner coordinates
    new_header['sform_code'] = 1  # Scanner coordinates
    
    # Fix 4: Ensure proper affine matrix
    affine = img.affine.copy()
    
    # Create the fixed image
    fixed_img = nib.Nifti1Image(data_fixed, affine, new_header)
    
    # Save the fixed image
    nib.save(fixed_img, output_file)
    
    print(f"Fixed file saved as: {output_file}")
    print(f"New data type: {data_fixed.dtype}")
    print(f"New value range: {data_fixed.min()} to {data_fixed.max()}")
    
    return output_file

def create_simple_test_volume():
    """
    Create a simple test volume that should definitely work in Slicer
    """
    print("Creating simple test volume...")
    
    # Create a simple 3D volume with basic shapes
    shape = (64, 64, 32)
    data = np.zeros(shape, dtype=np.uint8)
    
    # Add some simple geometric shapes
    # Sphere in center
    center = (32, 32, 16)
    radius = 10
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                dist = np.sqrt((i-center[0])**2 + (j-center[1])**2 + (k-center[2])**2)
                if dist < radius:
                    data[i, j, k] = 1
    
    # Add a cube
    data[10:20, 10:20, 5:15] = 2
    
    # Create proper affine matrix (1mm isotropic)
    affine = np.array([
        [1.0, 0.0, 0.0, -32.0],
        [0.0, 1.0, 0.0, -32.0],
        [0.0, 0.0, 1.0, -16.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    
    # Create NIfTI image
    img = nib.Nifti1Image(data, affine)
    
    # Set proper header
    header = img.header
    header.set_data_dtype(np.uint8)
    header['scl_slope'] = 1.0
    header['scl_inter'] = 0.0
    header['qform_code'] = 1
    header['sform_code'] = 1
    
    # Save test volume
    test_file = "test_volume_for_slicer.nii.gz"
    nib.save(img, test_file)
    
    print(f"Test volume created: {test_file}")
    print("This file should definitely load in 3D Slicer as a LabelMap")
    
    return test_file

if __name__ == "__main__":
    # Fix the combined segmentation
    if os.path.exists("combined_segmentation.nii.gz"):
        fix_nifti_for_slicer("combined_segmentation.nii.gz")
    
    # Fix a single mask file as example
    if os.path.exists("test_output/liver.nii.gz"):
        fix_nifti_for_slicer("test_output/liver.nii.gz")
    
    # Create a simple test volume
    create_simple_test_volume() 