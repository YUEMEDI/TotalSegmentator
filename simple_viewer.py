#!/usr/bin/env python3
"""
Simple web-based viewer for TotalSegmentator results
"""

import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import webbrowser
import tempfile
import os

def create_simple_viewer():
    """Create a simple HTML viewer for segmentation results"""
    
    # Load original image
    original_path = "tests/reference_files/example_ct_sm.nii.gz"
    if os.path.exists(original_path):
        original_img = nib.load(original_path)
        original_data = original_img.get_fdata()
    else:
        print(f"Original image not found: {original_path}")
        return
    
    # Get segmentation files
    seg_dir = Path("test_output")
    seg_files = list(seg_dir.glob("*.nii.gz"))
    
    if not seg_files:
        print("No segmentation files found in test_output/")
        return
    
    # Load a few key segmentations
    key_organs = ['brain', 'heart', 'liver', 'spleen', 'kidney_left', 'kidney_right']
    seg_data = {}
    
    for organ in key_organs:
        for seg_file in seg_files:
            if organ in seg_file.name:
                seg_img = nib.load(seg_file)
                seg_data[organ] = seg_img.get_fdata()
                break
    
    # Create visualization
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('TotalSegmentator Results - Key Organs', fontsize=16)
    
    # Get middle slice
    mid_slice = original_data.shape[2] // 2
    
    # Plot original image
    axes[0, 0].imshow(original_data[:, :, mid_slice], cmap='gray')
    axes[0, 0].set_title('Original CT Image')
    axes[0, 0].axis('off')
    
    # Plot segmentations
    for i, (organ, data) in enumerate(seg_data.items()):
        row = (i + 1) // 3
        col = (i + 1) % 3
        
        if row < 2:  # Only plot if we have space
            axes[row, col].imshow(original_data[:, :, mid_slice], cmap='gray', alpha=0.7)
            axes[row, col].imshow(data[:, :, mid_slice], cmap='hot', alpha=0.5)
            axes[row, col].set_title(f'{organ.replace("_", " ").title()}')
            axes[row, col].axis('off')
    
    # Save to HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TotalSegmentator Results</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .info {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            .files {{ background: #e8f4f8; padding: 15px; border-radius: 5px; }}
            .file-list {{ max-height: 300px; overflow-y: auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 TotalSegmentator Results Viewer</h1>
            
            <div class="info">
                <h3>📊 Segmentation Summary</h3>
                <p><strong>Total files generated:</strong> {len(seg_files)}</p>
                <p><strong>Image dimensions:</strong> {original_data.shape}</p>
                <p><strong>Key organs segmented:</strong> {', '.join(seg_data.keys())}</p>
            </div>
            
            <div class="files">
                <h3>📁 Generated Files</h3>
                <div class="file-list">
                    {''.join([f'<div>• {f.name}</div>' for f in seg_files[:20]])}
                    {f'<div><em>... and {len(seg_files) - 20} more files</em></div>' if len(seg_files) > 20 else ''}
                </div>
            </div>
            
            <div class="info">
                <h3>🔗 Recommended Viewers</h3>
                <ul>
                    <li><a href="https://viewer.ohif.org/" target="_blank">OHIF Viewer</a> - Professional medical image viewer</li>
                    <li><a href="https://totalsegmentator.com/" target="_blank">TotalSegmentator Web Interface</a> - Official web tool</li>
                    <li><a href="https://niivue.github.io/niivue/" target="_blank">NiiVue</a> - Modern NIfTI viewer</li>
                </ul>
            </div>
            
            <div class="info">
                <h3>💡 How to View Your Results</h3>
                <ol>
                    <li>Go to <a href="https://viewer.ohif.org/" target="_blank">OHIF Viewer</a></li>
                    <li>Drag and drop your original CT file: <code>tests/reference_files/example_ct_sm.nii.gz</code></li>
                    <li>Drag and drop segmentation files from <code>test_output/</code> folder</li>
                    <li>Use the viewer controls to explore the 3D data</li>
                </ol>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Save HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        html_path = f.name
    
    # Open in browser
    webbrowser.open(f'file://{html_path}')
    print(f"🌐 Web viewer opened in browser: {html_path}")
    
    # Save the matplotlib figure
    plt.savefig('segmentation_preview.png', dpi=150, bbox_inches='tight')
    print("📸 Preview image saved as: segmentation_preview.png")

if __name__ == "__main__":
    create_simple_viewer() 