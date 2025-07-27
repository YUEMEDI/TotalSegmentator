#!/usr/bin/env python3
"""
Simple and reliable web-based 3D viewer for TotalSegmentator results
Uses a stable Three.js approach that works across versions
"""

import os
import json
import webbrowser
from pathlib import Path

def create_simple_web_viewer(mesh_directory="web3d_export"):
    """Create a simple, reliable web viewer using Three.js"""
    
    # Find mesh files
    mesh_dir = Path(mesh_directory)
    stl_files = list(mesh_dir.glob("*.stl"))
    obj_files = list(mesh_dir.glob("*.obj"))
    
    all_files = stl_files + obj_files
    
    if not all_files:
        print(f"No mesh files found in {mesh_directory}")
        return None
    
    # Create viewer directory
    viewer_dir = mesh_dir / "simple_viewer"
    viewer_dir.mkdir(exist_ok=True)
    
    # Copy mesh files to viewer directory
    import shutil
    viewer_files = []
    for mesh_file in all_files:
        dest_file = viewer_dir / mesh_file.name
        shutil.copy2(mesh_file, dest_file)
        viewer_files.append(mesh_file.name)
    
    # Create HTML with embedded Three.js (more reliable)
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TotalSegmentator 3D Viewer</title>
    <style>
        body {{ 
            margin: 0; 
            overflow: hidden; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a1a;
        }}
        
        #container {{ 
            position: relative; 
            width: 100vw; 
            height: 100vh; 
        }}
        
        #controls {{ 
            position: absolute; 
            top: 20px; 
            left: 20px; 
            z-index: 100;
            background: rgba(0,0,0,0.8); 
            color: white; 
            padding: 20px;
            border-radius: 10px; 
            max-width: 320px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }}
        
        #controls h3 {{
            margin-top: 0;
            color: #4CAF50;
        }}
        
        .button-group {{
            margin: 15px 0;
        }}
        
        .button-group button {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 15px;
            margin: 2px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
        }}
        
        .button-group button:hover {{
            background: #45a049;
        }}
        
        .organ-control {{ 
            margin: 8px 0; 
            display: flex;
            align-items: center;
        }}
        
        .organ-control input {{ 
            margin-right: 10px; 
            transform: scale(1.2);
        }}
        
        .organ-control label {{
            font-size: 13px;
            cursor: pointer;
        }}
        
        #info {{ 
            position: absolute; 
            bottom: 20px; 
            left: 20px; 
            z-index: 100;
            background: rgba(0,0,0,0.8); 
            color: white; 
            padding: 15px;
            border-radius: 10px; 
            font-size: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }}
        
        #loading {{ 
            position: absolute; 
            top: 50%; 
            left: 50%; 
            transform: translate(-50%, -50%);
            color: white; 
            font-size: 24px; 
            z-index: 200;
            text-align: center;
        }}
        
        .loading-spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #4CAF50;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="loading">
            <div class="loading-spinner"></div>
            <div>Loading 3D Models...</div>
            <div style="font-size: 14px; margin-top: 10px;">Please wait while we load your segmentations</div>
        </div>
        
        <div id="controls" style="display: none;">
            <h3>🎯 TotalSegmentator 3D</h3>
            <div class="button-group">
                <button onclick="resetCamera()">🔄 Reset View</button>
                <button onclick="toggleWireframe()">📐 Wireframe</button>
                <button onclick="toggleAnimation()">🔄 Auto Rotate</button>
            </div>
            <hr style="border-color: #333;">
            <div id="organ-controls"></div>
        </div>
        
        <div id="info" style="display: none;">
            <div><strong>Controls:</strong></div>
            <div>🖱️ Left Click + Drag: Rotate</div>
            <div>🖱️ Right Click + Drag: Pan</div>
            <div>⚡ Mouse Wheel: Zoom</div>
            <div style="margin-top: 10px;">
                <strong>Loaded:</strong> <span id="mesh-count">0</span> organs
            </div>
        </div>
    </div>

    <!-- Use a reliable CDN -->
    <script src="https://cdn.jsdelivr.net/npm/three@0.152.2/build/three.min.js"></script>
    
    <script>
        // Global variables
        let scene, camera, renderer, controls;
        let meshes = {{}};
        let animating = false;
        let wireframeMode = false;
        let loadedCount = 0;

        // Simple orbit controls implementation
        class SimpleOrbitControls {{
            constructor(camera, domElement) {{
                this.camera = camera;
                this.domElement = domElement;
                this.target = new THREE.Vector3();
                
                this.mouseButtons = {{
                    LEFT: THREE.MOUSE.ROTATE,
                    MIDDLE: THREE.MOUSE.DOLLY,
                    RIGHT: THREE.MOUSE.PAN
                }};
                
                this.enableDamping = true;
                this.dampingFactor = 0.1;
                
                this.minDistance = 0;
                this.maxDistance = Infinity;
                
                this.spherical = new THREE.Spherical();
                this.sphericalDelta = new THREE.Spherical();
                
                this.panOffset = new THREE.Vector3();
                this.zoomChanged = false;
                
                this.rotateStart = new THREE.Vector2();
                this.rotateEnd = new THREE.Vector2();
                this.rotateDelta = new THREE.Vector2();
                
                this.panStart = new THREE.Vector2();
                this.panEnd = new THREE.Vector2();
                this.panDelta = new THREE.Vector2();
                
                this.dollyStart = new THREE.Vector2();
                this.dollyEnd = new THREE.Vector2();
                this.dollyDelta = new THREE.Vector2();
                
                this.state = 'NONE';
                
                this.addEventListeners();
            }}
            
            addEventListeners() {{
                this.domElement.addEventListener('mousedown', this.onMouseDown.bind(this));
                this.domElement.addEventListener('wheel', this.onMouseWheel.bind(this));
                this.domElement.addEventListener('contextmenu', (e) => e.preventDefault());
            }}
            
            onMouseDown(event) {{
                event.preventDefault();
                
                switch (event.button) {{
                    case 0: // left
                        this.state = 'ROTATE';
                        this.rotateStart.set(event.clientX, event.clientY);
                        break;
                    case 2: // right
                        this.state = 'PAN';
                        this.panStart.set(event.clientX, event.clientY);
                        break;
                }}
                
                document.addEventListener('mousemove', this.onMouseMove.bind(this));
                document.addEventListener('mouseup', this.onMouseUp.bind(this));
            }}
            
            onMouseMove(event) {{
                event.preventDefault();
                
                if (this.state === 'ROTATE') {{
                    this.rotateEnd.set(event.clientX, event.clientY);
                    this.rotateDelta.subVectors(this.rotateEnd, this.rotateStart);
                    
                    this.sphericalDelta.theta -= 2 * Math.PI * this.rotateDelta.x / this.domElement.clientHeight;
                    this.sphericalDelta.phi -= 2 * Math.PI * this.rotateDelta.y / this.domElement.clientHeight;
                    
                    this.rotateStart.copy(this.rotateEnd);
                }} else if (this.state === 'PAN') {{
                    this.panEnd.set(event.clientX, event.clientY);
                    this.panDelta.subVectors(this.panEnd, this.panStart);
                    
                    this.pan(this.panDelta.x, this.panDelta.y);
                    
                    this.panStart.copy(this.panEnd);
                }}
            }}
            
            onMouseUp() {{
                document.removeEventListener('mousemove', this.onMouseMove.bind(this));
                document.removeEventListener('mouseup', this.onMouseUp.bind(this));
                this.state = 'NONE';
            }}
            
            onMouseWheel(event) {{
                event.preventDefault();
                
                if (event.deltaY < 0) {{
                    this.dollyIn();
                }} else if (event.deltaY > 0) {{
                    this.dollyOut();
                }}
            }}
            
            dollyIn() {{
                this.spherical.radius *= 0.95;
            }}
            
            dollyOut() {{
                this.spherical.radius *= 1.05;
            }}
            
            pan(deltaX, deltaY) {{
                const offset = new THREE.Vector3();
                offset.copy(this.camera.position).sub(this.target);
                
                let targetDistance = offset.length();
                targetDistance *= Math.tan((this.camera.fov / 2) * Math.PI / 180.0);
                
                const panLeft = new THREE.Vector3();
                panLeft.setFromMatrixColumn(this.camera.matrix, 0);
                panLeft.multiplyScalar(-2 * deltaX * targetDistance / this.domElement.clientHeight);
                
                const panUp = new THREE.Vector3();
                panUp.setFromMatrixColumn(this.camera.matrix, 1);
                panUp.multiplyScalar(2 * deltaY * targetDistance / this.domElement.clientHeight);
                
                this.panOffset.copy(panLeft).add(panUp);
            }}
            
            update() {{
                const offset = new THREE.Vector3();
                offset.copy(this.camera.position).sub(this.target);
                
                this.spherical.setFromVector3(offset);
                
                this.spherical.theta += this.sphericalDelta.theta;
                this.spherical.phi += this.sphericalDelta.phi;
                
                this.spherical.makeSafe();
                
                this.spherical.radius = Math.max(this.minDistance, Math.min(this.maxDistance, this.spherical.radius));
                
                this.target.add(this.panOffset);
                
                offset.setFromSpherical(this.spherical);
                this.camera.position.copy(this.target).add(offset);
                this.camera.lookAt(this.target);
                
                if (this.enableDamping) {{
                    this.sphericalDelta.theta *= (1 - this.dampingFactor);
                    this.sphericalDelta.phi *= (1 - this.dampingFactor);
                    this.panOffset.multiplyScalar(1 - this.dampingFactor);
                }} else {{
                    this.sphericalDelta.set(0, 0, 0);
                    this.panOffset.set(0, 0, 0);
                }}
            }}
        }}

        function init() {{
            // Scene
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1a1a1a);

            // Camera
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 10000);
            camera.position.set(50, 50, 100);

            // Renderer
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            document.getElementById('container').appendChild(renderer.domElement);

            // Controls
            controls = new SimpleOrbitControls(camera, renderer.domElement);

            // Lights
            const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
            scene.add(ambientLight);

            const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight1.position.set(100, 100, 50);
            scene.add(directionalLight1);
            
            const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
            directionalLight2.position.set(-100, -100, -50);
            scene.add(directionalLight2);

            // Load meshes
            loadMeshes();

            // Animation loop
            animate();
        }}

        function loadMeshes() {{
            const meshFiles = {json.dumps(viewer_files)};
            const colors = [
                0xff6b6b, 0x4ecdc4, 0x45b7d1, 0x96ceb4, 0xffeaa7,
                0xdda0dd, 0x98d8c8, 0xf7dc6f, 0xbb8fce, 0x85c1e9,
                0xff9ff3, 0x54a0ff, 0x5f27cd, 0x00d2d3, 0xff9f43
            ];

            const controlsDiv = document.getElementById('organ-controls');

            meshFiles.forEach((file, index) => {{
                const organName = file.replace(/\\.(stl|obj)$/, '').replace(/_/g, ' ');
                const color = colors[index % colors.length];

                if (file.endsWith('.stl')) {{
                    loadSTL(file, organName, color, controlsDiv);
                }}
            }});
        }}

        function loadSTL(filename, organName, color, controlsDiv) {{
            const loader = new THREE.STLLoader();
            
            loader.load(filename, function(geometry) {{
                const material = new THREE.MeshPhongMaterial({{ 
                    color: color, 
                    transparent: true, 
                    opacity: 0.85,
                    side: THREE.DoubleSide
                }});
                
                const mesh = new THREE.Mesh(geometry, material);
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
                
                if (loadedCount === 1) {{
                    // Show controls after first mesh loads
                    document.getElementById('controls').style.display = 'block';
                    document.getElementById('info').style.display = 'block';
                }}
                
                if (loadedCount === {json.dumps(len([f for f in viewer_files if f.endswith('.stl')]))}) {{
                    document.getElementById('loading').style.display = 'none';
                    fitCameraToScene();
                }}
            }}, undefined, function(error) {{
                console.error('Error loading', filename, error);
                loadedCount++;
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
                if (mesh.material) {{
                    mesh.material.wireframe = wireframeMode;
                }}
            }});
        }}

        function toggleAnimation() {{
            animating = !animating;
        }}

        function fitCameraToScene() {{
            if (Object.keys(meshes).length === 0) return;
            
            const box = new THREE.Box3();
            Object.values(meshes).forEach(mesh => {{
                if (mesh.visible) {{
                    box.expandByObject(mesh);
                }}
            }});
            
            if (box.isEmpty()) return;
            
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            
            const maxDim = Math.max(size.x, size.y, size.z);
            const fov = camera.fov * (Math.PI / 180);
            const cameraDistance = Math.abs(maxDim / 2 / Math.tan(fov / 2)) * 2;
            
            camera.position.copy(center);
            camera.position.z += cameraDistance;
            camera.position.y += cameraDistance * 0.3;
            camera.lookAt(center);
            controls.target.copy(center);
        }}

        function animate() {{
            requestAnimationFrame(animate);
            
            if (animating) {{
                Object.values(meshes).forEach(mesh => {{
                    mesh.rotation.y += 0.003;
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
        
        // STL Loader implementation
        THREE.STLLoader = function() {{}};
        THREE.STLLoader.prototype = {{
            load: function(url, onLoad, onProgress, onError) {{
                const loader = new THREE.FileLoader();
                loader.setResponseType('arraybuffer');
                loader.load(url, function(buffer) {{
                    try {{
                        const geometry = parseSTL(buffer);
                        onLoad(geometry);
                    }} catch (e) {{
                        if (onError) onError(e);
                    }}
                }}, onProgress, onError);
            }}
        }};

        function parseSTL(buffer) {{
            const dataview = new DataView(buffer);
            const isLittleEndian = true;

            // Check if binary or ASCII
            const header = new Uint8Array(buffer, 0, 80);
            let isBinary = true;
            
            // Simple binary check
            if (dataview.getUint32(80, isLittleEndian) * 50 + 84 !== buffer.byteLength) {{
                // Might be ASCII, but let's try binary first
            }}

            if (isBinary) {{
                return parseBinarySTL(dataview, isLittleEndian);
            }} else {{
                return parseASCIISTL(buffer);
            }}
        }}

        function parseBinarySTL(dataview, isLittleEndian) {{
            const faces = dataview.getUint32(80, isLittleEndian);
            const geometry = new THREE.BufferGeometry();
            
            const vertices = [];
            const normals = [];
            
            for (let face = 0; face < faces; face++) {{
                const start = 84 + face * 50;
                
                // Normal
                const nx = dataview.getFloat32(start, isLittleEndian);
                const ny = dataview.getFloat32(start + 4, isLittleEndian);
                const nz = dataview.getFloat32(start + 8, isLittleEndian);
                
                // Vertices
                for (let i = 0; i < 3; i++) {{
                    const vertexstart = start + 12 + i * 12;
                    vertices.push(
                        dataview.getFloat32(vertexstart, isLittleEndian),
                        dataview.getFloat32(vertexstart + 4, isLittleEndian),
                        dataview.getFloat32(vertexstart + 8, isLittleEndian)
                    );
                    normals.push(nx, ny, nz);
                }}
            }}
            
            geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
            geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
            
            return geometry;
        }}

        // Initialize when page loads
        window.addEventListener('load', init);
    </script>
</body>
</html>
    """
    
    # Save HTML file
    html_path = viewer_dir / "index.html"
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    print(f"✅ Simple web viewer created: {html_path}")
    
    # Open in browser
    webbrowser.open(f'file://{html_path.absolute()}')
    
    return str(html_path)

if __name__ == "__main__":
    create_simple_web_viewer("web3d_export") 