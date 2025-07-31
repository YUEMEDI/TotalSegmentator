// YUEUPLOAD - Upload JavaScript

// Fallback functions in case YUEUPLOAD object is not available
if (typeof YUEUPLOAD === 'undefined') {
    window.YUEUPLOAD = {
        formatFileSize: function(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },
        showNotification: function(message, type = 'info') {
            console.log(`${type.toUpperCase()}: ${message}`);
            // Create a simple notification
            const notification = document.createElement('div');
            notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
            notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            notification.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.appendChild(notification);
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 5000);
        }
    };
}

class UploadManager {
    constructor() {
        this.uploadZone = document.getElementById('upload-zone');
        this.fileInput = document.getElementById('file-input');
        this.progressContainer = document.getElementById('upload-progress');
        this.progressBar = document.getElementById('progress-bar');
        this.progressText = document.getElementById('progress-text');
        this.fileList = document.getElementById('file-list');
        this.filesContainer = document.getElementById('files-container');
        
        this.uploadedFiles = [];
        this.currentUploads = 0;
        this.totalFiles = 0;
        
        // Bind methods to preserve 'this' context
        this.preventDefaults = this.preventDefaults.bind(this);
        this.highlight = this.highlight.bind(this);
        this.unhighlight = this.unhighlight.bind(this);
        this.handleDrop = this.handleDrop.bind(this);
        this.handleFiles = this.handleFiles.bind(this);
        
        this.init();
    }
    
    init() {
        this.setupDragAndDrop();
        this.setupFileInput();
        this.updateStats();
    }
    
