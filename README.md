# CPL Website - Credit for Prior Learning System

## Demo




https://github.com/user-attachments/assets/d19141b0-c3c5-4775-a6d3-87533f9654f3

https://github.com/user-attachments/assets/fcfc93b7-9039-4644-b029-4cb7c437f819

https://github.com/user-attachments/assets/28345918-b92f-4ec1-947c-86aeb0a44f01

https://github.com/user-attachments/assets/00af5f6f-eae7-4cba-afed-b9a98125de3d






# Credit for Prior Learning (CPL) AI Assistant

> Intelligent automation system for evaluating student learning experiences for academic credit at Northeastern University's College of Professional Studies, built in partnership with IBM Research.

**GitHub:** https://github.com/ummaraali2/Credit-for-Prior-Learning-AI-Assistant

---

## Problem Statement

This project originated as a capstone at Northeastern University, sponsored by IBM Research and the College of Professional Studies. The problem came directly from academic advisors: they are overwhelmed by Credit for Prior Learning requests, particularly at the start of each semester when volume spikes. Each request requires a faculty reviewer to manually read through student-submitted documents, map qualifications against course learning outcomes, and render a decision with no AI assistance and no structured workflow.

The burden falls on both sides. Students with relevant professional experience have no way to gauge whether their application is worth pursuing before investing hours assembling documentation. Advisors and faculty have no tooling to surface the most relevant evidence inside lengthy submissions. The result is long turnaround times, inconsistent decisions, and a process that effectively discourages the students most likely to qualify.

I was also motivated by the opportunity to work directly with IBM Cloud and understand their AI services in a production-grade context. I led the project and was responsible for the full technical build. Success looked like: a system where students submit stronger applications with less friction, faculty spend time on judgment calls rather than document triage, and the entire workflow is traceable and auditable.

---

## Solution Overview

The CPL AI Assistant is a full-stack intelligent workflow system that automates the end-to-end CPL process, from application intake through faculty review and credit award.

Students interact through a Watson Assistant conversational interface embedded in a web portal. They describe their background, upload supporting documents (resumes, transcripts, certifications, project portfolios), and walk through a guided application flow before submitting. A separate faculty portal provides evaluation summaries grounded in retrieved document evidence, an inline document viewer, and a structured decision workflow.

AI is core to the solution, not supplementary. Without it, the system would be a form with a document upload button. The RAG pipeline is what makes competency assessment possible: it retrieves relevant course syllabus sections from a vector store, compares them against student submissions, and generates evidence-grounded evaluations with confidence indicators. The conversational interface does more than collect data. It guides students through articulating their experience in terms that map to course learning outcomes. Neither capability is meaningful without the underlying AI.

**Tech stack:** IBM Watson Assistant, IBM watsonx.ai (slate-125m-english-rtrvr-v2 embedding model), Milvus vector database, IBM watsonx.data (Apache Iceberg via Presto), IBM Cloud Object Storage, Python/Flask, Node.js/Express, LangChain, PyPDF2, python-docx.

---

## AI Integration

**Models and APIs used:**
- IBM watsonx.ai with the `slate-125m-english-rtrvr-v2` embedding model for high-dimensional semantic embeddings optimized for retrieval tasks
- Watson Assistant for conversational flow, session state management, and LLM looping via custom OpenAPI extensions
- LangChain for RAG pipeline orchestration, text splitting, and document loader abstraction

**Agentic patterns:**
- RAG: student documents are chunked, embedded, and stored in Milvus; at evaluation time, the pipeline retrieves the most semantically similar syllabus sections, then generates a competency mapping grounded in retrieved evidence
- Multi-turn reasoning: Watson Assistant Actions loop back to the LLM extension across turns, passing accumulated conversation history as context on each call, enabling the chatbot to maintain coherent state through a multi-step application without re-prompting from scratch
- Tool use: Watson Assistant calls custom extensions (defined via OpenAPI spec) for document processing, status lookups, and LLM completions, keeping business logic in the backend while the conversational layer stays focused on dialogue management

**Tradeoffs considered:**
- Chose Milvus over managed vector services to keep data on IBM infrastructure, which was a hard requirement given FERPA obligations; the cost was more operational overhead setting up the HNSW index and managing the collection schema
- The IBM slate embedding model produces larger embeddings than lightweight alternatives, increasing storage and search latency slightly, but retrieval quality on domain-specific educational text was noticeably better
- Watson Assistant character limits for session variables required careful chunking of conversation history passed to the LLM extension; the workaround (appending to a structured rolling buffer rather than raw transcript) introduced complexity but kept context coherent

