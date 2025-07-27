/**
 * YueTransfer - Main JavaScript Application
 */

// Global variables
let selectedFiles = new Set();
let uploadQueue = [];
let currentUpload = null;

// Initialize application
$(document).ready(function() {
    initializeApp();
});

function initializeApp() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize file upload handlers
    initializeFileUpload();
    
    // Initialize file browser
    initializeFileBrowser();
    
    // Initialize drag and drop
    initializeDragAndDrop();
    
    // Auto-refresh components
    startAutoRefresh();
}

/**
 * File Upload Functionality
 */
function initializeFileUpload() {
    const uploadForm = $('#upload-form');
    const fileInput = $('#file-input');
    const uploadArea = $('.upload-area');
    const progressBar = $('.upload-progress');
    const uploadButton = $('#upload-button');
    
    if (fileInput.length) {
        fileInput.on('change', function() {
            handleFileSelection(this.files);
        });
    }
    
    if (uploadForm.length) {
        uploadForm.on('submit', function(e) {
            e.preventDefault();
            startUpload();
        });
    }
}

function handleFileSelection(files) {
    const fileList = $('#file-list');
    fileList.empty();
    
    Array.from(files).forEach(file => {
        const fileItem = createFileItem(file);
        fileList.append(fileItem);
    });
    
    updateUploadButton();
}

function createFileItem(file) {
    const fileSize = formatFileSize(file.size);
    const fileType = getFileType(file.name);
    const fileIcon = getFileIcon(fileType);
    
    return $(`
        <div class="file-item" data-filename="${file.name}">
            <div class="file-item-icon">
                <i class="${fileIcon}"></i>
            </div>
            <div class="file-item-info">
                <div class="file-item-name">${file.name}</div>
                <div class="file-item-meta">${fileSize} • ${fileType.toUpperCase()}</div>
            </div>
            <div class="file-item-actions">
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeFile('${file.name}')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `);
}

function removeFile(filename) {
    $(`.file-item[data-filename="${filename}"]`).remove();
    updateUploadButton();
}

function updateUploadButton() {
    const fileCount = $('#file-list .file-item').length;
    const uploadButton = $('#upload-button');
    
    if (fileCount > 0) {
        uploadButton.prop('disabled', false).text(`Upload ${fileCount} File${fileCount > 1 ? 's' : ''}`);
    } else {
        uploadButton.prop('disabled', true).text('Select Files');
    }
}

function startUpload() {
    const formData = new FormData();
    const files = $('#file-input')[0].files;
    
    Array.from(files).forEach(file => {
        formData.append('files[]', file);
    });
    
    // Show progress
    $('.upload-progress-container').show();
    $('.upload-progress').css('width', '0%');
    
    $.ajax({
        url: '/api/upload',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        xhr: function() {
            const xhr = new window.XMLHttpRequest();
            xhr.upload.addEventListener('progress', function(evt) {
                if (evt.lengthComputable) {
                    const percentComplete = (evt.loaded / evt.total) * 100;
                    $('.upload-progress').css('width', percentComplete + '%');
                }
            }, false);
            return xhr;
        },
        success: function(response) {
            showAlert('success', 'Files uploaded successfully!');
            $('#file-list').empty();
            $('#file-input').val('');
            updateUploadButton();
            refreshFileBrowser();
        },
        error: function(xhr) {
            showAlert('danger', 'Upload failed: ' + (xhr.responseJSON?.message || 'Unknown error'));
        },
        complete: function() {
            $('.upload-progress-container').hide();
        }
    });
}

/**
 * File Browser Functionality
 */
function initializeFileBrowser() {
    // File selection
    $(document).on('click', '.file-item', function(e) {
        if (!$(e.target).hasClass('btn')) {
            toggleFileSelection($(this));
        }
    });
    
    // Bulk actions
    $('#select-all').on('change', function() {
        const isChecked = $(this).is(':checked');
        $('.file-item input[type="checkbox"]').prop('checked', isChecked);
        updateBulkActions();
    });
    
    // Search functionality
    $('#file-search').on('input', function() {
        const query = $(this).val().toLowerCase();
        filterFiles(query);
    });
}

function toggleFileSelection(fileItem) {
    const checkbox = fileItem.find('input[type="checkbox"]');
    checkbox.prop('checked', !checkbox.is(':checked'));
    
    if (checkbox.is(':checked')) {
        fileItem.addClass('selected');
        selectedFiles.add(fileItem.data('filename'));
    } else {
        fileItem.removeClass('selected');
        selectedFiles.delete(fileItem.data('filename'));
    }
    
    updateBulkActions();
}

function updateBulkActions() {
    const selectedCount = selectedFiles.size;
    const bulkActions = $('.bulk-actions');
    
    if (selectedCount > 0) {
        bulkActions.show();
        $('.selected-count').text(selectedCount);
    } else {
        bulkActions.hide();
    }
}

