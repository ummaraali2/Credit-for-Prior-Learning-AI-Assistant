# CPL Website - Project Structure

## Overview
```
CPL-Website/
├── backend/                          # Python backend services
│   ├── services/                     # Main application services
│   │   ├── watson_upload.py         # Main AI processing service (port 5000)
│   │   └── simple_server.py         # Query service for Watson Assistant
│   ├── handlers/                     # External service handlers
│   │   ├── cos_handler.py           # IBM Cloud Object Storage handler
│   │   └── iceberg_handler.py       # Iceberg/watsonx.data handler
│   ├── scripts/                      # Setup and maintenance scripts
│   │   ├── create_cpl_collection.py # Create Milvus collection
│   │   ├── load.py                  # Load Milvus collection
│   │   ├── verify_upload.py         # Verify uploads
│   │   ├── inspect_schema.py        # Database schema inspection
│   │   ├── list_models.py           # List available AI models
│   │   └── add_student_fields.py    # Database field management
│   ├── utils/                        # Utility functions
│   │   ├── check.py                 # General checks
│   │   ├── check2.py                # Additional checks
│   │   ├── verify_collection.py     # Collection verification
│   │   ├── flush.py                 # Data cleanup
│   │   ├── upload_nu_syllabi.py     # Bulk syllabus upload
│   │   └── verify.py                # Data verification
│   └── config/                       # Configuration files (empty)
│
├── frontend/                         # Frontend application
│   ├── pages/                        # HTML pages
│   │   ├── index.html               # Student portal (main page)
│   │   ├── landing.html             # Landing page
│   │   ├── faculty.html             # Faculty dashboard
│   │   ├── faculty-status.html      # Faculty status management
│   │   └── student-status.html      # Student status checking
│   ├── assets/                       # Static assets
│   │   ├── css/                     # Stylesheets
│   │   │   ├── styles.css           # Main styles
│   │   │   ├── status-styles.css    # Status page styles
│   │   │   └── student-status-styles.css # Student status styles
│   │   ├── js/                      # JavaScript files
│   │   │   ├── script.js            # Main frontend logic
│   │   │   ├── faculty-script.js    # Faculty dashboard logic
│   │   │   ├── status-script.js     # Status page logic
│   │   │   └── student-status-script.js # Student status logic
│   │   └── images/                  # Image assets
│   │       └── logo.png             # NU/CPL logo
│   └── components/                   # Reusable components (empty)
│
├── docs/                            # Documentation
│   ├── setup/                       # Setup and installation docs
│   │   ├── DEPENDENCIES.md         # Complete dependency documentation
│   │   ├── requirements.txt        # Python dependencies
│   │   └── h.txt                   # Setup notes
│   ├── api/                        # API documentation
│   │   ├── open api spec.json      # OpenAPI specification
│   │   ├── openapi-with-ngrok.json # Ngrok-enabled API spec
│   │   └── openapi with RAG.json   # RAG-enhanced API spec
│   └── architecture/               # Architecture documentation
│       ├── changesto script.txt    # Script change log
│       ├── explain.txt             # System explanation
│       ├── oldscript.txt          # Previous script versions
│       ├── oldupload.txt          # Previous upload logic
│       └── uploadservice.txt       # Upload service notes
│
├── sql/                            # Database schemas
│   └── schemas/                    # SQL schema definitions
│       └── CREATE-TABLE.sql       # Iceberg table creation
│
├── scripts/                        # Project management scripts
│   ├── deployment/                 # Deployment scripts (empty)
│   └── development/                # Development scripts (empty)
│
├── config/                         # Configuration files (empty)
│
├── tests/                          # Test files
│   ├── backend/                    # Backend tests (empty)
│   └── frontend/                   # Frontend tests (empty)
│
├── server.js                       # Node.js gateway server (port 3000)
├── package.json                    # Node.js dependencies
├── package-lock.json               # Node.js dependency lock
├── PROJECT_STRUCTURE.md            # This file
├── upload/                         # Temporary upload directory
├── PJMSyllabi-Cleaned.zip         # Sample data
└── venv/                          # Python virtual environment
```

## Key Components

### Backend Services
- **`watson_upload.py`**: Main AI processing service that handles document uploads, text extraction, embedding generation, and storage in Milvus/COS/Iceberg
- **`simple_server.py`**: Query service that provides student data to Watson Assistant

### Handlers
- **`cos_handler.py`**: Manages IBM Cloud Object Storage for original document storage
- **`iceberg_handler.py`**: Manages Apache Iceberg tables for metadata storage via Presto

### Frontend
- **`index.html`**: Main student portal with Watson Assistant integration
- **`faculty.html`**: Faculty dashboard for reviewing CPL requests
- **`script.js`**: Main frontend logic with file upload and Watson Assistant integration

## Service Architecture

```
Frontend (pages/) → Node.js Gateway (server.js:3000) → Python Backend (services/:5000)
                                                          ├── watsonx.ai (Embeddings)
                                                          ├── Milvus (Vector Database)
                                                          ├── IBM COS (Document Storage)
                                                          └── Iceberg (Metadata Tables)
```

## How to Start Services

### Backend (Python)
```bash
cd backend/services
python watson_upload.py
# Runs on http://localhost:5000
```

### Gateway (Node.js)
```bash
npm start
# Runs on http://localhost:3000
```

### Frontend
Access via: http://localhost:3000 (served by Node.js)

## Import Path Updates
After reorganization, Python services use relative imports with path adjustments:
```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from handlers.iceberg_handler import get_iceberg_handler
from handlers.cos_handler import get_cos_handler
```

