#!/usr/bin/env python3
"""
Simple HTTP server to serve TotalSegmentator 3D web viewer
Solves CORS issues when loading STL files locally
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path
import threading
import time

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to set proper CORS headers and content types"""
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        # Set proper content types
        if self.path.endswith('.stl'):
            self.send_header('Content-Type', 'application/octet-stream')
        elif self.path.endswith('.obj'):
            self.send_header('Content-Type', 'text/plain')
        elif self.path.endswith('.html'):
            self.send_header('Content-Type', 'text/html')
        elif self.path.endswith('.js'):
            self.send_header('Content-Type', 'application/javascript')
            
        super().end_headers()
    
    def log_message(self, format, *args):
        """Suppress log messages except for errors"""
        if "GET" in format and ("200" in format or "304" in format):
            return  # Suppress successful GET requests
        super().log_message(format, *args)

def find_available_port(start_port=8000, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as server:
                return port
        except OSError:
            continue
    return None

def serve_web3d_viewer(directory="web3d_export/simple_viewer", port=None, auto_open=True):
    """
    Start a local web server to serve the 3D viewer
    
    Args:
        directory: Directory containing the web viewer files
        port: Port to use (auto-detect if None)
        auto_open: Whether to automatically open browser
    """
    
    viewer_path = Path(directory)
    
    if not viewer_path.exists():
        print(f"❌ Directory not found: {directory}")
        print("Run the 3D export script first to generate the viewer")
        return None
    
    # Check for required files
    html_file = viewer_path / "index.html"
    if not html_file.exists():
        print(f"❌ index.html not found in {directory}")
        return None
    
    # Find STL files
    stl_files = list(viewer_path.glob("*.stl"))
    if not stl_files:
        print(f"⚠️  No STL files found in {directory}")
    
    # Find available port
    if port is None:
        port = find_available_port()
        if port is None:
            print("❌ Could not find available port")
            return None
    
    # Change to the viewer directory
    original_dir = os.getcwd()
    os.chdir(viewer_path)
    
    try:
        # Create server
        with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
            server_url = f"http://localhost:{port}"
            
            print(f"🌐 Starting web server...")
            print(f"📁 Serving directory: {viewer_path.absolute()}")
            print(f"🔗 Server URL: {server_url}")
            print(f"📊 STL files found: {len(stl_files)}")
            
            # Open browser in a separate thread
            if auto_open:
                def open_browser():
                    time.sleep(1)  # Wait for server to start
                    print(f"🚀 Opening browser: {server_url}")
                    webbrowser.open(server_url)
                
                browser_thread = threading.Thread(target=open_browser)
                browser_thread.daemon = True
                browser_thread.start()
            
            print(f"\n✅ Server running at {server_url}")
            print("Press Ctrl+C to stop the server")
            print("-" * 50)
            
            # Start serving
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        # Restore original directory
        os.chdir(original_dir)

def create_and_serve_viewer(
    input_dir="test_output",
    max_files=10,
    port=None,
    auto_open=True
):
    """
    Complete workflow: create 3D meshes and serve web viewer
    
    Args:
        input_dir: Directory with .nii.gz segmentation files
        max_files: Maximum number of files to process
        port: Port for web server (auto-detect if None)
        auto_open: Whether to open browser automatically
    """
    
    print("🔄 Step 1: Creating 3D meshes from segmentations...")
    
    # Import and run the 3D export
    try:
        from export_to_web3d import export_totalsegmentator_to_web3d
        
        export_totalsegmentator_to_web3d(
            input_dir=input_dir,
            output_dir="web3d_export",
            formats=["stl"],  # Focus on STL for web viewing
            max_files=max_files,
            create_viewer=False  # We'll create our own
        )
        
    except ImportError:
        print("❌ Could not import export_to_web3d module")
        return
    
    print("🔄 Step 2: Creating web viewer...")
    
    # Create simple viewer
    try:
        from simple_web3d_viewer import create_simple_web_viewer
        
        create_simple_web_viewer("web3d_export")
        
    except ImportError:
        print("❌ Could not import simple_web3d_viewer module")
        return
    
    print("🔄 Step 3: Starting web server...")
    
    # Serve the viewer
    serve_web3d_viewer(
        directory="web3d_export/simple_viewer",
        port=port,
        auto_open=auto_open
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Serve TotalSegmentator 3D Web Viewer")
    parser.add_argument("--directory", "-d", default="web3d_export/simple_viewer",
                       help="Directory containing the web viewer")
    parser.add_argument("--port", "-p", type=int, default=None,
                       help="Port to use (auto-detect if not specified)")
    parser.add_argument("--no-browser", action="store_true",
                       help="Don't automatically open browser")
    parser.add_argument("--create", action="store_true",
                       help="Create viewer from scratch (requires segmentation files)")
    parser.add_argument("--input-dir", default="test_output",
                       help="Input directory with .nii.gz files (when using --create)")
    parser.add_argument("--max-files", type=int, default=10,
                       help="Maximum number of files to process (when using --create)")
    
    args = parser.parse_args()
    
    if args.create:
        # Create and serve
        create_and_serve_viewer(
            input_dir=args.input_dir,
            max_files=args.max_files,
            port=args.port,
            auto_open=not args.no_browser
        )
    else:
        # Just serve existing viewer
        serve_web3d_viewer(
            directory=args.directory,
            port=args.port,
            auto_open=not args.no_browser
        ) 