    setupDragAndDrop() {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.uploadZone.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });
        
        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            this.uploadZone.addEventListener(eventName, this.highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            this.uploadZone.addEventListener(eventName, this.unhighlight, false);
        });
        
        // Handle dropped files
        this.uploadZone.addEventListener('drop', this.handleDrop, false);
        
        // Remove the click handler for the upload zone since we have buttons now
        // this.uploadZone.addEventListener('click', () => {
        //     this.fileInput.click();
        // });
    }
    
    setupFileInput() {
        this.fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });
        
        // Add folder input support
        const folderInput = document.getElementById('folder-input');
        if (folderInput) {
            folderInput.addEventListener('change', (e) => {
                const files = Array.from(e.target.files);
                // For folder input, webkitRelativePath should already be set
                // But let's ensure it's available
                files.forEach(file => {
                    if (!file.webkitRelativePath && file.webkitRelativePath !== '') {
                        console.warn('File from folder input missing webkitRelativePath:', file.name);
                    }
                });
                this.handleFiles(files);
            });
        }
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    highlight(e) {
        document.getElementById('upload-zone').classList.add('drag-over');
    }
    
    unhighlight(e) {
        document.getElementById('upload-zone').classList.remove('drag-over');
    }
    
    handleDrop(e) {
        const dt = e.dataTransfer;
        const items = dt.items;
        
        if (items) {
            // Handle both files and folders
            this.processItems(items);
        } else {
            // Fallback for older browsers
            const files = dt.files;
            this.handleFiles(files);
        }
    }
    
    processItems(items) {
        const files = [];
        let processedItems = 0;
        
        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            
            if (item.kind === 'file') {
                const entry = item.webkitGetAsEntry();
                if (entry) {
                    this.processEntry(entry, files, () => {
                        processedItems++;
                        if (processedItems === items.length) {
                            this.handleFiles(files);
                        }
                    });
                }
            }
        }
        
        // If no items were processed, try files fallback
        if (processedItems === 0) {
            const dt = event.dataTransfer;
            if (dt.files) {
                this.handleFiles(dt.files);
            }
        }
    }
    
    processEntry(entry, files, callback, currentPath = '') {
        if (entry.isFile) {
            entry.file((file) => {
                // Set the relative path for folder structure preservation
                // Only set webkitRelativePath if it's not already set and is writable
                if (!file.webkitRelativePath || file.webkitRelativePath === '') {
                    try {
                        // Try to set the property, but don't fail if it's read-only
                        Object.defineProperty(file, 'webkitRelativePath', {
                            value: currentPath + file.name,
                            writable: true,
                            configurable: true
                        });
                    } catch (e) {
                        // If we can't set webkitRelativePath, create a custom property
                        file.relativePath = currentPath + file.name;
                        console.log(`Using custom relativePath for ${file.name}: ${file.relativePath}`);
                    }
                }
                console.log(`Processing file: ${file.name} with path: ${file.webkitRelativePath || file.relativePath || 'no path'}`);
                files.push(file);
                callback();
            });
        } else if (entry.isDirectory) {
            console.log(`Processing directory: ${entry.name} at path: ${currentPath}`);
            this.readDirectory(entry, files, callback, currentPath + entry.name + '/');
        }
    }
    
    readDirectory(dirEntry, files, callback, currentPath = '') {
        const dirReader = dirEntry.createReader();
        let entries = [];
        
        const readEntries = () => {
            dirReader.readEntries((results) => {
                if (results.length === 0) {
                    // All entries read
                    let processedEntries = 0;
                    entries.forEach(entry => {
                        this.processEntry(entry, files, () => {
                            processedEntries++;
                            if (processedEntries === entries.length) {
                                callback();
                            }
                        }, currentPath);
                    });
                } else {
                    entries = entries.concat(results);
                    readEntries(); // Continue reading
                }
            });
        };
        
        readEntries();
    }
    
    handleFiles(files) {
        if (files.length === 0) return;
        
        this.totalFiles = files.length;
        this.currentUploads = 0;
        this.uploadedFiles = [];
        
        this.showProgress();
        this.uploadFiles(Array.from(files));
    }
    
    async uploadFiles(files) {
        // For large uploads, process in chunks
        const chunkSize = 3; // Process 3 files at a time (reduced for testing)
        const totalFiles = files.length;
        
        if (totalFiles > chunkSize) {
            console.log(`Large upload detected: ${totalFiles} files. Processing in chunks of ${chunkSize}...`);
            await this.uploadInChunks(files, chunkSize);
            return;
        }
        
        // Original single-upload logic for smaller files
        await this.uploadSingleBatch(files);
    }
    
    async uploadInChunks(files, chunkSize) {
        const totalChunks = Math.ceil(files.length / chunkSize);
        let uploadedFiles = [];
        let failedFiles = [];
        
        this.updateProgress(0, `Starting chunked upload: ${files.length} files in ${totalChunks} chunks...`);
        
        for (let i = 0; i < totalChunks; i++) {
            const start = i * chunkSize;
            const end = Math.min(start + chunkSize, files.length);
            const chunk = files.slice(start, end);
            
            const chunkNumber = i + 1;
            this.updateProgress(
                (i / totalChunks) * 100, 
                `Uploading chunk ${chunkNumber}/${totalChunks}: files ${start + 1}-${end}`
            );
            
            try {
                const result = await this.uploadSingleBatch(chunk);
                if (result.success) {
                    uploadedFiles = uploadedFiles.concat(result.uploaded_files || []);
                    console.log(`Chunk ${chunkNumber} completed: ${result.uploaded_files?.length || 0} files`);
                } else {
                    failedFiles = failedFiles.concat(chunk.map(f => f.name));
                    console.error(`Chunk ${chunkNumber} failed:`, result.error);
                }
            } catch (error) {
                console.error(`Chunk ${chunkNumber} error:`, error);
                failedFiles = failedFiles.concat(chunk.map(f => f.name));
            }
            
            // Small delay between chunks to prevent overwhelming the server
            if (i < totalChunks - 1) {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
        
        // Final progress update
        const successCount = uploadedFiles.length;
        const failureCount = failedFiles.length;
        
        this.updateProgress(100, `Upload completed! ${successCount} successful, ${failureCount} failed`);
        
        if (uploadedFiles.length > 0) {
            this.handleUploadSuccess(uploadedFiles);
        }
        
        if (failedFiles.length > 0) {
            YUEUPLOAD.showNotification(`${failedFiles.length} files failed to upload`, 'warning');
        }
        
        YUEUPLOAD.showNotification(`Chunked upload completed: ${successCount} successful, ${failureCount} failed`, 
            failureCount > 0 ? 'warning' : 'success');
    }
    
    async uploadSingleBatch(files) {
        const formData = new FormData();
        
        // Calculate total size and prepare files with path information
        let totalSize = 0;
        files.forEach((file, index) => {
            formData.append('files', file);
            
            // Add relative path information for folder structure preservation
            // Use the full relative path as the key to ensure uniqueness
            const pathKey = file.webkitRelativePath || file.relativePath || file.name;
            if (file.webkitRelativePath) {
                formData.append(`path_${pathKey}`, file.webkitRelativePath);
                console.log(`Adding path for ${pathKey}: ${file.webkitRelativePath}`);
            } else if (file.relativePath) {
                formData.append(`path_${pathKey}`, file.relativePath);
                console.log(`Adding relativePath for ${pathKey}: ${file.relativePath}`);
            } else {
                console.warn(`No path information for file: ${file.name}`);
            }
            
            totalSize += file.size;
        });
        
        // Debug: Log all FormData entries
        console.log('=== FormData Debug ===');
        for (let [key, value] of formData.entries()) {
            console.log(`FormData entry: ${key} = ${value}`);
        }
        console.log('=== End FormData Debug ===');
        
        const totalSizeMB = (totalSize / (1024 * 1024)).toFixed(2);
        console.log(`Uploading ${files.length} files, total size: ${totalSizeMB} MB`);
        
        try {
            this.updateProgress(5, `Preparing upload of ${files.length} files (${totalSizeMB} MB)...`);
            
            // Set longer timeout for large uploads
            const timeout = Math.max(60000, totalSize / (1024 * 1024) * 2000); // 2 seconds per MB, minimum 60s
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            
            const response = await fetch('/upload/api/upload', {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                let errorMessage = `Upload failed: ${response.status}`;
                
                if (response.status === 413) {
                    errorMessage = 'Upload too large. Please try uploading fewer files at once or contact support.';
                } else if (response.status === 500) {
                    errorMessage = 'Server error during upload. Please try again or contact support.';
                } else {
                    try {
                        const errorData = await response.json();
                        errorMessage = errorData.error || errorMessage;
                    } catch (e) {
                        const errorText = await response.text();
                        errorMessage = errorText || errorMessage;
                    }
                }
                
                throw new Error(errorMessage);
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.updateProgress(100, `Upload completed! ${result.successful_uploads} files uploaded successfully.`);
                
                if (result.failed_uploads > 0) {
                    YUEUPLOAD.showNotification(`${result.failed_uploads} files failed to upload. Check the list below.`, 'warning');
                }
                
                return result;
            } else {
                throw new Error(result.error || 'Upload failed');
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            
            let errorMessage = error.message;
            if (error.name === 'AbortError') {
                errorMessage = 'Upload timed out. Please try uploading fewer files at once.';
            }
            
            this.updateProgress(0, `Upload failed: ${errorMessage}`);
            YUEUPLOAD.showNotification(`Upload failed: ${errorMessage}`, 'danger');
            
            throw error;
        }
    }
    
    handleUploadSuccess(files) {
        this.uploadedFiles = files;
        this.showFileList();
        this.updateStats();
        
        YUEUPLOAD.showNotification(`Successfully uploaded ${files.length} files!`, 'success');
        
        // Hide progress after a delay
        setTimeout(() => {
            this.hideProgress();
        }, 2000);
    }
    
    showProgress() {
        this.progressContainer.style.display = 'block';
        this.progressContainer.classList.add('fade-in');
    }
    
    hideProgress() {
        this.progressContainer.style.display = 'none';
    }
    
    updateProgress(percent, text) {
        this.progressBar.style.width = `${percent}%`;
        this.progressBar.setAttribute('aria-valuenow', percent);
        this.progressText.textContent = text;
    }
    
    showFileList() {
        this.fileList.style.display = 'block';
        this.filesContainer.innerHTML = '';
        
        this.uploadedFiles.forEach(file => {
            this.addFileToList(file);
        });
    }
    
    addFileToList(file) {
        const fileElement = document.createElement('div');
        fileElement.className = `col-md-6 col-lg-4 mb-3`;
        
        const fileType = file.is_dicom ? 'dicom' : 'other';
        const fileIcon = file.is_dicom ? 'fa-file-medical' : 'fa-file';
        
        // Show folder structure if available
        let folderInfo = '';
        if (file.relative_path && file.relative_path !== file.original_name) {
            const pathParts = file.relative_path.split('/');
            if (pathParts.length > 1) {
                const folderPath = pathParts.slice(0, -1).join(' / ');
                folderInfo = `<div class="file-folder text-muted small"><i class="fas fa-folder me-1"></i>${folderPath}</div>`;
            }
        }
        
        fileElement.innerHTML = `
            <div class="file-item ${fileType}">
                <div class="d-flex align-items-center">
                    <div class="me-3">
                        <i class="fas ${fileIcon} fa-2x text-primary"></i>
                    </div>
                    <div class="file-info">
                        <div class="file-name">${file.original_name}</div>
                        ${folderInfo}
                        <div class="file-size">${YUEUPLOAD.formatFileSize(file.file_size)}</div>
                        <span class="file-status success">Uploaded</span>
                    </div>
                </div>
            </div>
        `;
        
        this.filesContainer.appendChild(fileElement);
    }
    
    updateStats() {
        const totalFiles = this.uploadedFiles.length;
        const totalSize = this.uploadedFiles.reduce((sum, file) => sum + file.file_size, 0);
        const dicomFiles = this.uploadedFiles.filter(file => file.is_dicom).length;
        const otherFiles = totalFiles - dicomFiles;
        
        document.getElementById('total-files').textContent = totalFiles;
        document.getElementById('total-size').textContent = YUEUPLOAD.formatFileSize(totalSize);
        document.getElementById('dicom-files').textContent = dicomFiles;
        document.getElementById('other-files').textContent = otherFiles;
    }
}

// Initialize upload manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new UploadManager();
});