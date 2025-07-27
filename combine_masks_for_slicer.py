#!/usr/bin/env python3
"""
Combine TotalSegmentator binary masks into a single multi-label volume for 3D Slicer
"""

import nibabel as nib
import numpy as np
import os
import glob

def combine_masks_for_slicer(input_dir="test_output", output_file="combined_segmentation.nii.gz"):
    """
    Combine binary masks into a single multi-label volume
    """
    
    # Get all .nii.gz files
    mask_files = glob.glob(os.path.join(input_dir, "*.nii.gz"))
    
    if not mask_files:
        print(f"No .nii.gz files found in {input_dir}")
        return
    
    print(f"Found {len(mask_files)} mask files")
    
    # Load first mask to get dimensions
    first_img = nib.load(mask_files[0])
    combined_data = np.zeros(first_img.shape, dtype=np.uint16)
    
    label_names = []
    
    for i, mask_file in enumerate(mask_files, 1):
        print(f"Processing {os.path.basename(mask_file)}...")
        
        try:
            img = nib.load(mask_file)
            data = img.get_fdata()
            
            # Add this mask with label value i
            mask_indices = data > 0.5  # Binary threshold
            combined_data[mask_indices] = i
            
            # Store label name
            label_name = os.path.basename(mask_file).replace('.nii.gz', '')
            label_names.append(f"{i}: {label_name}")
            
        except Exception as e:
            print(f"Error processing {mask_file}: {e}")
            continue
    
    # Save combined volume
    combined_img = nib.Nifti1Image(combined_data, first_img.affine, first_img.header)
    nib.save(combined_img, output_file)
    
    # Save label mapping
    with open("label_mapping.txt", "w") as f:
        f.write("Label Mapping for 3D Slicer:\n")
        f.write("=" * 30 + "\n")
        for label in label_names:
            f.write(label + "\n")
    
    print(f"\nCombined segmentation saved as: {output_file}")
    print(f"Label mapping saved as: label_mapping.txt")
    print(f"Total labels: {len(label_names)}")
    
    return output_file

if __name__ == "__main__":
    combine_masks_for_slicer() 