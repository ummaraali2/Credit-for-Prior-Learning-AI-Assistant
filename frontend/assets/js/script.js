// Global variables
let uploadedFiles = [];
let waInstance = null;
const BACKEND_URL = 'http://localhost:3000';

// Initialize Watson Assistant
window.watsonAssistantChatOptions = {
    integrationID: "2d6e2e03-4cef-4e0f-b131-f989bc4776d2",
    region: "au-syd",
    serviceInstanceID: "fb664aa6-6a7e-4626-b086-668dc8b1fa15",
    
    onLoad: async (instance) => {
        waInstance = instance;
        
        instance.on({
            type: 'receive',
            handler: (event) => {
                const context = event.data?.context;
                if (context?.skills?.['actions skill']?.skill_variables) {
                    const vars = context.skills['actions skill'].skill_variables;
                    
                    if (vars.student_name) studentContext.name = vars.student_name;
                    if (vars.nuid) studentContext.nuid = vars.nuid;
                    if (vars.request_type) studentContext.requestType = vars.request_type;
                    if (vars.target_course) studentContext.targetCourse = vars.target_course;
                    
                    console.log('[CONTEXT] Student Context Updated:', studentContext);
                }
            }
        });
        
        instance.on({
            type: 'view:change',
            handler: (event) => {
                console.log('[VIEW] View changed');
                setTimeout(() => addUploadButtons(instance), 300);
            }
        });
        
        instance.on({
            type: 'pre:send',
            handler: (event) => {
        if (uploadedFiles.length > 0) {
            event.data.context = event.data.context || {};
            event.data.context.skills = event.data.context.skills || {};
            
            // KEY FIX: Use 'action skill' (SINGULAR!) 
            event.data.context.skills['actions skill'] = 
                event.data.context.skills['actions skill'] || {};
            event.data.context.skills['actions skill'].skill_variables = 
                event.data.context.skills['actions skill'].skill_variables || {};
            
            // Store extracted text as simple variables
            event.data.context.skills['actions skill'].skill_variables.file_name = 
                uploadedFiles[0].name;
            event.data.context.skills['actions skill'].skill_variables.file_text = 
                uploadedFiles[0].analysisResult || 'No text extracted';
            event.data.context.skills['actions skill'].skill_variables.file_size = 
                uploadedFiles[0].size;
            
            console.log('[SUCCESS] Context sent to Watson:');
            console.log('File:', uploadedFiles[0].name);
            console.log('Text length:', uploadedFiles[0].analysisResult?.length || 0);
        }
    }
});
        
        // CLEAR FILES after message is sent
        instance.on({
            type: 'send',
            handler: () => {
                if (uploadedFiles.length > 0) {
                    console.log('📨 Message sent with files, clearing');
                    showToast(`Sent ${uploadedFiles.length} file(s)`, 'success');
                    uploadedFiles = [];
                    renderFiles();
                }
            }
        });
        
        // Listen for custom file upload requests from Watson
        instance.on({
            type: 'customResponse',
            handler: (event) => {
                if (event.data.message.user_defined?.user_defined_type === 'user-file-upload') {
                    console.log('📂 Watson requested file upload');
                    document.getElementById('file-upload-input').click();
                }
            }
        });
        
        await instance.render();
        
        setTimeout(() => addUploadButtons(instance), 500);
        
        console.log('[SUCCESS] Watson Assistant loaded');
    }
};

// Load Watson Assistant
setTimeout(function() {
    const t = document.createElement('script');
    t.src = "https://web-chat.global.assistant.watson.appdomain.cloud/versions/" + 
            (window.watsonAssistantChatOptions.clientVersion || 'latest') + 
            "/WatsonAssistantChatEntry.js";
    document.head.appendChild(t);
});

// Add upload buttons to BOTH home page and conversation page
function addUploadButtons(instance) {
    if (!instance.writeableElements) {
        console.log('⏳ writeableElements not ready');
        setTimeout(() => addUploadButtons(instance), 500);
        return;
    }
    
    addHomePageButton(instance);
    addConversationPageButton(instance);
    setupFileInput();
}

