// Student Status Tracking System
const BACKEND_URL = 'http://localhost:3000';

let currentNuid = null;
let studentRequests = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupLookupForm();
});

// Setup NUID lookup form
function setupLookupForm() {
    const form = document.getElementById('nuid-lookup-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await lookupByNuid();
    });
}

// Lookup requests by NUID
async function lookupByNuid() {
    const nuidInput = document.getElementById('nuid-input');
    const nuid = nuidInput.value.trim();
    
    if (!nuid) {
        alert('Please enter your NUID');
        return;
    }
    
    currentNuid = nuid;
    
    // Show loading
    const lookupSection = document.getElementById('lookup-section');
    const statusSection = document.getElementById('status-display-section');
    
    lookupSection.style.display = 'none';
    statusSection.style.display = 'block';
    
    document.getElementById('requests-container').innerHTML = 
        '<div class="loading-state">Loading your requests...</div>';
    
    try {
        // Fetch all requests and filter by NUID
        const response = await fetch(`${BACKEND_URL}/api/requests`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch requests');
        }
        
        const data = await response.json();
        
        // Filter requests for this student's NUID
        studentRequests = data.requests.filter(req => req.nuid === nuid);
        
        console.log(`Found ${studentRequests.length} requests for NUID: ${nuid}`);
        
        // Display student info
        if (studentRequests.length > 0) {
            document.getElementById('student-name-display').textContent = 
                studentRequests[0].studentName || 'Student';
        }
        document.getElementById('nuid-display').textContent = `NUID: ${nuid}`;
        
        // Render requests
        renderStudentRequests();
        
    } catch (error) {
        console.error('Error fetching requests:', error);
        document.getElementById('requests-container').innerHTML = 
            '<div class="empty-state"><h3>Error Loading Requests</h3><p>Please try again later.</p></div>';
    }
}

// Render student's requests
function renderStudentRequests() {
    const container = document.getElementById('requests-container');
    
    if (studentRequests.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>No Requests Found</h3>
                <p>You don't have any CPL requests submitted yet.</p>
                <a href="index.html" class="btn-primary" style="display: inline-block; margin-top: 16px; text-decoration: none;">Submit a Request</a>
            </div>
        `;
        return;
    }
    
    const html = studentRequests.map(request => {
        const statusClass = (request.status || 'pending').toLowerCase().replace(' ', '-');
        const statusLabel = getStatusLabel(request.status || 'pending');
        
        return `
            <div class="student-request-card">
                <div class="request-header-row">
                    <div>
                        <h3 class="request-title">${request.targetCourse || 'Course Not Specified'}</h3>
                        <p class="request-meta-info">
                            ${request.requestType || 'Request Type Not Specified'} • 
                            Submitted ${formatDate(request.submittedDate)}
                        </p>
                    </div>
                    <span class="status-badge ${statusClass}">${statusLabel}</span>
                </div>
                
                <div class="request-details-grid">
                    <div class="detail-block">
                        <span class="detail-label">Request Type</span>
                        <span class="detail-value">${request.requestType || 'Not Specified'}</span>
                    </div>
                    
                    <div class="detail-block">
                        <span class="detail-label">Target Course</span>
                        <span class="detail-value">${request.targetCourse || 'Not Specified'}</span>
                    </div>
                    
                    <div class="detail-block">
                        <span class="detail-label">Documents Submitted</span>
                        <span class="detail-value">${request.documents ? request.documents.length : 0} file(s)</span>
                    </div>
                    
                    ${request.credits ? `
                    <div class="detail-block">
                        <span class="detail-label">Credits Awarded</span>
                        <span class="detail-value"><span class="credits-badge">${request.credits} Credits</span></span>
                    </div>
                    ` : ''}
                </div>
                
                ${request.notes && request.notes.trim() ? `
                <div class="advisor-notes-section">
                    <h4>Advisor Feedback</h4>
                    <p class="advisor-notes-text">${request.notes}</p>
                </div>
                ` : ''}
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

// Change NUID lookup
function changeLookup() {
    document.getElementById('lookup-section').style.display = 'block';
    document.getElementById('status-display-section').style.display = 'none';
    document.getElementById('nuid-input').value = '';
    document.getElementById('nuid-input').focus();
    currentNuid = null;
    studentRequests = [];
}

// Helper: Format date
function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
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

console.log('Student Status System initialized');