**Where AI exceeded expectations:** The automated post-submission workflow performed better than expected end to end. Once a student submits, the system stores the application, runs the intelligent routing algorithm to assign the most appropriate faculty reviewer based on department and workload, and dispatches notifications to both parties without any manual intervention. During user testing this pipeline ran without failures across all test scenarios, which was not a given given the number of services involved. The context-aware chunking also preserved document meaning better than a naive fixed-size approach would have, which kept semantic search results coherent across long professional resumes and multi-page project portfolios.

**Where it fell short:** Watson Assistant's Actions vs. Dialog skill distinction introduced early architectural friction. Looping behavior and context variable handling differ between them in non-obvious ways, and the debugging surface is limited. The system also has no graceful fallback when a student's document is a scanned image rather than searchable text; OCR preprocessing is required before upload.

---

## Architecture and Design Decisions

The system uses a three-tier architecture. For the full architecture diagram, see [CPL Project Documentation.pdf](docs/CPL%20Project%20Documentation.pdf) (Appendix A).
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
     ┌────────────────────────────────────────────────────┼──────────────┐
     │                                                    │              │
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ watsonx.ai   │  │   Milvus     │  │  IBM COS     │  │ watsonx.data │
│ (Embeddings) │  │  (Vectors)   │  │ (Documents)  │  │  (Iceberg)   │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

**Project structure:**

```
Credit-for-Prior-Learning-AI-Assistant/
├── backend/                    # Python AI processing services
│   ├── services/               # Main application services
│   ├── handlers/               # External service handlers
│   ├── scripts/                # Setup and maintenance scripts
│   ├── utils/                  # Utility functions
│   └── config/                 # Configuration files
├── deployments/                # Jupyter Notebook RAG pipeline deployed as a watsonx.ai online function
│   └── watsonx-ai/
├── frontend/                   # Web application
│   ├── pages/                  # HTML pages
│   ├── assets/css/             # Stylesheets
│   ├── assets/js/              # JavaScript files
│   └── assets/images/
├── docs/                       # Documentation
│   ├── setup/                  # Installation guides
│   ├── api/                    # OpenAPI specs
│   └── architecture/           # System design docs
├── tests/                      # Test suites
│   ├── backend/                # Python backend tests
│   ├── frontend/               # JavaScript frontend tests
│   ├── integration/            # API integration tests
│   └── e2e/                    # End-to-end browser tests
├── sql/schemas/                # Database schemas
├── server.js                   # Node.js gateway entry point
├── package.json
└── pytest.ini
```

**Presentation layer:** Watson Assistant web chat widget embedded in HTML5 portals. The student portal handles application submission; the faculty portal handles evaluation. Both are served as static assets from the Node.js gateway.

**Application layer (dual-backend):**
- Node.js/Express gateway handles HTTP routing, CORS, and file upload (via Multer). It proxies requests to the Python backend and serves the frontend.
- Python/Flask AI backend handles document processing (PyPDF2, python-docx), embedding generation via the watsonx.ai API, vector storage and retrieval via PyMilvus, and RAG pipeline orchestration via LangChain.

