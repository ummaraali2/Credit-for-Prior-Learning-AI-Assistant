# CPL Website - Credit for Prior Learning System

## Overview

The Credit for Prior Learning (CPL) Website is an AI-powered system that automates the evaluation of student documents for credit transfer and prior learning assessment at Northeastern University. The system integrates IBM watsonx.ai, vector databases, and conversational AI to provide intelligent document analysis and streamlined workflows for both students and faculty.

## Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │────│  Node.js        │────│  Python         │
│   (HTML/JS)     │    │  Gateway        │    │  Backend        │
│   Port: 3000    │    │  Port: 3000     │    │  Port: 5000     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        │              ┌─────────────────┐                │
        └──────────────│ Watson Assistant│                │
                       │   (IBM Cloud)   │                │
                       └─────────────────┘                │
                                                          │
           ┌──────────────────────────────────────────────┼─────────────┐
           │                                              │             │
   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐
   │  watsonx.ai   │  │    Milvus     │  │   IBM COS     │  │ watsonx.data │
   │  (Embeddings) │  │  (Vectors)    │  │ (Documents)   │  │  (Iceberg)   │
   └───────────────┘  └───────────────┘  └───────────────┘  └──────────────┘
```

### Technology Stack

**Frontend:**
- HTML5, CSS3, JavaScript (ES6+)
- IBM Watson Assistant (Conversational AI)
- Google Fonts (Lato)

**Backend:**
- **Node.js Gateway:** Express.js, CORS, Multer, FormData
- **Python AI Service:** Flask, IBM watsonx.ai SDK, PyMilvus
- **Document Processing:** PyPDF2, python-docx, LangChain

**External Services:**
- **IBM watsonx.ai:** AI embeddings and vector search
- **Milvus:** Vector database for semantic search
- **IBM Cloud Object Storage:** Original document storage
- **IBM watsonx.data:** Apache Iceberg tables for metadata

## Project Structure

```
CPL-Website/
├── backend/                          # Python AI processing services
│   ├── services/                     # Main application services
│   ├── handlers/                     # External service handlers
│   ├── scripts/                      # Setup and maintenance scripts
│   ├── utils/                        # Utility functions
│   └── config/                       # Configuration files
├── frontend/                         # Web application
│   ├── pages/                        # HTML pages
│   ├── assets/css/                   # Stylesheets
│   ├── assets/js/                    # JavaScript files
│   └── assets/images/                # Image assets
├── docs/                            # Documentation
│   ├── setup/                       # Installation guides
│   ├── api/                         # API documentation
│   └── architecture/                # System design docs
├── tests/                           # Test suites
│   ├── backend/                     # Python backend tests
│   ├── frontend/                    # JavaScript frontend tests
│   ├── integration/                 # API integration tests
│   └── e2e/                        # End-to-end browser tests
├── sql/schemas/                     # Database schemas
├── scripts/                         # Deployment and dev scripts
└── config/                          # Project configuration
```

## Features

### For Students
- **Document Upload:** Upload transcripts, resumes, course syllabi via Watson Assistant
- **AI-Powered Analysis:** Automatic text extraction and embedding generation
- **Status Tracking:** Check CPL request status and progress
- **Natural Language Interface:** Conversational interaction through Watson Assistant

### For Faculty/Advisors
- **Request Management:** Review and evaluate CPL requests
- **Document Access:** Download and preview original student documents
- **Status Updates:** Approve/deny requests with credit allocation
- **Metadata Search:** Find requests by student, course, or request type

### AI Capabilities
- **Semantic Search:** Vector-based similarity search through document content
- **Intelligent Chunking:** Context-aware document segmentation
- **Metadata Enrichment:** Embedded student context in searchable content
- **Multi-format Support:** PDF, DOCX, and TXT document processing

## Installation

### Prerequisites

- **Node.js:** 18.17.0 or higher
- **Python:** 3.9 or higher
- **IBM Cloud Account:** For watsonx.ai, COS, and watsonx.data access

### Environment Setup

1. **Clone Repository:**
```bash
git clone <repository-url>
cd CPL-Website
```

2. **Install Node.js Dependencies:**
```bash
npm install
```

3. **Install Python Dependencies:**
```bash
pip install -r docs/setup/requirements.txt
```

4. **Configure Environment Variables:**
Create a `.env` file in the project root with the following variables:

```bash
# IBM watsonx.ai Configuration
WATSONX_AI_APIKEY=your_watsonx_api_key
WATSONX_AI_SERVICE_URL=https://us-south.ml.cloud.ibm.com
WATSONX_AI_PROJECT_ID=your_project_id

