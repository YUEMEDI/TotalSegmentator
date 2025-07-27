#!/usr/bin/env python3
"""
Export TotalSegmentator results to web-based 3D formats
Supports: STL, OBJ, PLY, GLTF, and web viewers
"""

import nibabel as nib
import numpy as np
from pathlib import Path
import json
import tempfile
import webbrowser
import os
from typing import List, Dict, Optional

def nifti_to_stl(nifti_path: str, output_path: str, threshold: float = 0.5):
    """Convert NIfTI segmentation to STL mesh using marching cubes"""
    try:
        from skimage import measure
        import trimesh
        
        # Load NIfTI file
        img = nib.load(nifti_path)
        data = img.get_fdata()
        
        # Apply threshold for binary mask
        binary_mask = data > threshold
        
        if not np.any(binary_mask):
            print(f"Warning: No voxels above threshold {threshold} in {nifti_path}")
            return None
        
        # Generate mesh using marching cubes
        verts, faces, normals, values = measure.marching_cubes(binary_mask, level=0.5)
        
        # Apply voxel spacing (from NIfTI header)
        spacing = img.header.get_zooms()[:3]
        verts = verts * spacing
        
        # Create mesh
        mesh = trimesh.Trimesh(vertices=verts, faces=faces)
        
        # Export to STL
        mesh.export(output_path, file_type='stl')
        print(f"✅ STL exported: {output_path}")
        
        return output_path
        
    except ImportError:
        print("❌ Missing dependencies. Install: pip install scikit-image trimesh")
        return None
    except Exception as e:
        print(f"❌ Error converting {nifti_path}: {e}")
        return None

def nifti_to_obj(nifti_path: str, output_path: str, threshold: float = 0.5):
    """Convert NIfTI segmentation to OBJ mesh"""
    try:
        from skimage import measure
        
        # Load NIfTI file
        img = nib.load(nifti_path)
        data = img.get_fdata()
        
        # Apply threshold
        binary_mask = data > threshold
        
        if not np.any(binary_mask):
            return None
        
        # Generate mesh
        verts, faces, normals, values = measure.marching_cubes(binary_mask, level=0.5)
        
        # Apply spacing
        spacing = img.header.get_zooms()[:3]
        verts = verts * spacing
        
        # Write OBJ file
        with open(output_path, 'w') as f:
            f.write("# OBJ file generated from TotalSegmentator\n")
            f.write(f"# Source: {nifti_path}\n\n")
            
            # Write vertices
            for v in verts:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            
            # Write faces (OBJ uses 1-based indexing)
            for face in faces:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
        
        print(f"✅ OBJ exported: {output_path}")
        return output_path
        
    except ImportError:
        print("❌ Missing dependencies. Install: pip install scikit-image")
        return None
    except Exception as e:
        print(f"❌ Error converting {nifti_path}: {e}")
        return None