**Data layer:**
- Milvus vector database stores embeddings with an 8-field schema including student metadata, enabling filtered semantic search (e.g., retrieve only embeddings from a specific student's submission)
- IBM watsonx.data (Apache Iceberg via Presto) stores application metadata with full ACID compliance, partitioned by status for efficient queue queries
- IBM Cloud Object Storage preserves original documents (S3-compatible API)

**Key design decisions:**

**1. Dual portal with dual Watson Assistant instances.** Rather than a single interface with role-based views, I deployed two fully separate portals (student and faculty), each backed by its own Watson Assistant instance. The student-facing assistant is optimized for guided application intake across multiple turns; the faculty-facing assistant is optimized for application queries and status management. This kept each conversational flow clean and purpose-built. The tradeoff is maintaining two assistant configurations, but the clarity in each user experience justified it.

**2. Building a Milvus vector store from scratch instead of using the default watsonx vector database.** IBM watsonx.data includes a built-in vector store, but I chose to set up Milvus independently for three reasons: finer control over the index type (HNSW with L2 metric), the ability to include student metadata fields in the schema for filtered search (so a faculty reviewer querying for a specific student only retrieves that student's embeddings), and keeping the vector store portable and not locked to a specific IBM service tier. Building the 8-field schema from scratch added setup time but gave retrieval behavior I could tune directly.

**3. Using LangChain as the RAG orchestration layer.** The alternative was wiring the pipeline manually: call the watsonx.ai embedding API, push to Milvus, retrieve, call the generation API. LangChain abstracts this into composable components (document loaders, text splitters, vectorstore interfaces, chains) that made the pipeline easier to reason about and iterate on. The tradeoff is a dependency that adds abstraction overhead, but for a project with evolving chunking and retrieval logic the flexibility was the right call.

**4. OpenAPI extension design for Watson Assistant communication.** Connecting Watson Assistant to the backend required defining a custom extension via an OpenAPI specification. Three approaches were designed and tested: a baseline spec connecting directly to the Flask backend, a RAG-integrated spec that routes evaluation requests through the full pipeline, and an ngrok-tunneled variant for local development and testing before the backend had a stable public endpoint. These specs are in [`docs/api/`](docs/api/). The production build uses the RAG-integrated spec.

---

## What AI Helped With (and Where It Got in the Way)

**Where AI coding tools accelerated development:**

Claude and Copilot were most useful for boilerplate-heavy tasks: writing the OpenAPI spec for Watson Assistant custom extensions, scaffolding the LangChain pipeline structure, and generating the Milvus collection schema and index configuration from the documented parameter space. Tasks that would have taken an hour of reading IBM documentation were compressed to minutes of prompting and verification.

The Watson Assistant web chat integration, particularly the `writeableElements` API and `updateUserDefinedResponse` patterns, was also faster with AI assistance since the documentation is dense and the API surface is narrow.

**Where AI tools got in the way:**

IBM-specific SDK behavior was a persistent gap. Suggestions for `ibm-watsonx-ai` method signatures, Milvus `DataType` enum values, and Presto SQL quirks in watsonx.data were frequently wrong or outdated. The pattern that emerged: use AI tools to scaffold structure and identify the right abstractions, then go directly to IBM documentation to verify parameters and handle edge cases. Trusting generated IBM SDK code without verification added debugging time.

Watson Assistant session variable handling, especially passing structured context to LLM extensions, required iterative debugging that AI tools could not meaningfully accelerate, because the failure modes (silent truncation, context drops between steps) only surface at runtime inside the Watson console.

---

## Getting Started

### System Requirements

**End users (students and faculty):** Modern web browser (Chrome, Firefox, Safari, Edge), JavaScript enabled, stable internet connection.

**System administrators:** Node.js 18+, Python 3.9+, Linux/macOS/Windows Server.

**External services required:** IBM Cloud account with active subscriptions for watsonx.ai, Watson Assistant, Cloud Object Storage, and watsonx.data; Milvus cluster (self-hosted or cloud-managed).

### Installation

```bash
# Clone the repository
git clone https://github.com/ummaraali2/Credit-for-Prior-Learning-AI-Assistant.git
cd Credit-for-Prior-Learning-AI-Assistant

# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Full `.env` reference:

```bash
# IBM watsonx.ai
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

```bash
# Initialize the Milvus collection
cd backend/scripts && python create_cpl_collection.py

# Initialize the Iceberg metadata table
# Execute sql/schemas/CREATE-TABLE.sql in your watsonx.data Presto interface

# Start services in two terminals

# Terminal 1 - Python AI backend (runs on http://localhost:5000):
cd backend/services && python watson_upload.py

# Terminal 2 - Node.js gateway (runs on http://localhost:3000):
npm start

# Access the application:
# open http://localhost:3000/frontend/pages/index.html
```

See [`docs/setup/requirements.txt`](docs/setup/requirements.txt) and [`docs/setup/DEPENDENCIES.md`](docs/setup/DEPENDENCIES.md) for complete dependency lists. For full installation instructions, environment variable reference, and service verification steps, see the [User Manual](docs/User%20Manual.pdf).

---

The student flow begins with the Watson Assistant widget in the bottom-right of the portal. Students greet the bot, select an application type (experience-based CPL, prior coursework, or credit transfer), provide detailed information about their background, and upload supporting documents. A unique application ID is generated on submission for status tracking.

Faculty access the review portal, where each application shows a RAG-grounded evaluation summary, an inline document viewer with highlighted evidence, and a decision form for approvals, denials, or information requests.

 Screenshots and architecture diagrams are in [CPL Project Documentation.pdf](docs/CPL%20Project%20Documentation.pdf) (Appendix A). (Appendix B).

---

## Testing and Error Handling

The system was tested across three surfaces: unit tests for the Python backend (covering text extraction, chunking, and embedding pipeline), integration tests for the Node.js gateway (file upload routing, CORS, proxy behavior), and end-to-end user testing with real student and faculty participants.

Test configuration is managed via `pytest.ini`. The test suite is in [`tests/`](tests/).

**Running tests:**

```bash
# All tests
npm test

# Python backend tests with coverage
python -m pytest tests/backend/ -v --cov=backend

# Integration tests
python -m pytest tests/integration/ -v

# End-to-end browser tests
npx playwright test tests/e2e/
```

**API endpoints (Node.js gateway, port 3000):**
- `POST /api/upload` - Upload student documents
- `GET /api/download-document/:documentId/:filename` - Download documents
- `GET /api/preview-document/:documentId/:filename` - Preview documents inline
- `GET /api/requests` - Get all CPL requests
- `GET /api/requests-by-nuid/:nuid` - Get requests by student ID
- `PUT /api/requests/:id/status` - Update request status
- `GET /health` - Service health check

**API endpoints (Python backend, port 5000):**
- `POST /api/upload-to-watsonx` - Process and embed documents
- `GET /api/get-requests` - Query Iceberg for requests
- `PUT /api/update-status` - Update request status in Iceberg
- `POST /api/search` - Vector search through documents
- `GET /health` - Service health check

**Vector store configuration:**
- Collection: `cpl_documents_v5`
- Index type: HNSW with L2 metric
- Embedding dimensions: 768 (IBM slate model output)
- Chunk size: 800 characters with 150-character overlap, tuned to the 512-token embedding model limit

Error handling covers the failure modes most likely to occur in production: file type mismatches and oversized uploads (caught at the Node.js layer before reaching the backend), text extraction failures on scanned PDFs (surfaced to the user with an OCR recommendation), Milvus connection failures (logged with retry logic), and Watson Assistant API timeouts (handled with exponential backoff in the custom extension). The Iceberg metadata table uses ACID transactions to prevent partial writes on application submission.

The user testing report covering task completion rates, qualitative feedback, and identified pain points is in [docs/full-documentation.md](docs/full-documentation.md), Section IV.

---

## Future Improvements

- **Generalized prompts for easier scaling.** The current prompts are tuned specifically for PJM (Project Management) courses at Northeastern. Making them more generalized, so that department, course code, and learning outcome structure are injected dynamically rather than hardcoded, would make it far easier to extend to other programs without rewriting the AI pipeline.
- **Handoff-ready architecture for sponsors.** I would refactor with the IBM team's operational standards in mind from the start, specifically using IBM-native deployment patterns (watsonx.ai online functions for all AI components, watsonx Orchestrate for workflow automation) so that IBM Research or the College of Professional Studies could take ownership of the codebase and scale it without depending on my original setup choices.
- **OCR preprocessing pipeline.** Automatically detect and process scanned PDFs at upload time, rather than returning an error and asking users to pre-process externally.
- **LMS and SIS integration.** Webhook-based status sync with Northeastern's student information system so credit awards post automatically rather than requiring registrar action.
- **Confidence calibration.** The assessment confidence indicators are not yet calibrated against faculty decision outcomes. A feedback loop that updates scoring based on accepted/denied decisions would improve reliability over time.

---

## Documentation

| File | Contents |
|------|----------|
| [`docs/user-manual.md`](docs/User%20Manual.pdf) | Complete installation guide, student portal walkthrough, faculty portal walkthrough, troubleshooting, FAQ, security and compliance notes, and full references for all libraries, SDKs, and frameworks used |
| [`docs/full-documentation.md`](docs/setup/CPL%20Project%20Documentation.pdf) | Full project documentation including competitor analysis, project development plan, work breakdown structure, schedule, risk/quality/communication plans, user testing plan, user testing report, and architecture appendices |
| [`docs/setup/requirements.txt`](docs/setup/requirements.txt) | Python dependency list |
| [`docs/setup/DEPENDENCIES.md`](docs/setup/DEPENDENCIES.md) | Annotated dependency reference |
| [`docs/api/`](docs/api/) | OpenAPI specifications for Watson Assistant custom extensions (baseline, RAG-integrated, and ngrok variants) |
| [`docs/architecture/`](docs/architecture/) | Architecture decision records and script history |
| `sql/` | Iceberg table DDL and query examples |

---

## Acknowledgments and Third-Party Components

**IBM Services:** IBM watsonx.ai, Watson Assistant, Cloud Object Storage, watsonx.data (Apache Iceberg / Presto). Used under IBM Cloud subscription terms.

**Open-source libraries (Python):** Flask, LangChain, PyMilvus, PyPDF2, python-docx, ibm-watsonx-ai SDK, ibm-cos-sdk, pandas, pydantic, aiohttp. See [`docs/setup/requirements.txt`](docs/setup/requirements.txt) for full versions.

**Open-source libraries (Node.js):** Express.js, Multer, CORS, dotenv, uuid, axios. See [`package.json`](package.json) for full versions.

**Infrastructure:** Milvus vector database (Apache 2.0 license). Apache Iceberg (Apache 2.0 license).

A complete annotated reference list covering all libraries, SDKs, frameworks, Watson services documentation, and third-party resources is in the [User Manual](docs/setup/User%20Manual.pdf) (References section).

---

## Project Background

Capstone project, Team 06, Northeastern University College of Professional Studies, in partnership with IBM Research.
Technical Lead: Ummara Ali
Contact: ummaraali2020@gmail.com
GitHub Issues: https://github.com/ummaraali2/Credit-for-Prior-Learning-AI-Assistant/issues
