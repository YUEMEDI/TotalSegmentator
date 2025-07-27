"""
YueTransfer SFTP Server Implementation
"""

import os
import logging
import threading
import socket
from pathlib import Path
from paramiko import SFTPServer, SFTPServerInterface, SFTPAttributes, SFTPHandle
from paramiko import SSHException, AuthenticationException
from paramiko.server import ServerInterface
from paramiko import Transport, RSAKey
import stat
import time

class YueTransferSFTPServer(SFTPServerInterface):
    """Custom SFTP server interface for YueTransfer"""
    
    def __init__(self, server, username, root_path):
        self.server = server
        self.username = username
        self.root_path = Path(root_path) / username
        self.root_path.mkdir(parents=True, exist_ok=True)
        
        # Create user directories
        self._create_user_directories()
        
    def _create_user_directories(self):
        """Create standard directories for new users"""
        directories = [
            'dicom_datasets',
            'nifti_files', 
            'archives',
            'selected_for_processing',
            'results'
        ]
        
        for directory in directories:
            (self.root_path / directory).mkdir(exist_ok=True)
    
    def _get_real_path(self, path):
        """Convert SFTP path to real filesystem path"""
        # Remove leading slash and normalize
        clean_path = path.lstrip('/')
        if not clean_path:
            return self.root_path
        
        real_path = self.root_path / clean_path
        return real_path
    
    def _check_permissions(self, path):
        """Check if user has permission to access path"""
        real_path = self._get_real_path(path)
        
        # Ensure path is within user's root directory
        try:
            real_path.resolve().relative_to(self.root_path.resolve())
        except ValueError:
            return False
        
        return True
    
    def list_folder(self, path):
        """List contents of a folder"""
        if not self._check_permissions(path):
            return []
        
        real_path = self._get_real_path(path)
        
        if not real_path.exists() or not real_path.is_dir():
            return []
        
        try:
            items = []
            for item in real_path.iterdir():
                try:
                    stat_info = item.stat()
                    attrs = SFTPAttributes()
                    attrs.filename = item.name
                    attrs.size = stat_info.st_size
                    attrs.uid = stat_info.st_uid
                    attrs.gid = stat_info.st_gid
                    attrs.mtime = int(stat_info.st_mtime)
                    attrs.atime = int(stat_info.st_atime)
                    
                    if item.is_dir():
                        attrs.permissions = stat.S_IFDIR | 0o755
                    else:
                        attrs.permissions = stat.S_IFREG | 0o644
                    
                    items.append(attrs)
                except OSError:
                    continue
            
            return items
        except OSError:
            return []
    
    def stat(self, path):
        """Get file attributes"""
        if not self._check_permissions(path):
            return None
        
        real_path = self._get_real_path(path)
        
        if not real_path.exists():
            return None
        
        try:
            stat_info = real_path.stat()
            attrs = SFTPAttributes()
            attrs.size = stat_info.st_size
            attrs.uid = stat_info.st_uid
            attrs.gid = stat_info.st_gid
            attrs.mtime = int(stat_info.st_mtime)
            attrs.atime = int(stat_info.st_atime)
            
            if real_path.is_dir():
                attrs.permissions = stat.S_IFDIR | 0o755
            else:
                attrs.permissions = stat.S_IFREG | 0o644
            
            return attrs
        except OSError:
            return None
    
    def lstat(self, path):
        """Get file attributes (follow symlinks)"""
        return self.stat(path)
    
    def open(self, path, flags, attr):
        """Open a file"""
        if not self._check_permissions(path):
            return None
        
        real_path = self._get_real_path(path)
        
        # Create parent directories if needed
        real_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            binary_flag = getattr(os, 'O_BINARY', 0)
            flags |= binary_flag
            
            mode = getattr(attr, 'permissions', None)
            if mode is None:
                mode = 0o644
            
            if flags & os.O_CREAT and not real_path.exists():
                real_path.touch(mode=mode)
            
            file_obj = real_path.open('rb' if flags & os.O_RDONLY else 'wb')
            
            return YueTransferSFTPHandle(real_path, file_obj)
        except OSError:
            return None
    
    def remove(self, path):
        """Remove a file"""
        if not self._check_permissions(path):
            return False
        
        real_path = self._get_real_path(path)
        
        try:
            if real_path.is_file():
                real_path.unlink()
                return True
        except OSError:
            pass
        
        return False
    
    def rename(self, oldpath, newpath):
        """Rename a file"""
        if not self._check_permissions(oldpath) or not self._check_permissions(newpath):
            return False
        
        old_real_path = self._get_real_path(oldpath)
        new_real_path = self._get_real_path(newpath)
        
        try:
            new_real_path.parent.mkdir(parents=True, exist_ok=True)
            old_real_path.rename(new_real_path)
            return True
        except OSError:
            return False
    
    def mkdir(self, path, attr):
        """Create a directory"""
        if not self._check_permissions(path):
            return False
        
        real_path = self._get_real_path(path)
        
        try:
            mode = getattr(attr, 'permissions', 0o755)
            real_path.mkdir(parents=True, mode=mode)
            return True
        except OSError:
            return False
    
    def rmdir(self, path):
        """Remove a directory"""
        if not self._check_permissions(path):
            return False
        
        real_path = self._get_real_path(path)
        
        try:
            if real_path.is_dir():
                real_path.rmdir()
                return True
        except OSError:
            pass
        
        return False
    
    def chattr(self, path, attr):
        """Change file attributes"""
        if not self._check_permissions(path):
            return False
        
        real_path = self._get_real_path(path)
        
        try:
            if hasattr(attr, 'permissions'):
                real_path.chmod(attr.permissions)
            return True
        except OSError:
            return False
    
    def readlink(self, path):
        """Read a symbolic link"""
        if not self._check_permissions(path):
            return None
        
        real_path = self._get_real_path(path)
        
        try:
            if real_path.is_symlink():
                return str(real_path.readlink())
        except OSError:
            pass
        
        return None
    
    def symlink(self, target_path, link_path):
        """Create a symbolic link"""
        if not self._check_permissions(target_path) or not self._check_permissions(link_path):
            return False
        
        target_real_path = self._get_real_path(target_path)
        link_real_path = self._get_real_path(link_path)
        
        try:
            link_real_path.symlink_to(target_real_path)
            return True
        except OSError:
            return False