def create_three_js_viewer(mesh_files: List[str], output_dir: str = "web_viewer"):
    """Create a Three.js web viewer for the 3D meshes"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # HTML template with Three.js viewer
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TotalSegmentator 3D Viewer</title>
    <style>
        body {{ margin: 0; overflow: hidden; font-family: Arial, sans-serif; }}
        #container {{ position: relative; width: 100vw; height: 100vh; }}
        #controls {{ 
            position: absolute; top: 10px; left: 10px; z-index: 100;
            background: rgba(0,0,0,0.7); color: white; padding: 15px;
            border-radius: 5px; max-width: 300px;
        }}
        #info {{ 
            position: absolute; bottom: 10px; left: 10px; z-index: 100;
            background: rgba(0,0,0,0.7); color: white; padding: 10px;
            border-radius: 5px; font-size: 12px;
        }}
        .organ-control {{ margin: 5px 0; }}
        .organ-control input {{ margin-right: 8px; }}
        #loading {{ 
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            color: white; font-size: 18px; z-index: 200;
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="loading">Loading 3D models...</div>
        <div id="controls">
            <h3>🎯 TotalSegmentator 3D Viewer</h3>
            <div>
                <button onclick="resetCamera()">Reset View</button>
                <button onclick="toggleWireframe()">Wireframe</button>
                <button onclick="toggleAnimation()">Rotate</button>
            </div>
            <hr>
            <div id="organ-controls"></div>
        </div>
        <div id="info">
            <div>Mouse: Rotate | Wheel: Zoom | Right-click: Pan</div>
            <div>Meshes loaded: <span id="mesh-count">0</span></div>
        </div>
    </div>

    <!-- Updated Three.js imports for compatibility -->
    <script src="https://unpkg.com/three@0.152.2/build/three.min.js"></script>
    <script src="https://unpkg.com/three@0.152.2/examples/js/controls/OrbitControls.js"></script>
    <script src="https://unpkg.com/three@0.152.2/examples/js/loaders/STLLoader.js"></script>
    <script src="https://unpkg.com/three@0.152.2/examples/js/loaders/OBJLoader.js"></script>

    <script>
        let scene, camera, renderer, controls;
        let meshes = {{}};
        let animating = false;
        let wireframeMode = false;

        function init() {{
            // Scene
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x222222);

            // Camera
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 0, 100);

            // Renderer
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            document.getElementById('container').appendChild(renderer.domElement);

            // Controls - Fixed constructor
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.1;

            // Lights
            const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
            scene.add(ambientLight);

            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(10, 10, 5);
            directionalLight.castShadow = true;
            scene.add(directionalLight);

            // Load meshes
            loadMeshes();

            // Animation loop
            animate();
        }}

        function loadMeshes() {{
            const meshFiles = {json.dumps([os.path.basename(f) for f in mesh_files])};
            const colors = [
                0xff6b6b, 0x4ecdc4, 0x45b7d1, 0x96ceb4, 0xffeaa7,
                0xdda0dd, 0x98d8c8, 0xf7dc6f, 0xbb8fce, 0x85c1e9
            ];

            let loadedCount = 0;
            const controlsDiv = document.getElementById('organ-controls');

            meshFiles.forEach((file, index) => {{
                const organName = file.replace(/\\.(stl|obj)$/, '').replace(/_/g, ' ');
                const color = colors[index % colors.length];

                // Determine loader based on file extension
                let loader;
                if (file.endsWith('.stl')) {{
                    loader = new THREE.STLLoader();
                }} else if (file.endsWith('.obj')) {{
                    loader = new THREE.OBJLoader();
                }}

                loader.load(file, function(geometry) {{
                    let mesh;
                    
                    if (file.endsWith('.stl')) {{
                        const material = new THREE.MeshPhongMaterial({{ 
                            color: color, 
                            transparent: true, 
                            opacity: 0.8,
                            side: THREE.DoubleSide
                        }});
                        mesh = new THREE.Mesh(geometry, material);
                    }} else {{
                        // For OBJ files, geometry is already a group
                        mesh = geometry;
                        mesh.traverse(function(child) {{
                            if (child instanceof THREE.Mesh) {{
                                child.material = new THREE.MeshPhongMaterial({{ 
                                    color: color, 
                                    transparent: true, 
                                    opacity: 0.8,
                                    side: THREE.DoubleSide
                                }});
                            }}
                        }});
                    }}

                    mesh.name = organName;
                    scene.add(mesh);
                    meshes[organName] = mesh;

                    // Add control
                    const control = document.createElement('div');
                    control.className = 'organ-control';
                    control.innerHTML = `
                        <input type="checkbox" id="${{organName}}" checked onchange="toggleMesh('${{organName}}')">
                        <label for="${{organName}}">${{organName}}</label>
                    `;
                    controlsDiv.appendChild(control);

                    loadedCount++;
                    document.getElementById('mesh-count').textContent = loadedCount;
                    
                    if (loadedCount === meshFiles.length) {{
                        document.getElementById('loading').style.display = 'none';
                        fitCameraToScene();
                    }}
                }}, undefined, function(error) {{
                    console.error('Error loading', file, error);
                }});
            }});
        }}

        function toggleMesh(organName) {{
            const mesh = meshes[organName];
            if (mesh) {{
                mesh.visible = !mesh.visible;
            }}
        }}

        function resetCamera() {{
            fitCameraToScene();
        }}

        function toggleWireframe() {{
            wireframeMode = !wireframeMode;
            Object.values(meshes).forEach(mesh => {{
                mesh.traverse(function(child) {{
                    if (child instanceof THREE.Mesh) {{
                        child.material.wireframe = wireframeMode;
                    }}
                }});
            }});
        }}

        function toggleAnimation() {{
            animating = !animating;
        }}

        function fitCameraToScene() {{
            const box = new THREE.Box3();
            Object.values(meshes).forEach(mesh => {{
                box.expandByObject(mesh);
            }});
            
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            
            const maxDim = Math.max(size.x, size.y, size.z);
            const fov = camera.fov * (Math.PI / 180);
            const cameraDistance = Math.abs(maxDim / 2 / Math.tan(fov / 2)) * 1.5;
            
            camera.position.copy(center);
            camera.position.z += cameraDistance;
            camera.lookAt(center);
            controls.target.copy(center);
            controls.update();
        }}

        function animate() {{
            requestAnimationFrame(animate);
            
            if (animating) {{
                Object.values(meshes).forEach(mesh => {{
                    mesh.rotation.y += 0.005;
                }});
            }}
            
            controls.update();
            renderer.render(scene, camera);
        }}

        function onWindowResize() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }}

        window.addEventListener('resize', onWindowResize);
        
        // Initialize when page loads
        init();
    </script>
</body>
</html>
    """
    
    # Save HTML file
    html_path = os.path.join(output_dir, "index.html")
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    return html_path

