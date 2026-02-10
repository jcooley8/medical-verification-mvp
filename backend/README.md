# Medical Verification MVP - Backend

## Overview
This backend implements a document ingestion API with async OCR processing using Celery workers.

## Architecture

### Components
1. **FastAPI Web Server** - REST API endpoints
2. **PostgreSQL Database** - Document metadata and results
3. **Redis** - Celery message broker
4. **Celery Worker** - Async document processing

### Implemented Features

#### 1. Document Upload API
**Endpoint:** `POST /api/v1/documents/upload`

- Accepts PDF file uploads
- Validates file type (application/pdf only)
- Saves files to `/code/uploads/` directory
- Creates database record with `QUEUED` status
- Triggers Celery task for processing

**Response:**
```json
{
  "message": "Document uploaded successfully",
  "document_id": 1,
  "filename": "medical-record.pdf",
  "status": "QUEUED",
  "created_at": "2024-01-15T10:30:00"
}
```

#### 2. Document Status API
**Endpoint:** `GET /api/v1/documents/{document_id}`

Returns document details including processing status and OCR results.

**Endpoint:** `GET /api/v1/documents`

Lists all uploaded documents.

#### 3. Celery Worker
**Task:** `process_document(document_id)`

- Updates document status to `PROCESSING`
- Runs MockOCRService to extract text and bounding boxes
- Updates status to `COMPLETED` with results
- Handles failures and updates status to `FAILED`

#### 4. Mock OCR Service
**Class:** `MockOCRService`

Simulates AWS Textract OCR processing:
- 2-second processing delay
- Returns realistic OCR output with:
  - Word-level text extraction
  - Confidence scores
  - Bounding box coordinates
  - Page dimensions

**Purpose:** Test async infrastructure without AWS credentials

## Database Schema

### Document Model
```python
{
  "id": Integer (primary key),
  "filename": String,
  "status": Enum (QUEUED, PROCESSING, COMPLETED, FAILED),
  "created_at": DateTime,
  "updated_at": DateTime,
  "file_path": String,
  "ocr_result": String (JSON)
}
```

## Running the Application

### Start Services
```bash
docker compose up
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379
- Backend API on port 8000
- Celery worker

### Test Document Upload
```bash
# Upload a PDF
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test-document.pdf"

# Check document status
curl "http://localhost:8000/api/v1/documents/1"

# List all documents
curl "http://localhost:8000/api/v1/documents"
```

### Monitor Celery Worker
Watch the celery_worker container logs:
```bash
docker compose logs -f celery_worker
```

Expected output:
```
celery_worker_1  | Processing document 1: test-document.pdf
celery_worker_1  | Running Mock OCR on /code/uploads/test-document.pdf...
celery_worker_1  | Mock OCR done for document 1
celery_worker_1  | Document 1 processing completed successfully
```

## File Structure
```
backend/
├── app/
│   ├── main.py           # FastAPI application & upload endpoint
│   ├── database.py       # SQLAlchemy database configuration
│   ├── models.py         # Document model & DocumentStatus enum
│   ├── tasks.py          # Celery task: process_document
│   ├── celery_app.py     # Celery configuration
│   ├── ocr_service.py    # MockOCRService class
│   └── schemas.py        # Pydantic schemas (existing)
├── Dockerfile
├── requirements.txt
└── README.md
```

## Next Steps
1. Replace MockOCRService with real AWS Textract integration
2. Add S3 storage instead of local filesystem
3. Implement retry logic for failed documents
4. Add authentication and authorization
5. Create frontend for document upload and viewing