// Add button to HOME PAGE
function addHomePageButton(instance) {
    try {
        const homeElement = instance.writeableElements.homeScreenAfterStartersElement;
        
        if (!homeElement) {
            console.log('⏳ Home screen element not available');
            return;
        }
        
        if (document.getElementById('cpl-home-upload-btn')) {
            return;
        }
        
        const container = document.createElement('div');
        container.style.cssText = `
            display: flex;
            justify-content: center;
            padding: 16px;
            background: transparent;
        `;
        
        const btn = document.createElement('button');
        btn.id = 'cpl-home-upload-btn';
        btn.title = 'Upload Document';
        btn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20">
                <path fill="#999" d="M16.5 6v11.5c0 2.21-1.79 4-4 4s-4-1.79-4-4V5a2.5 2.5 0 0 1 5 0v10.5c0 .55-.45 1-1 1s-1-.45-1-1V6H10v9.5a2.5 2.5 0 0 0 5 0V5c0-2.21-1.79-4-4-4S7 2.79 7 5v12.5c0 3.04 2.46 5.5 5.5 5.5s5.5-2.46 5.5-5.5V6h-1.5z"/>
            </svg>
            <span style="margin-left: 6px; font-size: 13px; color: #999;">Upload Document</span>
        `;
        btn.style.cssText = `
            background: transparent;
            border: none;
            cursor: pointer;
            padding: 8px 16px;
            display: inline-flex;
            align-items: center;
            opacity: 0.7;
            transition: opacity 0.2s;
            font-family: 'Lato', sans-serif;
        `;
        btn.onmouseover = () => btn.style.opacity = '1';
        btn.onmouseout = () => btn.style.opacity = '0.7';
        btn.onclick = () => document.getElementById('file-upload-input').click();
        
        container.appendChild(btn);
        homeElement.innerHTML = '';
        homeElement.appendChild(container);
        
        console.log('[SUCCESS] Home page button added');
        
    } catch (error) {
        console.error('[ERROR] Error adding home button:', error);
    }
}

// Add button to CONVERSATION PAGE
function addConversationPageButton(instance) {
    try {
        const beforeInput = instance.writeableElements.beforeInputElement;
        
        if (!beforeInput) {
            console.log('⏳ Conversation input element not available');
            return;
        }
        
        if (document.getElementById('cpl-conv-upload-btn')) {
            return;
        }
        
        const container = document.createElement('div');
        container.id = 'cpl-conv-container';
        container.style.cssText = `
            display: flex;
            flex-direction: column;
            background: transparent;
            width: 100%;
        `;
        
        // File preview area
        const preview = document.createElement('div');
        preview.id = 'cpl-file-preview';
        preview.style.cssText = `
            padding: 0 12px 8px 12px;
            font-family: 'Lato', sans-serif;
        `;
        
        // Bottom row with paperclip button
        const bottomRow = document.createElement('div');
        bottomRow.style.cssText = `
            display: flex;
            align-items: center;
            padding: 8px 12px;
            background: transparent;
        `;
        
        const btn = document.createElement('button');
        btn.id = 'cpl-conv-upload-btn';
        btn.title = 'Upload Document';
        btn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20">
                <path fill="#666" d="M16.5 6v11.5c0 2.21-1.79 4-4 4s-4-1.79-4-4V5a2.5 2.5 0 0 1 5 0v10.5c0 .55-.45 1-1 1s-1-.45-1-1V6H10v9.5a2.5 2.5 0 0 0 5 0V5c0-2.21-1.79-4-4-4S7 2.79 7 5v12.5c0 3.04 2.46 5.5 5.5 5.5s5.5-2.46 5.5-5.5V6h-1.5z"/>
            </svg>
        `;
        btn.style.cssText = `
            background: transparent;
            border: none;
            cursor: pointer;
            padding: 6px;
            display: inline-flex;
            align-items: center;
            opacity: 0.7;
            transition: opacity 0.2s;
        `;
        btn.onmouseover = () => btn.style.opacity = '1';
        btn.onmouseout = () => btn.style.opacity = '0.7';
        btn.onclick = () => document.getElementById('file-upload-input').click();
        
        bottomRow.appendChild(btn);
        container.appendChild(preview);
        container.appendChild(bottomRow);
        
        beforeInput.innerHTML = '';
        beforeInput.appendChild(container);
        
        renderFiles();
        
        console.log('[SUCCESS] Conversation page button added');
        
    } catch (error) {
        console.error('[ERROR] Error adding conversation button:', error);
    }
}

