# CPL Website - Complete Dependencies Documentation

## Project Overview
This Credit for Prior Learning (CPL) system integrates multiple IBM Cloud services with a Node.js gateway and Python backend to process student documents using AI embeddings and vector search.

---

## Node.js Dependencies (Gateway Server)

### Core Framework
- **`express@^5.1.0`**
  - **Purpose**: Main HTTP server framework
  - **Why needed**: Handles API routing, file uploads, and proxying to Python backend
  - **Endpoints**: `/api/upload`, `/api/download-document`, `/api/requests`

### Cross-Origin & File Handling
- **`cors@^2.8.5`**
  - **Purpose**: Cross-Origin Resource Sharing middleware
  - **Why needed**: Allows frontend (different port) to communicate with API server
  - **Configuration**: Enables all origins for development

- **`multer@^2.0.2`**
  - **Purpose**: Multipart form data middleware for file uploads
  - **Why needed**: Processes student document uploads (PDF, DOCX, TXT)
  - **Configuration**: Memory storage, single file upload

- **`form-data@^4.0.4`**
  - **Purpose**: Constructs multipart form data for HTTP requests
  - **Why needed**: Forwards uploaded files from Node.js to Python service with metadata

### HTTP Client & Document Processing
- **`node-fetch@^2.7.0`**
  - **Purpose**: HTTP client for making external requests
  - **Why needed**: Communicates with Python backend service running on port 5000
  - **Usage**: Proxies upload/download requests, handles Watson Assistant responses

- **`mammoth@^1.11.0`**
  - **Purpose**: Converts DOCX files to text/HTML
  - **Why needed**: Backup document processing (primary processing in Python)

- **`pdf-parse@^2.4.5`**
  - **Purpose**: Extracts text from PDF files
  - **Why needed**: Fallback PDF processing capability in Node.js layer

---

## Python Dependencies (Backend Service)

### Web Framework
- **`Flask@3.0.0`**
  - **Purpose**: Main Python web framework
  - **Why needed**: Serves AI processing endpoints, handles document uploads to watsonx.ai
  - **Endpoints**: `/api/upload-to-watsonx`, `/api/get-requests`, `/api/update-status`

- **`Flask-CORS@4.0.0`**
  - **Purpose**: CORS support for Flask
  - **Why needed**: Allows Node.js gateway to communicate with Python service

### IBM Cloud Services
- **`ibm-watsonx-ai@1.0.5`**
  - **Purpose**: Official IBM watsonx.ai SDK
  - **Why needed**:
    - Generate embeddings using `ibm/slate-125m-english-rtrvr-v2` model
    - Store document chunks in Milvus vector database
    - Enable semantic search through student documents
  - **Key Features**: Embeddings, vector store integration, 768-dimensional vectors

- **`ibm-boto3@1.17.0` & `ibm-botocore@1.20.0`**
  - **Purpose**: IBM Cloud Object Storage client (S3-compatible)
  - **Why needed**:
    - Store original student documents for faculty download
    - Organize files by document ID: `{document_id}/{filename}`
    - Metadata storage for student information

### Vector Database
- **`pymilvus@2.3.4`**
  - **Purpose**: Milvus vector database client
  - **Why needed**:
    - Store 768-dimensional document embeddings
    - Enable semantic similarity search
    - Collection: `cpl_documents_v5` with HNSW index and L2 metric
    - Supports metadata filtering by student, course, request type

### Data Warehouse
- **`prestodb@0.8.4`**
  - **Purpose**: Presto SQL client for watsonx.data
  - **Why needed**:
    - Query Apache Iceberg tables containing CPL request metadata
    - Track request status, credits awarded, advisor notes
    - Table: `iceberg_data.cpl_schema.cpl_requests`

### Document Processing
- **`PyPDF2@3.0.1`**
  - **Purpose**: PDF text extraction
  - **Why needed**: Extract text content from student transcripts and certificates
  - **Processing**: Page-by-page text extraction for embedding generation

- **`python-docx@1.1.0`**
  - **Purpose**: Microsoft Word document processing
  - **Why needed**: Extract text from DOCX resumes and course descriptions
  - **Processing**: Paragraph-by-paragraph text extraction

### AI Text Processing
- **`langchain-text-splitters@0.2.2`**
  - **Purpose**: Intelligent document chunking
  - **Why needed**:
    - Split documents into 800-character chunks (optimized for 512 token limit)
    - Maintain semantic boundaries and context
    - 150-character overlap for continuity

- **`langchain-core@0.2.11`**
  - **Purpose**: Core LangChain document handling
  - **Why needed**: Document objects and metadata management for chunking pipeline

### Utilities
- **`python-dotenv@1.0.0`**
  - **Purpose**: Environment variable management
  - **Why needed**: Load 45+ configuration variables from .env file securely

- **`requests@2.31.0`**
  - **Purpose**: HTTP client library
  - **Why needed**: Make API calls to external services, health checks

- **`pandas@2.1.4` & `numpy@1.24.3`**
  - **Purpose**: Data manipulation and numerical operations
  - **Why needed**: Dependencies for AI libraries, data processing operations

---

## Frontend Dependencies

### External Services
- **IBM Watson Assistant**
  - **Integration ID**: `2d6e2e03-4cef-4e0f-b131-f989bc4776d2`
  - **Region**: `au-syd`
  - **Purpose**: Conversational AI interface for student interactions
  - **Features**: File upload integration, context tracking, natural language queries

- **Google Fonts (Lato)**
  - **Purpose**: Typography for consistent UI design
  - **Loaded via CDN**: Weights 300, 400, 500, 600, 700

### Browser APIs
- **File API**: Document upload handling
- **Fetch API**: HTTP requests to Node.js gateway
- **FormData API**: Multipart form construction

---

## Installation Instructions

### Node.js Setup
```bash
# Install Node.js dependencies
npm install

# Start Node.js gateway server
npm start
# Server runs on http://localhost:3000
```

### Python Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start Python backend service
python watson_upload.py
# Service runs on http://localhost:5000
```

### Environment Variables Required
Create `.env` file with 45+ variables including:
- IBM watsonx.ai credentials and project ID
- Milvus connection details (host, port, username, password)
- IBM Cloud Object Storage configuration
- watsonx.data Presto connection strings
- Iceberg catalog, schema, and table names

---

## System Architecture

```
Frontend (HTML/JS)
    ↓
Watson Assistant (Conversational UI)
    ↓
Node.js Gateway :3000 (File routing, CORS)
    ↓
Python Backend :5000 (AI processing)
    ↓
├── watsonx.ai (Embeddings + Vector Store)
├── Milvus (Vector Database)
├── IBM COS (Document Storage)
└── watsonx.data/Iceberg (Metadata Tables)
```

This architecture ensures scalable document processing with AI-powered semantic search capabilities for the CPL system.