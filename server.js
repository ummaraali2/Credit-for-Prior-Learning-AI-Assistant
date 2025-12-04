const express = require('express');
const multer = require('multer');
const cors = require('cors');
const FormData = require('form-data');
const fetch = require('node-fetch');

const app = express();
const upload = multer({ storage: multer.memoryStorage() });

app.use(cors());
app.use(express.json());

const WATSONX_SERVICE_URL = 'http://localhost:5000';

app.post('/api/upload', upload.single('file'), async (req, res) => {
    try {
        const file = req.file;
        
        const studentName = req.body.studentName || 'Unknown';
        const nuid = req.body.nuid || 'N/A';
        const requestType = req.body.requestType || 'Not Specified';
        const targetCourse = req.body.targetCourse || 'Not Specified';
        
        console.log('[RECEIVED] Received file:', file.originalname);
        console.log('[STUDENT] Student:', studentName, '|', nuid);
        console.log('[REQUEST] Request:', requestType, '|', targetCourse);
        console.log('[FORWARDING] Forwarding to watsonx.ai service...');
        
        const formData = new FormData();
        formData.append('file', file.buffer, file.originalname);
        formData.append('studentName', studentName);
        formData.append('nuid', nuid);
        formData.append('requestType', requestType);
        formData.append('targetCourse', targetCourse);
        
        const response = await fetch(`${WATSONX_SERVICE_URL}/api/upload-to-watsonx`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        console.log('[SUCCESS] Upload complete:', result.storage);
        
        res.json({
            success: true,
            fileName: file.originalname,
            analysisResult: `File uploaded to watsonx.ai, Milvus, and COS!`,
            ...result
        });
        
    } catch (error) {
        console.error('[ERROR] Error:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});



app.get('/api/download-document/:documentId/:filename', async (req, res) => {
    try {
        const { documentId, filename } = req.params;
        
        console.log(`[RECEIVED] Download request: ${documentId}/${filename}`);
        
        const response = await fetch(
            `${WATSONX_SERVICE_URL}/api/download-document/${documentId}/${filename}`
        );
        
        if (!response.ok) {
            throw new Error('Document not found in COS');
        }
        
        const buffer = await response.buffer();
        
        res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
        res.setHeader('Content-Type', 'application/octet-stream');
        res.send(buffer);
        
        console.log(`[SUCCESS] Downloaded: ${filename}`);
        
    } catch (error) {
        console.error('[ERROR] Download error:', error);
        res.status(404).json({ success: false, error: error.message });
    }
});



app.get('/api/preview-document/:documentId/:filename', async (req, res) => {
    try {
        const { documentId, filename } = req.params;
        
        console.log(`[PREVIEW] Preview request: ${documentId}/${filename}`);
        
        const response = await fetch(
            `${WATSONX_SERVICE_URL}/api/preview-document/${documentId}/${filename}`
        );
        
        if (!response.ok) {
            throw new Error('Document not found in COS');
        }
        
        const contentType = response.headers.get('content-type');
        
        const buffer = await response.buffer();
        
        res.setHeader('Content-Type', contentType || 'application/pdf');
        res.setHeader('Content-Disposition', `inline; filename="${filename}"`);
        res.send(buffer);
        
        console.log(`[SUCCESS] Previewed: ${filename}`);
        
    } catch (error) {
        console.error('[ERROR] Preview error:', error);
        res.status(404).json({ success: false, error: error.message });
    }
});



app.get('/api/view-document/:documentId/:filename', async (req, res) => {
    try {
        const { documentId, filename } = req.params;
        
        const response = await fetch(
            `${WATSONX_SERVICE_URL}/api/view-document/${documentId}/${filename}`
        );
        
        const result = await response.json();
        res.json(result);
        
    } catch (error) {
        console.error('[ERROR] View error:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});



app.get('/api/requests', async (req, res) => {
    try {
        console.log('[REQUEST] Fetching CPL requests from Iceberg...');
        
        const response = await fetch(`${WATSONX_SERVICE_URL}/api/get-requests`);
        
        if (!response.ok) {
            throw new Error('Iceberg service unavailable');
        }
        
        const result = await response.json();
        
        console.log(`[SUCCESS] Retrieved ${result.count} requests from Iceberg`);
        
        res.json({
            success: true,
            requests: result.requests || [],
            count: result.count || 0,
            source: 'iceberg'
        });
        
    } catch (error) {
        console.error('[ERROR] Error fetching from Iceberg:', error);
        res.status(503).json({
            success: false,
            error: 'Iceberg service unavailable',
            requests: [],
            count: 0,
            source: 'error'
        });
    }
});



app.get('/api/requests-by-nuid/:nuid', async (req, res) => {
    try {
        const { nuid } = req.params;
        console.log(`[FOUND] Fetching requests for NUID: ${nuid}`);
        
        const response = await fetch(`${WATSONX_SERVICE_URL}/api/get-requests-by-nuid/${nuid}`);
        
        if (!response.ok) {
            throw new Error('Iceberg query failed');
        }
        
        const result = await response.json();
        
        console.log(`[SUCCESS] Found ${result.count} requests for ${nuid}`);
        
        res.json({
            success: true,
            requests: result.requests || [],
            count: result.count || 0,
            nuid: nuid
        });
        
    } catch (error) {
        console.error('[ERROR] Error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            requests: [],
            count: 0
        });
    }
});



app.put('/api/requests/:id/status', async (req, res) => {
    try {
        const { id } = req.params;
        const { status, credits, notes, updatedBy } = req.body;
        
        console.log(`[UPDATING] Updating status in Iceberg for ${id}`);
        console.log(`   New status: ${status}`);
        console.log(`   Credits: ${credits || 'N/A'}`);
        console.log(`   Updated by: ${updatedBy || 'Unknown'}`);
        
        const response = await fetch(`${WATSONX_SERVICE_URL}/api/update-status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                requestId: id,
                status: status,
                credits: credits,
                notes: notes,
                updatedBy: updatedBy
            })
        });
        
        if (!response.ok) {
            throw new Error('Iceberg update failed');
        }
        
        const result = await response.json();
        
        console.log(`[SUCCESS] Status updated in Iceberg table`);
        
        res.json({
            success: true,
            message: 'Status updated successfully',
            requestId: id,
            newStatus: status
        });
        
    } catch (error) {
        console.error('[ERROR] Error updating status:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});



app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        message: 'Node.js Gateway running',
        endpoints: {
            upload: 'POST /api/upload',
            download: 'GET /api/download-document/:documentId/:filename',
            view: 'GET /api/view-document/:documentId/:filename',
            requests: 'GET /api/requests',
            requestsByNuid: 'GET /api/requests-by-nuid/:nuid',
            updateStatus: 'PUT /api/requests/:id/status'
        },
        watsonxService: WATSONX_SERVICE_URL,
        features: ['COS Downloads', 'Iceberg Storage', 'Milvus Search']
    });
});



const PORT = 3000;
app.listen(PORT, () => {
    console.log(`[SUCCESS] Node.js Gateway running on http://localhost:${PORT}`);
    console.log(`[CONNECTED] Connected to watsonx service: ${WATSONX_SERVICE_URL}`);
    console.log(`[FETCHING] Features: COS Downloads + Iceberg + Milvus`);
});