# Milvus Vector Database
MILVUS_CONNECTION_ID=your_milvus_connection_id
MILVUS_HOST=your_milvus_host
MILVUS_PORT=32668
MILVUS_USERNAME=your_username
MILVUS_PASSWORD=your_password

# IBM Cloud Object Storage
COS_API_KEY=your_cos_api_key
COS_INSTANCE_ID=your_cos_instance_id
COS_ENDPOINT=https://s3.us-south.cloud-object-storage.ibmcloud.com
COS_BUCKET_NAME=cpl-documents

# IBM watsonx.data (Iceberg)
WATSONX_DATA_HOST=your_presto_host
WATSONX_DATA_PORT=30670
WATSONX_DATA_USER=ibmlhapikey_your_email
WATSONX_DATA_PASSWORD=your_api_key
ICEBERG_CATALOG=iceberg_data
ICEBERG_SCHEMA=cpl_schema
ICEBERG_TABLE=cpl_requests
```

### Database Setup

1. **Create Milvus Collection:**
```bash
cd backend/scripts
python create_cpl_collection.py
```

2. **Create Iceberg Table:**
```bash
# Execute the SQL schema in watsonx.data
cat sql/schemas/CREATE-TABLE.sql
```

### Service Startup

1. **Start Python Backend:**
```bash
cd backend/services
python watson_upload.py
# Service runs on http://localhost:5000
```

2. **Start Node.js Gateway:**
```bash
npm start
# Service runs on http://localhost:3000
```

3. **Access Application:**
Open browser to: `http://localhost:3000/frontend/pages/index.html`

## API Documentation

### Node.js Gateway Endpoints

- `POST /api/upload` - Upload student documents
- `GET /api/download-document/:documentId/:filename` - Download documents
- `GET /api/preview-document/:documentId/:filename` - Preview documents
- `GET /api/requests` - Get all CPL requests
- `GET /api/requests-by-nuid/:nuid` - Get requests by student ID
- `PUT /api/requests/:id/status` - Update request status
- `GET /health` - Service health check

### Python Backend Endpoints

- `POST /api/upload-to-watsonx` - Process documents with AI
- `GET /api/get-requests` - Query Iceberg for requests
- `PUT /api/update-status` - Update request status in Iceberg
- `POST /api/search` - Vector search through documents
- `GET /health` - Service health check

## Testing

### Run All Tests
```bash
npm test
```

### Backend Python Tests
```bash
cd tests
python -m pytest backend/ -v --cov=backend
```

### Frontend JavaScript Tests
```bash
cd tests/frontend
npm test
```

### Integration Tests
```bash
python -m pytest tests/integration/ -v
```

### End-to-End Tests
```bash
npx playwright test tests/e2e/
```

## Configuration

### Chunk Size Optimization
The system uses 800-character chunks with 150-character overlap, optimized for the 512-token limit of the IBM embedding model.

### Vector Store Configuration
- **Collection:** `cpl_documents_v5`
- **Index Type:** HNSW with L2 metric
- **Dimensions:** 768 (embedding vector size)

### Security
- All API keys stored in environment variables
- CORS enabled for cross-origin requests
- File type validation for uploads
- Authentication through IBM Cloud services

## Deployment

### Production Considerations
- Use environment-specific `.env` files
- Enable HTTPS for all services
- Configure load balancing for high availability
- Set up monitoring and logging
- Implement backup strategies for vector data

### Environment Variables for Production
Update the following for production deployment:
- Use production IBM Cloud service URLs
- Configure production Milvus cluster
- Set up production COS buckets
- Use production Iceberg catalogs

## Contributing

1. **Code Style:** Follow ESLint for JavaScript, Black for Python
2. **Testing:** Maintain test coverage above 80%
3. **Documentation:** Update README for significant changes
4. **Version Control:** Use feature branches and pull requests

## Support

### Common Issues

**Service Connection Errors:**
- Verify environment variables are correctly set
- Check IBM Cloud service status
- Ensure Milvus and Iceberg services are running

**File Upload Failures:**
- Check file size limits (default: 50MB)
- Verify supported file types: PDF, DOCX, TXT
- Ensure COS bucket permissions are correct

**Watson Assistant Issues:**
- Verify Watson Assistant credentials
- Check CORS configuration for embedded iframe
- Ensure proper integration ID and region settings

### Logs and Monitoring
- Node.js logs: Console output from `npm start`
- Python logs: Console output from backend services
- Browser logs: Developer Tools Console
- Vector database logs: Milvus server logs

## License

This project is licensed under the ISC License - see the package.json file for details.

## Acknowledgments

- Northeastern University College of Professional Studies
- IBM watsonx.ai and IBM Cloud services
- Open source community for Python and Node.js packages