function filterFiles(query) {
    $('.file-item').each(function() {
        const fileName = $(this).find('.file-item-name').text().toLowerCase();
        const fileType = $(this).find('.file-item-meta').text().toLowerCase();
        
        if (fileName.includes(query) || fileType.includes(query)) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
}

function refreshFileBrowser() {
    $.get('/api/files', function(data) {
        $('#file-browser-content').html(data);
    });
}

/**
 * Drag and Drop Functionality
 */
function initializeDragAndDrop() {
    const uploadArea = $('.upload-area');
    
    if (uploadArea.length) {
        uploadArea.on('dragover', function(e) {
            e.preventDefault();
            $(this).addClass('dragover');
        });
        
        uploadArea.on('dragleave', function(e) {
            e.preventDefault();
            $(this).removeClass('dragover');
        });
        
        uploadArea.on('drop', function(e) {
            e.preventDefault();
            $(this).removeClass('dragover');
            
            const files = e.originalEvent.dataTransfer.files;
            $('#file-input')[0].files = files;
            handleFileSelection(files);
        });
    }
}

/**
 * TotalSegmentator Integration
 */
function processFilesWithTotalSegmentator() {
    if (selectedFiles.size === 0) {
        showAlert('warning', 'Please select files to process');
        return;
    }
    
    const fileList = Array.from(selectedFiles);
    
    $.ajax({
        url: '/api/process-files',
        type: 'POST',
        data: JSON.stringify({ files: fileList }),
        contentType: 'application/json',
        success: function(response) {
            showAlert('success', 'Files sent to TotalSegmentator for processing');
            selectedFiles.clear();
            updateBulkActions();
        },
        error: function(xhr) {
            showAlert('danger', 'Failed to process files: ' + (xhr.responseJSON?.message || 'Unknown error'));
        }
    });
}

/**
 * Utility Functions
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function getFileType(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    
    if (['dcm'].includes(ext)) return 'dicom';
    if (['nii', 'gz'].includes(ext)) return 'nifti';
    if (['zip', 'tar', 'gz'].includes(ext)) return 'archive';
    if (['jpg', 'jpeg', 'png', 'bmp', 'tiff'].includes(ext)) return 'image';
    
    return 'unknown';
}

function getFileIcon(fileType) {
    const icons = {
        'dicom': 'fas fa-calendar',
        'nifti': 'fas fa-file-medical',
        'archive': 'fas fa-archive',
        'image': 'fas fa-image',
        'unknown': 'fas fa-file'
    };
    
    return icons[fileType] || icons.unknown;
}

function showAlert(type, message) {
    const alert = $(`
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('main').prepend(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.alert('close');
    }, 5000);
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showAlert('success', 'Copied to clipboard!');
    }).catch(function() {
        showAlert('danger', 'Failed to copy to clipboard');
    });
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Auto-refresh functionality
 */
function startAutoRefresh() {
    // Refresh file browser every 30 seconds
    setInterval(function() {
        if ($('#file-browser-content').length) {
            refreshFileBrowser();
        }
    }, 30000);
    
    // Refresh stats every 60 seconds
    setInterval(function() {
        if ($('.stats-card').length) {
            refreshStats();
        }
    }, 60000);
}

function refreshStats() {
    $.get('/api/stats', function(data) {
        $('.stats-dicom').text(data.dicom_files);
        $('.stats-nifti').text(data.nifti_files);
        $('.stats-storage').text(data.storage_used);
        $('.stats-jobs').text(data.processing_jobs);
    });
}

/**
 * Keyboard shortcuts
 */
$(document).on('keydown', function(e) {
    // Ctrl+A: Select all files
    if (e.ctrlKey && e.key === 'a') {
        e.preventDefault();
        $('#select-all').prop('checked', true).trigger('change');
    }
    
    // Delete: Delete selected files
    if (e.key === 'Delete' && selectedFiles.size > 0) {
        e.preventDefault();
        deleteSelectedFiles();
    }
    
    // Ctrl+Enter: Process selected files
    if (e.ctrlKey && e.key === 'Enter' && selectedFiles.size > 0) {
        e.preventDefault();
        processFilesWithTotalSegmentator();
    }
});

function deleteSelectedFiles() {
    confirmAction('Are you sure you want to delete the selected files?', function() {
        const fileList = Array.from(selectedFiles);
        
        $.ajax({
            url: '/api/delete-files',
            type: 'DELETE',
            data: JSON.stringify({ files: fileList }),
            contentType: 'application/json',
            success: function(response) {
                showAlert('success', 'Files deleted successfully');
                selectedFiles.clear();
                updateBulkActions();
                refreshFileBrowser();
            },
            error: function(xhr) {
                showAlert('danger', 'Failed to delete files: ' + (xhr.responseJSON?.message || 'Unknown error'));
            }
        });
    });
}

/**
 * Theme switching
 */
function toggleTheme() {
    const body = $('body');
    const currentTheme = body.attr('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    body.attr('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update theme icon
    const themeIcon = $('.theme-toggle i');
    themeIcon.removeClass('fas fa-moon fas fa-sun').addClass(newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon');
}

// Load saved theme
$(document).ready(function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        $('body').attr('data-theme', savedTheme);
        const themeIcon = $('.theme-toggle i');
        themeIcon.removeClass('fas fa-moon fas fa-sun').addClass(savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon');
    }
});

/**
 * Export functions for global access
 */
window.YueTransfer = {
    processFilesWithTotalSegmentator,
    copyToClipboard,
    showAlert,
    formatFileSize,
    toggleTheme
}; 