// Setup file input
function setupFileInput() {
    const input = document.getElementById('file-upload-input');
    if (input && !input.dataset.listener) {
        input.addEventListener('change', handleFileSelect);
        input.dataset.listener = 'true';
    }
}

// Handle file selection
function handleFileSelect(event) {
    const files = event.target.files;
    if (!files.length) return;
    
    Array.from(files).forEach(file => {
        if (!validateFile(file)) return;
        
        uploadedFiles.push({
            id: Date.now() + Math.random(),
            file,
            name: file.name,
            size: file.size,
            type: file.type,
            status: 'pending'
        });
    });
    
    renderFiles();
    
    uploadedFiles.forEach(f => {
        if (f.status === 'pending') uploadFileToBackend(f);
    });
    
    event.target.value = '';
}

// Validate file
function validateFile(file) {
    const MAX_SIZE = 10 * 1024 * 1024;
    const ALLOWED = [
        'application/pdf', 'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain', 'image/jpeg', 'image/png', 'image/jpg'
    ];
    
    if (file.size > MAX_SIZE) {
        showToast('File too large (max 10MB)', 'error');
        return false;
    }
    
    if (!ALLOWED.includes(file.type)) {
        showToast('Invalid file type', 'error');
        return false;
    }
    
    return true;
}

