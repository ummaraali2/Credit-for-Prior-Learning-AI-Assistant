// Status Management System with COS Download
const BACKEND_URL = 'http://localhost:3000';

let allRequests = [];
let filteredRequests = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadRequests();
    setupFormHandler();
});

// Load all requests FROM ICEBERG
async function loadRequests() {
    document.getElementById('requests-list').innerHTML = '<div class="loading-message">Loading requests from Iceberg...</div>';
    
    try {
        const response = await fetch(`${BACKEND_URL}/api/requests`);
        
        if (!response.ok) {
            throw new Error('Backend unavailable');
        }
        
        const data = await response.json();
        
        // Verify data source
        if (data.source !== 'iceberg') {
            console.warn('[WARNING] Data not from Iceberg, showing message');
            document.getElementById('requests-list').innerHTML = 
                '<div class="empty-message">Iceberg connection unavailable. Please check backend services.</div>';
            return;
        }
        
        console.log(`[SUCCESS] Loaded ${data.count} requests from Iceberg`);
        allRequests = data.requests || [];
        filteredRequests = [...allRequests];
        renderRequests();
        
    } catch (error) {
        console.error('[ERROR] Error loading requests:', error);
        document.getElementById('requests-list').innerHTML = 
            '<div class="empty-message">Unable to connect to Iceberg. Please ensure backend services are running.</div>';
    }
}

// Download document from COS
async function downloadDocument(documentId, filename, event) {
    // Stop event propagation to prevent opening the modal
    if (event) {
        event.stopPropagation();
    }
    
    try {
        console.log(`[DOWNLOAD] Downloading: ${documentId}/${filename}`);
        
        // Show downloading notification
        showNotification(`Downloading ${filename}...`, 'info');
        
        // Download file
        const response = await fetch(`${BACKEND_URL}/api/download-document/${documentId}/${filename}`);
        
        if (!response.ok) {
            throw new Error('Download failed');
        }
        
        // Create blob and download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        console.log(`[SUCCESS] Downloaded: ${filename}`);
        showNotification(`Downloaded ${filename} successfully`, 'success');
        
    } catch (error) {
        console.error('[ERROR] Download error:', error);
        showNotification(`Failed to download ${filename}`, 'error');
    }
}

// Preview document in modal
async function previewDocument(documentId, filename, event) {
    // Stop event propagation to prevent opening the status modal
    if (event) {
        event.stopPropagation();
    }
    
    try {
        console.log(`[PREVIEW] Previewing: ${documentId}/${filename}`);
        
        // Set document name in modal header
        document.getElementById('preview-document-name').textContent = filename;
        
        // Set iframe source to preview endpoint
        const previewUrl = `${BACKEND_URL}/api/preview-document/${documentId}/${filename}`;
        document.getElementById('document-preview-frame').src = previewUrl;
        
        // Show preview modal
        document.getElementById('preview-modal').classList.add('active');
        
        console.log(`[SUCCESS] Opened preview for: ${filename}`);
        
    } catch (error) {
        console.error('[ERROR] Preview error:', error);
        showNotification(`Failed to preview ${filename}`, 'error');
    }
}

// Close preview modal
function closePreviewModal() {
    const modal = document.getElementById('preview-modal');
    modal.classList.remove('active');
    
    // Clear iframe to stop loading
    document.getElementById('document-preview-frame').src = '';
}