def export_totalsegmentator_to_web3d(
    input_dir: str = "test_output",
    output_dir: str = "web3d_export",
    formats: List[str] = ["stl", "obj"],
    max_files: int = 10,
    create_viewer: bool = True
):
    """
    Export TotalSegmentator results to web-based 3D formats
    
    Args:
        input_dir: Directory containing .nii.gz segmentation files
        output_dir: Output directory for 3D files
        formats: List of formats to export ("stl", "obj", "ply")
        max_files: Maximum number of files to process (to avoid overwhelming)
        create_viewer: Whether to create a web viewer
    """
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Get segmentation files
    nifti_files = list(input_path.glob("*.nii.gz"))
    
    if not nifti_files:
        print(f"❌ No .nii.gz files found in {input_dir}")
        return
    
    # Limit files to process
    if len(nifti_files) > max_files:
        print(f"⚠️  Found {len(nifti_files)} files, processing first {max_files}")
        nifti_files = nifti_files[:max_files]
    
    print(f"🔄 Processing {len(nifti_files)} segmentation files...")
    
    exported_files = []
    
    for nifti_file in nifti_files:
        organ_name = nifti_file.stem.replace('.nii', '')
        print(f"Processing: {organ_name}")
        
        for fmt in formats:
            output_file = output_path / f"{organ_name}.{fmt}"
            
            if fmt == "stl":
                result = nifti_to_stl(str(nifti_file), str(output_file))
            elif fmt == "obj":
                result = nifti_to_obj(str(nifti_file), str(output_file))
            else:
                print(f"⚠️  Format {fmt} not supported yet")
                continue
            
            if result:
                exported_files.append(str(output_file))
    
    # Create web viewer
    if create_viewer and exported_files:
        print("🌐 Creating web viewer...")
        viewer_dir = output_path / "viewer"
        
        # Copy mesh files to viewer directory
        viewer_dir.mkdir(exist_ok=True)
        viewer_files = []
        
        for mesh_file in exported_files:
            dest_file = viewer_dir / os.path.basename(mesh_file)
            import shutil
            shutil.copy2(mesh_file, dest_file)
            viewer_files.append(str(dest_file))
        
        # Create viewer
        html_path = create_three_js_viewer(viewer_files, str(viewer_dir))
        
        # Open in browser
        webbrowser.open(f'file://{os.path.abspath(html_path)}')
        print(f"✅ Web viewer created: {html_path}")
    
    print(f"\n🎉 Export complete!")
    print(f"📁 Output directory: {output_path}")
    print(f"📊 Files exported: {len(exported_files)}")
    
    return output_path

if __name__ == "__main__":
    # Check dependencies
    try:
        import skimage
        import trimesh
        print("✅ All dependencies available")
    except ImportError:
        print("⚠️  Installing required dependencies...")
        print("Run: pip install scikit-image trimesh")
        exit(1)
    
    # Export to web 3D formats
    export_totalsegmentator_to_web3d(
        input_dir="test_output",
        output_dir="web3d_export",
        formats=["stl", "obj"],
        max_files=10,
        create_viewer=True
    ) 