class YueTransferSFTPHandle(SFTPHandle):
    """Custom SFTP handle for file operations"""
    
    def __init__(self, path, file_obj):
        super().__init__()
        self.path = path
        self.file_obj = file_obj
    
    def close(self):
        """Close the file"""
        try:
            self.file_obj.close()
        except:
            pass
    
    def read(self, offset, length):
        """Read from file"""
        try:
            self.file_obj.seek(offset)
            return self.file_obj.read(length)
        except:
            return None
    
    def write(self, offset, data):
        """Write to file"""
        try:
            self.file_obj.seek(offset)
            self.file_obj.write(data)
            return len(data)
        except:
            return 0
    
    def stat(self):
        """Get file attributes"""
        try:
            stat_info = self.path.stat()
            attrs = SFTPAttributes()
            attrs.size = stat_info.st_size
            attrs.uid = stat_info.st_uid
            attrs.gid = stat_info.st_gid
            attrs.mtime = int(stat_info.st_mtime)
            attrs.atime = int(stat_info.st_atime)
            attrs.permissions = stat_info.st_mode
            return attrs
        except OSError:
            return None

class YueTransferSSHServer(ServerInterface):
    """SSH server for SFTP authentication"""
    
    def __init__(self, user_manager):
        self.user_manager = user_manager
        self.event = threading.Event()
    
    def check_auth_password(self, username, password):
        """Check password authentication"""
        try:
            if self.user_manager.authenticate_user(username, password):
                return paramiko.AUTH_SUCCESSFUL
        except Exception as e:
            logging.error(f"Authentication error for user {username}: {e}")
        
        return paramiko.AUTH_FAILED
    
    def check_auth_publickey(self, username, key):
        """Check public key authentication (not implemented)"""
        return paramiko.AUTH_FAILED
    
    def check_channel_request(self, kind, chanid):
        """Check channel request"""
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_channel_shell_request(self, channel):
        """Check shell request (not allowed)"""
        return False
    
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        """Check PTY request (not allowed)"""
        return False
    
    def check_channel_request(self, kind, chanid):
        """Check channel request"""
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

class SFTPServer:
    """Main SFTP server class"""
    
    def __init__(self, host='0.0.0.0', port=2222, root_dir='uploads'):
        self.host = host
        self.port = port
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize user manager
        from app.models.user import UserManager
        self.user_manager = UserManager()
        
        # Generate server key
        self.server_key = RSAKey.generate(2048)
        
        # Server state
        self.running = False
        self.server_socket = None
    
    def start(self):
        """Start the SFTP server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(100)
            
            self.running = True
            logging.info(f"SFTP server started on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client, addr = self.server_socket.accept()
                    logging.info(f"SFTP connection from {addr[0]}:{addr[1]}")
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error:
                    if self.running:
                        raise
                    break
                    
        except Exception as e:
            logging.error(f"SFTP server error: {e}")
            raise
        finally:
            self.stop()
    
    def _handle_client(self, client, addr):
        """Handle individual client connection"""
        try:
            transport = Transport(client)
            transport.add_server_key(self.server_key)
            
            ssh_server = YueTransferSSHServer(self.user_manager)
            transport.start_server(server=ssh_server)
            
            channel = transport.accept(20)
            if channel is None:
                return
            
            transport.accept()
            
            server = SFTPServer()
            server.start_subsystem('sftp', YueTransferSFTPServer, transport, self.root_dir)
            
        except Exception as e:
            logging.error(f"Error handling SFTP client {addr}: {e}")
        finally:
            try:
                client.close()
            except:
                pass
    
    def stop(self):
        """Stop the SFTP server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        logging.info("SFTP server stopped") 