// Render requests list with download buttons
function renderRequests() {
    const container = document.getElementById('requests-list');
    
    if (filteredRequests.length === 0) {
        container.innerHTML = '<div class="empty-message">No requests found matching your criteria.</div>';
        return;
    }
    
    const html = filteredRequests.map(request => `
        <div class="request-card" onclick="openStatusModal('${request.id}')">
            <div class="request-header">
                <div class="request-info">
                    <div class="student-name">${request.studentName}</div>
                    <div class="request-meta">
                        <span>NUID: ${request.nuid}</span>
                        <span>Type: ${request.requestType}</span>
                        <span>Submitted: ${formatDate(request.submittedDate)}</span>
                    </div>
                </div>
                <span class="status-badge ${request.status}">${getStatusLabel(request.status)}</span>
            </div>
            
            <div class="request-details">
                <div class="detail-item">
                    <span class="detail-label">Target Course</span>
                    <span class="detail-value">${request.targetCourse}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Document</span>
                    <span class="detail-value">
                        <span class="document-filename">${request.documentName || 'N/A'}</span>
                        ${request.documentId && request.documentName ? `
                            <button 
                                class="preview-doc-btn" 
                                onclick="previewDocument('${request.documentId}', '${request.documentName}', event)"
                                title="Preview document">
                                Preview
                            </button>
                            <button 
                                class="download-doc-btn" 
                                onclick="downloadDocument('${request.documentId}', '${request.documentName}', event)"
                                title="Download original document">
                                Download
                            </button>
                        ` : ''}
                    </span>
                </div>
                ${request.credits ? `
                <div class="detail-item">
                    <span class="detail-label">Credits Awarded</span>
                    <span class="detail-value">${request.credits} credits</span>
                </div>
                ` : ''}
                ${request.notes ? `
                <div class="detail-item">
                    <span class="detail-label">Latest Note</span>
                    <span class="detail-value">${truncateText(request.notes, 50)}</span>
                </div>
                ` : ''}
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

// Search requests
function searchRequests() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase().trim();
    
    if (!searchTerm) {
        filteredRequests = [...allRequests];
    } else {
        filteredRequests = allRequests.filter(req => 
            req.studentName.toLowerCase().includes(searchTerm) ||
            req.nuid.toLowerCase().includes(searchTerm) ||
            req.targetCourse.toLowerCase().includes(searchTerm) ||
            req.requestType.toLowerCase().includes(searchTerm)
        );
    }
    
    // Apply current status filter
    const statusFilter = document.getElementById('status-filter').value;
    if (statusFilter !== 'all') {
        filteredRequests = filteredRequests.filter(req => req.status === statusFilter);
    }
    
    renderRequests();
}

// Filter by status
function filterRequests() {
    const statusFilter = document.getElementById('status-filter').value;
    const searchTerm = document.getElementById('search-input').value.toLowerCase().trim();
    
    // Start with all requests
    filteredRequests = [...allRequests];
    
    // Apply search filter
    if (searchTerm) {
        filteredRequests = filteredRequests.filter(req => 
            req.studentName.toLowerCase().includes(searchTerm) ||
            req.nuid.toLowerCase().includes(searchTerm) ||
            req.targetCourse.toLowerCase().includes(searchTerm) ||
            req.requestType.toLowerCase().includes(searchTerm)
        );
    }
    
    // Apply status filter
    if (statusFilter !== 'all') {
        filteredRequests = filteredRequests.filter(req => req.status === statusFilter);
    }
    
    renderRequests();
}

// Refresh requests
async function refreshRequests() {
    document.getElementById('requests-list').innerHTML = '<div class="loading-message">Refreshing requests...</div>';
    await loadRequests();
}

// Open status update modal
function openStatusModal(requestId) {
    const request = allRequests.find(r => r.id === requestId);
    if (!request) return;
    
    // Populate modal with request data
    document.getElementById('modal-request-id').value = request.id;
    document.getElementById('modal-student-name').textContent = request.studentName;
    document.getElementById('modal-nuid').textContent = request.nuid;
    document.getElementById('modal-request-type').textContent = request.requestType;
    document.getElementById('modal-course').textContent = request.targetCourse;
    document.getElementById('modal-submitted').textContent = formatDate(request.submittedDate);
    
    // Document info with preview and download buttons
    const documentInfoEl = document.getElementById('modal-document-info');
    if (request.documentId && request.documentName) {
        documentInfoEl.innerHTML = `
            <span class="document-filename">${request.documentName}</span><br>
            <button 
                class="preview-doc-btn-modal" 
                onclick="previewDocument('${request.documentId}', '${request.documentName}', event)"
                title="Preview document">
                Preview Document
            </button>
            <button 
                class="download-doc-btn-modal" 
                onclick="downloadDocument('${request.documentId}', '${request.documentName}', event)"
                title="Download original document">
                Download Document
            </button>
        `;
    } else {
        documentInfoEl.textContent = request.documentName || 'N/A';
    }
    
    const currentStatusEl = document.getElementById('modal-current-status');
    currentStatusEl.innerHTML = `<span class="status-badge ${request.status}">${getStatusLabel(request.status)}</span>`;
    
    // Pre-fill form with current values
    document.getElementById('new-status').value = request.status;
    document.getElementById('credits-awarded').value = request.credits || '';
    document.getElementById('advisor-notes').value = request.notes || '';
    
    // Show modal
    document.getElementById('status-modal').classList.add('active');
}

// Close modal
function closeModal() {
    document.getElementById('status-modal').classList.remove('active');
    document.getElementById('status-update-form').reset();
}

// Setup form submission handler
function setupFormHandler() {
    const form = document.getElementById('status-update-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await submitStatusUpdate();
    });
}

// Submit status update
async function submitStatusUpdate() {
    const requestId = document.getElementById('modal-request-id').value;
    const newStatus = document.getElementById('new-status').value;
    const credits = document.getElementById('credits-awarded').value;
    const notes = document.getElementById('advisor-notes').value;
    
    if (!newStatus) {
        alert('Please select a status');
        return;
    }
    
    const updateData = {
        requestId,
        status: newStatus,
        credits: credits ? parseFloat(credits) : null,
        notes: notes.trim(),
        updatedBy: 'Current Advisor', // In production, get from auth
        updatedAt: new Date().toISOString()
    };
    
    try {
        const response = await fetch(`${BACKEND_URL}/api/requests/${requestId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData)
        });
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || 'Update failed');
        }
        
        console.log('[SUCCESS] Status updated in Iceberg:', result);
        
        closeModal();
        showNotification('Status updated successfully', 'success');
        
        // Reload data from Iceberg to show updated status
        await loadRequests();
        
    } catch (error) {
        console.error('[ERROR] Update error:', error);
        showNotification('Failed to update status: ' + error.message, 'error');
    }
}

// Helper: Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Helper: Get status label
function getStatusLabel(status) {
    const labels = {
        'pending': 'Pending Review',
        'under-review': 'Under Review',
        'approved': 'Approved',
        'denied': 'Denied',
        'requires-info': 'Requires Information'
    };
    return labels[status] || status;
}

// Helper: Truncate text
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    
    const colors = {
        success: { bg: '#d1e7dd', color: '#0f5132', border: '#badbcc' },
        error: { bg: '#f8d7da', color: '#842029', border: '#f5c2c7' },
        info: { bg: '#cfe2ff', color: '#084298', border: '#b6d4fe' }
    };
    
    const style = colors[type] || colors.success;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${style.bg};
        color: ${style.color};
        border: 1px solid ${style.border};
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        font-family: 'Lato', sans-serif;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Close modal on outside click
document.addEventListener('click', (e) => {
    const statusModal = document.getElementById('status-modal');
    const previewModal = document.getElementById('preview-modal');
    
    if (e.target === statusModal) {
        closeModal();
    }
    
    if (e.target === previewModal) {
        closePreviewModal();
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
        closePreviewModal();
    }
});

console.log('Status Management System with COS Downloads and Preview initialized');