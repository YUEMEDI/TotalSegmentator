#!/usr/bin/env python3
"""
YueCheck - System Configuration Analysis Tool
Comprehensive system check before YueTransfer and TotalSegmentator setup
"""

import os
import sys
import platform
import subprocess
import json
import socket
import shutil
import psutil
import pkg_resources
from pathlib import Path
from datetime import datetime
import importlib.util
import winreg
import ctypes


class YueSystemChecker:
    def __init__(self):
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'system': {},
            'hardware': {},
            'python': {},
            'conda': {},
            'gpu': {},
            'ai_frameworks': {},
            'network': {},
            'storage': {},
            'permissions': {},
            'conflicts': [],
            'recommendations': [],
            'status': 'unknown'
        }
        
    def run_command(self, cmd, shell=True, capture_output=True):
        """Safely run system commands"""
        try:
            result = subprocess.run(
                cmd, 
                shell=shell, 
                capture_output=capture_output, 
                text=True, 
                timeout=30
            )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except Exception as e:
            return "", str(e), -1
    
    def check_system_info(self):
        """Check operating system and basic system information"""
        print("🔍 Checking system information...")
        
        self.report['system'] = {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'hostname': platform.node(),
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            'uptime_hours': (datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds() / 3600
        }
        
        # Windows specific checks
        if platform.system() == 'Windows':
            try:
                # Get Windows version details
                stdout, _, _ = self.run_command('ver')
                self.report['system']['windows_version'] = stdout
                
                # Check Windows edition
                stdout, _, _ = self.run_command('wmic os get Caption,Version,BuildNumber /format:csv')
                self.report['system']['windows_details'] = stdout
                
                # Check if running as admin
                self.report['system']['is_admin'] = ctypes.windll.shell32.IsUserAnAdmin() != 0
                
            except Exception as e:
                self.report['system']['windows_error'] = str(e)
    
    def check_hardware(self):
        """Check hardware specifications"""
        print("🔧 Checking hardware specifications...")
        
        # CPU Information
        self.report['hardware']['cpu'] = {
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            'cpu_percent': psutil.cpu_percent(interval=1)
        }
        
        # Memory Information
        memory = psutil.virtual_memory()
        self.report['hardware']['memory'] = {
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'percent_used': memory.percent
        }
        
        # Disk Information
        self.report['hardware']['disks'] = []
        for partition in psutil.disk_partitions():
            try:
                disk_usage = psutil.disk_usage(partition.mountpoint)
                self.report['hardware']['disks'].append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total_gb': round(disk_usage.total / (1024**3), 2),
                    'free_gb': round(disk_usage.free / (1024**3), 2),
                    'used_gb': round(disk_usage.used / (1024**3), 2),
                    'percent_used': round((disk_usage.used / disk_usage.total) * 100, 2)
                })
            except Exception as e:
                self.report['hardware']['disks'].append({
                    'device': partition.device,
                    'error': str(e)
                })
    
    def check_python_installations(self):
        """Check Python installations and versions"""
        print("🐍 Checking Python installations...")
        
        # Current Python
        self.report['python']['current'] = {
            'version': sys.version,
            'version_info': list(sys.version_info),
            'executable': sys.executable,
            'prefix': sys.prefix,
            'path': sys.path[:5]  # First 5 paths only
        }
        
        # Find all Python installations
        python_versions = []
        
        # Check common Python installation paths on Windows
        common_paths = [
            r"C:\Python*",
            r"C:\Program Files\Python*",
            r"C:\Program Files (x86)\Python*",
            r"C:\Users\*\AppData\Local\Programs\Python\Python*",
            r"C:\ProgramData\miniconda3\python.exe",
            r"C:\ProgramData\Anaconda3\python.exe"
        ]
        
        # Check PATH for python executables
        for path in os.environ.get('PATH', '').split(os.pathsep):
            python_exe = os.path.join(path, 'python.exe')
            if os.path.exists(python_exe):
                try:
                    stdout, _, code = self.run_command(f'"{python_exe}" --version')
                    if code == 0:
                        python_versions.append({
                            'path': python_exe,
                            'version': stdout
                        })
                except:
                    pass
        
        self.report['python']['installations'] = python_versions
        
        # Check installed packages
        try:
            installed_packages = {pkg.project_name: pkg.version for pkg in pkg_resources.working_set}
            
            # Key packages to check
            key_packages = [
                'flask', 'paramiko', 'sqlalchemy', 'pillow', 'werkzeug',
                'torch', 'torchvision', 'tensorflow', 'numpy', 'scipy',
                'totalsegmentator', 'nnunetv2', 'nibabel', 'scikit-image'
            ]
            
            self.report['python']['key_packages'] = {}
            for pkg in key_packages:
                self.report['python']['key_packages'][pkg] = installed_packages.get(pkg, 'Not installed')
            
        except Exception as e:
            self.report['python']['package_check_error'] = str(e)
    
    def check_conda_installation(self):
        """Check Conda/Miniconda installations"""
        print("🐨 Checking Conda installations...")
        
        # Check common conda paths
        conda_paths = [
            r"D:\anaconda3\Scripts\conda.exe",
            r"D:\ProgramData\miniconda3\Scripts\conda.exe",
            r"C:\ProgramData\miniconda3\Scripts\conda.exe", 
            r"C:\Users\*\miniconda3\Scripts\conda.exe",
            r"C:\Users\*\anaconda3\Scripts\conda.exe",
            r"C:\ProgramData\Anaconda3\Scripts\conda.exe",
            r"C:\Anaconda3\Scripts\conda.exe"
        ]
        
        conda_found = []
        for path_pattern in conda_paths:
            if '*' in path_pattern:
                # Expand wildcards
                import glob
                for actual_path in glob.glob(path_pattern):
                    if os.path.exists(actual_path):
                        conda_found.append(actual_path)
            elif os.path.exists(path_pattern):
                conda_found.append(path_pattern)
        
        self.report['conda']['installations'] = conda_found
        
        # Test conda functionality
        for conda_path in conda_found:
            try:
                stdout, stderr, code = self.run_command(f'"{conda_path}" --version')
                if code == 0:
                    self.report['conda']['working_conda'] = conda_path
                    self.report['conda']['version'] = stdout
                    
                    # List environments
                    stdout, _, _ = self.run_command(f'"{conda_path}" env list')
                    self.report['conda']['environments'] = stdout.split('\n')
                    
                    break
            except Exception as e:
                self.report['conda'][f'error_{conda_path}'] = str(e)
        
        # Check if conda is in PATH
        stdout, _, code = self.run_command('conda --version')
        self.report['conda']['in_path'] = code == 0
        if code == 0:
            self.report['conda']['path_version'] = stdout
    
    def check_gpu_cuda(self):
        """Check GPU and CUDA installation with detailed AI framework info"""
        print("🎮 Checking GPU, CUDA, and AI frameworks...")
        
        # Check NVIDIA GPU and Driver
        stdout, _, code = self.run_command('nvidia-smi')
        if code == 0:
            self.report['gpu']['nvidia_smi'] = stdout
            self.report['gpu']['has_nvidia'] = True
            
            # Parse nvidia-smi output for detailed info
            lines = stdout.split('\n')
            for line in lines:
                if 'Driver Version:' in line:
                    driver_version = line.split('Driver Version:')[1].split()[0]
                    self.report['gpu']['driver_version'] = driver_version
                if 'CUDA Version:' in line:
                    cuda_runtime = line.split('CUDA Version:')[1].split()[0]
                    self.report['gpu']['cuda_runtime_version'] = cuda_runtime
                if 'GeForce' in line or 'RTX' in line or 'GTX' in line or 'Quadro' in line or 'Tesla' in line:
                    gpu_name = line.split('|')[1].strip().split()[0:3]
                    self.report['gpu']['gpu_model'] = ' '.join(gpu_name)
        else:
            self.report['gpu']['has_nvidia'] = False
            self.report['gpu']['nvidia_error'] = 'nvidia-smi not found'
        
        # Check CUDA Toolkit version
        stdout, _, code = self.run_command('nvcc --version')
        if code == 0:
            self.report['gpu']['cuda_toolkit'] = stdout
            self.report['gpu']['has_cuda_toolkit'] = True
            
            # Parse nvcc version
            for line in stdout.split('\n'):
                if 'release' in line.lower():
                    version_part = line.split('release')[1].split(',')[0].strip()
                    self.report['gpu']['cuda_toolkit_version'] = version_part
        else:
            self.report['gpu']['has_cuda_toolkit'] = False
            self.report['gpu']['cuda_toolkit_error'] = 'nvcc not found'
        
        # Check cuDNN version
        try:
            import torch
            if torch.cuda.is_available():
                self.report['gpu']['cudnn_version'] = str(torch.backends.cudnn.version())
                self.report['gpu']['cudnn_enabled'] = torch.backends.cudnn.enabled
        except:
            pass
        
        # Check PyTorch
        try:
            import torch
            self.report['ai_frameworks']['pytorch'] = {
                'version': torch.__version__,
                'cuda_available': torch.cuda.is_available(),
                'cuda_version': torch.version.cuda if hasattr(torch.version, 'cuda') else None,
                'cudnn_version': torch.backends.cudnn.version() if torch.cuda.is_available() else None,
                'device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0,
                'device_names': [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else []
            }
        except ImportError:
            self.report['ai_frameworks']['pytorch'] = {'status': 'Not installed'}
        except Exception as e:
            self.report['ai_frameworks']['pytorch'] = {'error': str(e)}
        
        # Check TensorFlow
        try:
            import tensorflow as tf
            self.report['ai_frameworks']['tensorflow'] = {
                'version': tf.__version__,
                'gpu_available': len(tf.config.list_physical_devices('GPU')) > 0,
                'gpu_devices': [device.name for device in tf.config.list_physical_devices('GPU')],
                'cuda_version': tf.sysconfig.get_build_info().get('cuda_version', 'Unknown'),
                'cudnn_version': tf.sysconfig.get_build_info().get('cudnn_version', 'Unknown')
            }
        except ImportError:
            self.report['ai_frameworks']['tensorflow'] = {'status': 'Not installed'}
        except Exception as e:
            self.report['ai_frameworks']['tensorflow'] = {'error': str(e)}
        
        # Check other AI frameworks
        frameworks = {
            'numpy': 'numpy',
            'scipy': 'scipy', 
            'scikit-learn': 'sklearn',
            'pandas': 'pandas',
            'matplotlib': 'matplotlib',
            'opencv': 'cv2',
            'pillow': 'PIL',
            'jupyter': 'jupyter'
        }
        
        for name, import_name in frameworks.items():
            try:
                module = __import__(import_name)
                version = getattr(module, '__version__', 'Unknown')
                self.report['ai_frameworks'][name] = {'version': version}
            except ImportError:
                self.report['ai_frameworks'][name] = {'status': 'Not installed'}
            except Exception as e:
                self.report['ai_frameworks'][name] = {'error': str(e)}
    
    def check_network_ports(self):
        """Check network configuration and port availability"""
        print("🌐 Checking network and port availability...")
        
        # Check if ports are available
        ports_to_check = [5000, 2222, 8080, 3000]
        self.report['network']['port_availability'] = {}
        
        for port in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                result = sock.connect_ex(('localhost', port))
                self.report['network']['port_availability'][port] = result != 0  # True if available
            except Exception as e:
                self.report['network']['port_availability'][port] = f"Error: {e}"
            finally:
                sock.close()
        
        # Get network interfaces
        try:
            interfaces = psutil.net_if_addrs()
            self.report['network']['interfaces'] = {}
            for interface, addrs in interfaces.items():
                self.report['network']['interfaces'][interface] = [
                    {'family': addr.family.name, 'address': addr.address, 'netmask': addr.netmask}
                    for addr in addrs
                ]
        except Exception as e:
            self.report['network']['interface_error'] = str(e)
    
    def check_storage_requirements(self):
        """Check storage requirements and availability"""
        print("💾 Checking storage requirements...")
        
        # Estimate space requirements
        requirements = {
            'yuetransfer_env': 1,  # GB
            'totalsegmentator_env': 15,  # GB (PyTorch + TensorFlow + models)
            'user_data': 10,  # GB minimum for medical data
            'temp_processing': 5,  # GB for temporary files
            'total_recommended': 35  # GB total
        }
        
        self.report['storage']['requirements'] = requirements
        
        # Check available space on current drive
        current_drive = Path.cwd().drive if hasattr(Path.cwd(), 'drive') else os.path.splitdrive(os.getcwd())[0]
        try:
            disk_usage = psutil.disk_usage(current_drive)
            available_gb = disk_usage.free / (1024**3)
            
            self.report['storage']['current_drive'] = {
                'drive': current_drive,
                'available_gb': round(available_gb, 2),
                'sufficient': available_gb >= requirements['total_recommended']
            }
        except Exception as e:
            self.report['storage']['storage_error'] = str(e)
    
    def check_permissions(self):
        """Check file system permissions"""
        print("🔐 Checking permissions...")
        
        # Check write permissions in current directory
        test_file = Path.cwd() / 'yuetransfer_test_write.tmp'
        try:
            test_file.write_text('test')
            test_file.unlink()
            self.report['permissions']['current_dir_write'] = True
        except Exception as e:
            self.report['permissions']['current_dir_write'] = False
            self.report['permissions']['write_error'] = str(e)
        
        # Check if running with admin privileges (Windows)
        if platform.system() == 'Windows':
            try:
                self.report['permissions']['is_admin'] = ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                self.report['permissions']['is_admin'] = False
    
    def analyze_conflicts(self):
        """Analyze potential conflicts and issues"""
        print("⚠️ Analyzing potential conflicts...")
        
        conflicts = []
        recommendations = []
        
        # Check Python version compatibility
        python_version = sys.version_info
        if python_version < (3, 8):
            conflicts.append("Python version too old (< 3.8). TotalSegmentator requires Python 3.8+")
            recommendations.append("Update Python to 3.10.13 or newer")
        elif python_version > (3, 11):
            conflicts.append("Python version very new (> 3.11). May have compatibility issues")
            recommendations.append("Consider using Python 3.10.13 for best compatibility")
        
        # Check memory requirements
        memory_gb = self.report['hardware']['memory']['total_gb']
        if memory_gb < 8:
            conflicts.append(f"Low system memory ({memory_gb}GB). Minimum 8GB recommended for AI processing")
            recommendations.append("Consider adding more RAM or using CPU-only mode")
        elif memory_gb < 16:
            recommendations.append(f"Current memory ({memory_gb}GB) is adequate but 16GB+ recommended for large datasets")
        
        # Check GPU availability
        if not self.report['gpu']['has_nvidia']:
            recommendations.append("No NVIDIA GPU detected. AI processing will be slower on CPU")
        elif not self.report['gpu'].get('has_cuda_toolkit', False):
            conflicts.append("NVIDIA GPU found but CUDA toolkit not installed. GPU acceleration unavailable")
            recommendations.append("Install CUDA toolkit for GPU acceleration")
        
        # Check conda installation
        if not self.report['conda'].get('working_conda'):
            conflicts.append("Conda/Anaconda not found or not working")
            recommendations.append("Verify Anaconda installation at D:\\anaconda3\\ or check if conda is in PATH")
        
        # Check port availability
        port_issues = []
        for port, available in self.report['network']['port_availability'].items():
            if not available:
                port_issues.append(str(port))
        
        if port_issues:
            conflicts.append(f"Ports already in use: {', '.join(port_issues)}")
            recommendations.append("Stop services using these ports or modify configuration")
        
        # Check storage space
        if not self.report['storage'].get('current_drive', {}).get('sufficient', False):
            conflicts.append("Insufficient disk space for installation")
            recommendations.append("Free up at least 35GB of disk space")
        
        # Check existing environments
        if 'environments' in self.report['conda']:
            env_lines = self.report['conda']['environments']
            if any('yuetransfer' in line for line in env_lines):
                recommendations.append("yuetransfer environment already exists. Setup will recreate it")
            if any('totalsegmentator' in line for line in env_lines):
                recommendations.append("totalsegmentator environment already exists. Setup will recreate it")
        
        self.report['conflicts'] = conflicts
        self.report['recommendations'] = recommendations
        
        # Overall status
        if conflicts:
            self.report['status'] = 'conflicts_found'
        elif recommendations:
            self.report['status'] = 'ready_with_notes'
        else:
            self.report['status'] = 'ready'
    
    def generate_report(self):
        """Generate comprehensive report with AI development details"""
        self.generate_console_report()
        self.generate_markdown_report()
        return self.report
    
    def generate_console_report(self):
        """Generate console report"""
        print("\n" + "="*80)
        print("🏥 YUETRANSFER SYSTEM CHECK REPORT")
        print("="*80)
        
        print(f"\n📅 Timestamp: {self.report['timestamp']}")
        print(f"🖥️  System: {self.report['system']['platform']}")
        print(f"🏗️  Architecture: {self.report['system']['architecture'][0]}")
        
        print(f"\n💻 HARDWARE")
        print(f"   CPU: {self.report['hardware']['cpu']['physical_cores']} cores / {self.report['hardware']['cpu']['logical_cores']} threads")
        print(f"   Memory: {self.report['hardware']['memory']['total_gb']}GB total, {self.report['hardware']['memory']['available_gb']}GB available")
        
        for disk in self.report['hardware']['disks']:
            if 'error' not in disk:
                print(f"   Disk {disk['device']}: {disk['free_gb']}GB free / {disk['total_gb']}GB total")
        
        print(f"\n🐍 PYTHON")
        print(f"   Current: Python {'.'.join(map(str, self.report['python']['current']['version_info'][:3]))}")
        print(f"   Location: {self.report['python']['current']['executable']}")
        print(f"   Installations found: {len(self.report['python']['installations'])}")
        
        print(f"\n🐨 CONDA")
        if self.report['conda'].get('working_conda'):
            print(f"   Status: ✅ Working ({self.report['conda']['version']})")
            print(f"   Location: {self.report['conda']['working_conda']}")
            if 'environments' in self.report['conda']:
                env_count = len([line for line in self.report['conda']['environments'] if line.strip() and not line.startswith('#')])
                print(f"   Environments: {env_count} found")
        else:
            print(f"   Status: ❌ Not found or not working")
        
        print(f"\n🎮 GPU & CUDA & AI FRAMEWORKS")
        if self.report['gpu']['has_nvidia']:
            print(f"   NVIDIA GPU: ✅ {self.report['gpu'].get('gpu_model', 'Available')}")
            print(f"   Driver Version: {self.report['gpu'].get('driver_version', 'Unknown')}")
            print(f"   CUDA Runtime: {self.report['gpu'].get('cuda_runtime_version', 'Unknown')}")
            if self.report['gpu'].get('has_cuda_toolkit', False):
                print(f"   CUDA Toolkit: ✅ {self.report['gpu'].get('cuda_toolkit_version', 'Available')}")
            else:
                print(f"   CUDA Toolkit: ❌ Not available")
        else:
            print(f"   NVIDIA GPU: ❌ Not detected")
        
        # AI Frameworks
        if 'ai_frameworks' in self.report:
            if 'pytorch' in self.report['ai_frameworks']:
                pt = self.report['ai_frameworks']['pytorch']
                if 'version' in pt:
                    print(f"   PyTorch: ✅ {pt['version']} (CUDA: {'✅' if pt.get('cuda_available') else '❌'})")
                else:
                    print(f"   PyTorch: ❌ {pt.get('status', 'Error')}")
            
            if 'tensorflow' in self.report['ai_frameworks']:
                tf = self.report['ai_frameworks']['tensorflow']
                if 'version' in tf:
                    print(f"   TensorFlow: ✅ {tf['version']} (GPU: {'✅' if tf.get('gpu_available') else '❌'})")
                else:
                    print(f"   TensorFlow: ❌ {tf.get('status', 'Error')}")
        
        print(f"\n🌐 NETWORK")
        for port, available in self.report['network']['port_availability'].items():
            status = "✅ Available" if available else "❌ In use"
            print(f"   Port {port}: {status}")
        
        print(f"\n💾 STORAGE")
        storage = self.report['storage']
        if 'current_drive' in storage:
            drive_info = storage['current_drive']
            status = "✅ Sufficient" if drive_info['sufficient'] else "❌ Insufficient"
            print(f"   Drive {drive_info['drive']}: {drive_info['available_gb']}GB available {status}")
            print(f"   Required: {storage['requirements']['total_recommended']}GB recommended")
        
        # Status summary
        print(f"\n🎯 OVERALL STATUS: ", end="")
        if self.report['status'] == 'ready':
            print("✅ READY TO INSTALL")
        elif self.report['status'] == 'ready_with_notes':
            print("⚠️ READY WITH RECOMMENDATIONS")
        else:
            print("❌ CONFLICTS FOUND")
        
        # Show conflicts
        if self.report['conflicts']:
            print(f"\n❌ CONFLICTS ({len(self.report['conflicts'])}):")
            for i, conflict in enumerate(self.report['conflicts'], 1):
                print(f"   {i}. {conflict}")
        
        # Show recommendations
        if self.report['recommendations']:
            print(f"\n💡 RECOMMENDATIONS ({len(self.report['recommendations'])}):")
            for i, rec in enumerate(self.report['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        print("\n" + "="*80)
        
        # Save detailed report to file
        report_file = Path.cwd() / f"yuecheck_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.report, f, indent=2, default=str)
            print(f"📄 Detailed JSON report saved to: {report_file}")
        except Exception as e:
            print(f"⚠️ Could not save JSON report file: {e}")
    
    def generate_markdown_report(self):
        """Generate detailed Markdown report for AI development"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        md_file = Path.cwd() / f"yuecheck_report_{timestamp}.md"
        
        try:
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(f"""# 🏥 YueTransfer AI Development System Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**System:** {self.report['system']['platform']}  
**Architecture:** {self.report['system']['architecture'][0]}

## 📊 Overall Status

""")
                
                if self.report['status'] == 'ready':
                    f.write("### ✅ **READY TO INSTALL**\n\n")
                elif self.report['status'] == 'ready_with_notes':
                    f.write("### ⚠️ **READY WITH RECOMMENDATIONS**\n\n")
                else:
                    f.write("### ❌ **CONFLICTS FOUND**\n\n")
                
                # System Information Table
                f.write("## 🖥️ System Information\n\n")
                f.write("| Component | Details |\n")
                f.write("|-----------|----------|\n")
                f.write(f"| OS | {self.report['system']['platform']} |\n")
                f.write(f"| Architecture | {self.report['system']['architecture'][0]} |\n")
                f.write(f"| Hostname | {self.report['system']['hostname']} |\n")
                f.write(f"| Admin Rights | {'✅ Yes' if self.report['system'].get('is_admin') else '❌ No'} |\n")
                f.write(f"| Uptime | {round(self.report['system']['uptime_hours'], 1)} hours |\n\n")
                
                # Hardware Table
                f.write("## 💻 Hardware Specifications\n\n")
                f.write("| Component | Specification |\n")
                f.write("|-----------|---------------|\n")
                f.write(f"| CPU Cores | {self.report['hardware']['cpu']['physical_cores']} physical / {self.report['hardware']['cpu']['logical_cores']} logical |\n")
                f.write(f"| Memory | {self.report['hardware']['memory']['total_gb']}GB total, {self.report['hardware']['memory']['available_gb']}GB available |\n")
                f.write(f"| Memory Usage | {self.report['hardware']['memory']['percent_used']}% used |\n")
                
                for disk in self.report['hardware']['disks']:
                    if 'error' not in disk:
                        f.write(f"| Disk {disk['device']} | {disk['free_gb']}GB free / {disk['total_gb']}GB total ({disk['percent_used']}% used) |\n")
                f.write("\n")
                
                # Storage Requirements Chart
                f.write("## 💾 Storage Requirements\n\n")
                f.write("```\n")
                f.write("AI Development Storage Breakdown:\n")
                f.write("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                reqs = self.report['storage']['requirements']
                f.write(f"YueTransfer Environment:     {reqs['yuetransfer_env']:2d}GB  ███\n")
                f.write(f"TotalSegmentator + PyTorch: {reqs['totalsegmentator_env']:2d}GB  ███████████████\n")
                f.write(f"User Data Storage:          {reqs['user_data']:2d}GB  ██████████\n")
                f.write(f"Temporary Processing:        {reqs['temp_processing']:2d}GB  █████\n")
                f.write(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                f.write(f"TOTAL RECOMMENDED:          {reqs['total_recommended']:2d}GB\n")
                f.write("```\n\n")
                
                # GPU & CUDA Information
                f.write("## 🎮 GPU & CUDA Configuration\n\n")
                f.write("| Component | Status | Version/Details |\n")
                f.write("|-----------|--------|------------------|\n")
                
                if self.report['gpu']['has_nvidia']:
                    f.write(f"| NVIDIA GPU | ✅ Available | {self.report['gpu'].get('gpu_model', 'Unknown Model')} |\n")
                    f.write(f"| NVIDIA Driver | ✅ Installed | {self.report['gpu'].get('driver_version', 'Unknown')} |\n")
                    f.write(f"| CUDA Runtime | ✅ Available | {self.report['gpu'].get('cuda_runtime_version', 'Unknown')} |\n")
                    
                    if self.report['gpu'].get('has_cuda_toolkit'):
                        f.write(f"| CUDA Toolkit | ✅ Installed | {self.report['gpu'].get('cuda_toolkit_version', 'Unknown')} |\n")
                    else:
                        f.write("| CUDA Toolkit | ❌ Not Found | Install for development |\n")
                    
                    if self.report['gpu'].get('cudnn_version'):
                        f.write(f"| cuDNN | ✅ Available | {self.report['gpu'].get('cudnn_version')} |\n")
                    else:
                        f.write("| cuDNN | ❌ Not Available | Install for deep learning |\n")
                else:
                    f.write("| NVIDIA GPU | ❌ Not Detected | CPU-only processing |\n")
                    f.write("| CUDA | ❌ N/A | GPU required |\n")
                
                f.write("\n")
                
                # AI Frameworks Table
                f.write("## 🤖 AI Development Frameworks\n\n")
                f.write("| Framework | Status | Version | GPU Support | Details |\n")
                f.write("|-----------|--------|---------|-------------|----------|\n")
                
                if 'ai_frameworks' in self.report:
                    frameworks = self.report['ai_frameworks']
                    
                    # PyTorch
                    if 'pytorch' in frameworks:
                        pt = frameworks['pytorch']
                        if 'version' in pt:
                            cuda_support = "✅ Available" if pt.get('cuda_available') else "❌ CPU Only"
                            devices = f"{pt.get('device_count', 0)} GPU(s)" if pt.get('cuda_available') else "CPU Only"
                            f.write(f"| PyTorch | ✅ Installed | {pt['version']} | {cuda_support} | {devices} |\n")
                        else:
                            f.write(f"| PyTorch | ❌ Not Installed | - | - | {pt.get('status', 'Error')} |\n")
                    
                    # TensorFlow
                    if 'tensorflow' in frameworks:
                        tf = frameworks['tensorflow']
                        if 'version' in tf:
                            gpu_support = "✅ Available" if tf.get('gpu_available') else "❌ CPU Only"
                            cuda_ver = tf.get('cuda_version', 'Unknown')
                            cudnn_ver = tf.get('cudnn_version', 'Unknown')
                            f.write(f"| TensorFlow | ✅ Installed | {tf['version']} | {gpu_support} | CUDA: {cuda_ver}, cuDNN: {cudnn_ver} |\n")
                        else:
                            f.write(f"| TensorFlow | ❌ Not Installed | - | - | {tf.get('status', 'Error')} |\n")
                    
                    # Other frameworks
                    framework_names = {
                        'numpy': 'NumPy',
                        'scipy': 'SciPy', 
                        'scikit-learn': 'Scikit-Learn',
                        'pandas': 'Pandas',
                        'matplotlib': 'Matplotlib',
                        'opencv': 'OpenCV',
                        'pillow': 'Pillow (PIL)',
                        'jupyter': 'Jupyter'
                    }
                    
                    for key, display_name in framework_names.items():
                        if key in frameworks:
                            fw = frameworks[key]
                            if 'version' in fw:
                                f.write(f"| {display_name} | ✅ Installed | {fw['version']} | N/A | Data Science |\n")
                            else:
                                f.write(f"| {display_name} | ❌ Not Installed | - | N/A | {fw.get('status', 'Error')} |\n")
                
                f.write("\n")
                
                # Python Environment
                f.write("## 🐍 Python Environment\n\n")
                f.write("| Component | Details |\n")
                f.write("|-----------|----------|\n")
                f.write(f"| Current Python | {'.'.join(map(str, self.report['python']['current']['version_info'][:3]))} |\n")
                f.write(f"| Executable Path | `{self.report['python']['current']['executable']}` |\n")
                f.write(f"| Installation Prefix | `{self.report['python']['current']['prefix']}` |\n")
                f.write(f"| Total Installations | {len(self.report['python']['installations'])} found |\n\n")
                
                # Conda Environment
                f.write("## 🐨 Conda Environment Manager\n\n")
                f.write("| Component | Status | Details |\n")
                f.write("|-----------|---------|----------|\n")
                
                if self.report['conda'].get('working_conda'):
                    f.write(f"| Conda Status | ✅ Working | {self.report['conda']['version']} |\n")
                    f.write(f"| Installation Path | ✅ Found | `{self.report['conda']['working_conda']}` |\n")
                    if 'environments' in self.report['conda']:
                        env_count = len([line for line in self.report['conda']['environments'] if line.strip() and not line.startswith('#')])
                        f.write(f"| Environments | ✅ Available | {env_count} environments found |\n")
                else:
                    f.write("| Conda Status | ❌ Not Working | Not found or not accessible |\n")
                
                f.write("\n")
                
                # Network Configuration
                f.write("## 🌐 Network Configuration\n\n")
                f.write("| Port | Service | Status |\n")
                f.write("|------|---------|--------|\n")
                port_services = {5000: 'Flask Web Server', 2222: 'SFTP Server', 8080: 'Alternative HTTP', 3000: 'Development Server'}
                for port, available in self.report['network']['port_availability'].items():
                    status = "✅ Available" if available else "❌ In Use"
                    service = port_services.get(port, 'Unknown')
                    f.write(f"| {port} | {service} | {status} |\n")
                f.write("\n")
                
                # Issues and Recommendations
                if self.report['conflicts']:
                    f.write("## ❌ Conflicts Found\n\n")
                    for i, conflict in enumerate(self.report['conflicts'], 1):
                        f.write(f"{i}. **{conflict}**\n")
                    f.write("\n")
                
                if self.report['recommendations']:
                    f.write("## 💡 Recommendations\n\n")
                    for i, rec in enumerate(self.report['recommendations'], 1):
                        f.write(f"{i}. {rec}\n")
                    f.write("\n")
                
                # Installation Commands
                f.write("## 🚀 Next Steps\n\n")
                f.write("If the system check shows **READY** or **READY WITH RECOMMENDATIONS**, proceed with:\n\n")
                f.write("```bash\n")
                f.write("# 1. Set up YueTransfer environment\n")
                f.write("start_yuetransfer.bat\n\n")
                f.write("# 2. Set up TotalSegmentator with AI frameworks\n")
                f.write("start_totalsegmentator.bat\n\n")
                f.write("# 3. Initialize database\n")
                f.write("python init_db.py\n\n")
                f.write("# 4. Start the server\n")
                f.write("yueserver.bat\n")
                f.write("```\n\n")
                
                f.write("---\n")
                f.write(f"*Report generated by YueCheck v1.0 on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            
            print(f"📄 Detailed Markdown report saved to: {md_file}")
            
        except Exception as e:
            print(f"⚠️ Could not save Markdown report: {e}")
    
    def run_full_check(self):
        """Run all system checks"""
        print("🔍 Starting comprehensive system check...")
        print("This may take a few moments...\n")
        
        try:
            self.check_system_info()
            self.check_hardware()
            self.check_python_installations()
            self.check_conda_installation()
            self.check_gpu_cuda()
            self.check_network_ports()
            self.check_storage_requirements()
            self.check_permissions()
            self.analyze_conflicts()
            
            return self.generate_report()
            
        except Exception as e:
            print(f"❌ Error during system check: {e}")
            self.report['check_error'] = str(e)
            return self.report


def main():
    """Main entry point"""
    print("🏥 YueTransfer System Configuration Checker")
    print("=" * 50)
    
    # Check if required modules are available
    try:
        import psutil
    except ImportError:
        print("❌ Missing required module: psutil")
        print("Please install with: pip install psutil")
        return
    
    checker = YueSystemChecker()
    report = checker.run_full_check()
    
    # Return appropriate exit code
    if report['status'] == 'conflicts_found':
        print(f"\n🚨 Please resolve conflicts before running setup scripts!")
        return 1
    elif report['status'] == 'ready_with_notes':
        print(f"\n✅ System is ready with some recommendations noted above.")
        return 0
    else:
        print(f"\n🎉 System is ready for YueTransfer installation!")
        return 0


if __name__ == "__main__":
    exit(main()) 