// Upload to backend - UPDATED TO SEND STUDENT CONTEXT
async function uploadFileToBackend(fileObj) {
    const formData = new FormData();
    formData.append('file', fileObj.file);
    formData.append('fileId', fileObj.id);
    
    // IMPORTANT: Send student context with file
    if (studentContext.name) formData.append('studentName', studentContext.name);
    if (studentContext.nuid) formData.append('nuid', studentContext.nuid);
    if (studentContext.requestType) formData.append('requestType', studentContext.requestType);
    if (studentContext.targetCourse) formData.append('targetCourse', studentContext.targetCourse);
    
    fileObj.status = 'uploading';
    renderFiles();
    showToast(`Uploading ${fileObj.name}...`, 'info');
    
    try {
        const response = await fetch(`${BACKEND_URL}/api/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Upload failed');
        
        const result = await response.json();
        fileObj.status = 'ready';
        fileObj.cosUrl = result.cosUrl;
        fileObj.cosKey = result.fileName;
        fileObj.analysisResult = result.analysisResult;
        fileObj.documentId = result.document_id;
        
        showToast(`${fileObj.name} ready - Click button to send`, 'success');
        renderFiles();
        
    } catch (error) {
        console.error('Upload error:', error);
        fileObj.status = 'error';
        showToast(`Failed: ${fileObj.name}`, 'error');
        renderFiles();
    }
}

// Render files with manual Send button
function renderFiles() {
    const preview = document.getElementById('cpl-file-preview');
    if (!preview) return;
    
    if (uploadedFiles.length === 0) {
        preview.innerHTML = '';
        preview.style.display = 'none';
        return;
    }
    
    preview.style.display = 'block';
    
    // Render file items
    const filesHTML = uploadedFiles.map(f => {
        const icon = getIcon(f.type);
        const statusIcon = getStatusIcon(f.status);
        const statusColor = getStatusColor(f.status);
        const displayName = f.name.length > 30 ? f.name.substring(0, 30) + '...' : f.name;
        
        return `
            <div style="display: flex; align-items: center; background: ${statusColor}; padding: 8px 10px; border-radius: 8px; margin-bottom: 6px; border: 1px solid rgba(0,0,0,0.1);">
                <span style="font-size: 20px; margin-right: 8px;">${icon}</span>
                <div style="flex: 1; min-width: 0;">
                    <div style="font-size: 13px; font-weight: 600; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${displayName}</div>
                    <div style="font-size: 11px; color: #666; margin-top: 2px;">${formatSize(f.size)} • ${statusIcon} ${f.status}</div>
                </div>
                <button onclick="removeFile('${f.id}')" style="background: #da1e28; color: white; border: none; border-radius: 50%; width: 24px; height: 24px; cursor: pointer; font-size: 16px; font-weight: bold; display: flex; align-items: center; justify-content: center; margin-left: 8px;" title="Remove file">×</button>
            </div>
        `;
    }).join('');
    
    // Add "Send Files" button if files are ready
    const hasReadyFiles = uploadedFiles.filter(f => f.status === 'ready').length > 0;
    
    const sendButton = hasReadyFiles ? `
        <button 
            onclick="sendFilesToWatson()" 
            style="
                background: #cc0000;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 600;
                cursor: pointer;
                width: 100%;
                margin-top: 8px;
                transition: all 0.2s;
                font-family: 'Lato', sans-serif;
            "
            onmouseover="this.style.background='#aa0000'"
            onmouseout="this.style.background='#cc0000'"
        >
            [UPLOAD] Send ${uploadedFiles.length} File(s) to Assistant
        </button>
    ` : '';
    
    preview.innerHTML = filesHTML + sendButton;
}

// Remove file
function removeFile(fileId) {
    uploadedFiles = uploadedFiles.filter(f => f.id != fileId);
    renderFiles();
    showToast('File removed', 'success');
}

window.removeFile = removeFile;

// Send files to Watson manually
function sendFilesToWatson() {
    if (!waInstance) {
        console.error('[ERROR] Watson instance not ready');
        showToast('Assistant not ready, please try again', 'error');
        return;
    }
    
    if (uploadedFiles.length === 0) {
        showToast('No files to send', 'error');
        return;
    }
    
    const readyFiles = uploadedFiles.filter(f => f.status === 'ready');
    if (readyFiles.length === 0) {
        showToast('Please wait for files to finish uploading', 'info');
        return;
    }
    
    console.log('[UPLOAD] Manually sending', readyFiles.length, 'file(s) to Watson');
    
    waInstance.send({
        input: {
            message_type: 'text',
            text: `📎 Uploaded ${readyFiles.length} document(s) for evaluation`
        }
    }).then(() => {
        console.log('[SUCCESS] Files sent successfully via manual button');
    }).catch(err => {
        console.error('[ERROR] Send error:', err);
        showToast('Failed to send files', 'error');
    });
}

window.sendFilesToWatson = sendFilesToWatson;

// Helper: Get file icon
function getIcon(type) {
    if (type.includes('pdf')) return '[VIEW]';
    if (type.includes('word') || type.includes('document')) return '📝';
    if (type.includes('image')) return '🖼️';
    if (type.includes('text')) return '📃';
    return '📎';
}

// Helper: Get status icon
function getStatusIcon(status) {
    if (status === 'pending') return '⏳';
    if (status === 'uploading') return '[UPLOAD]';
    if (status === 'ready') return '[SUCCESS]';
    if (status === 'error') return '[ERROR]';
    return '📎';
}

// Helper: Get status color
function getStatusColor(status) {
    if (status === 'pending') return 'rgba(255, 193, 7, 0.1)';
    if (status === 'uploading') return 'rgba(15, 98, 254, 0.1)';
    if (status === 'ready') return 'rgba(36, 161, 72, 0.1)';
    if (status === 'error') return 'rgba(218, 30, 40, 0.1)';
    return 'rgba(0, 0, 0, 0.05)';
}

// Helper: Format file size
function formatSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toFixed(1) + ' ' + sizes[i];
}

// Toast notifications
function showToast(message, type = 'info') {
    document.querySelectorAll('.cpl-toast').forEach(el => el.remove());
    
    const toast = document.createElement('div');
    toast.className = 'cpl-toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed; top: 20px; right: 20px; padding: 12px 20px;
        border-radius: 6px; font-size: 14px; z-index: 999999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        font-family: 'Lato', sans-serif;
        ${type === 'success' ? 'background: #24a148; color: white;' : ''}
        ${type === 'error' ? 'background: #da1e28; color: white;' : ''}
        ${type === 'info' ? 'background: #0f62fe; color: white;' : ''}
    `;
    
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}