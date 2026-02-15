# API Documentation

Complete reference for the Medical Verification MVP REST API.

**Base URL**: `http://localhost:8000` (development) or your deployed URL

**API Version**: v1

## Table of Contents

- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Upload Document](#upload-document)
  - [Get Document Status](#get-document-status)
  - [List All Documents](#list-all-documents)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

## Authentication

**Current Version**: No authentication required (MVP)

**Future**: Will implement API key or JWT-based authentication.

## Endpoints

### Health Check

Check if the API and database are operational.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "ok",
  "database": "connected",
  "service": "medical-verification-mvp"
}
```

**Status Codes**:
- `200 OK`: Service is healthy
- `503 Service Unavailable`: Database connection failed

**Example**:
```bash
curl http://localhost:8000/health
```

---

### Upload Document

Upload a PDF document for processing through the extraction pipeline.

**Endpoint**: `POST /api/v1/documents/upload`

**Content-Type**: `multipart/form-data`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| file | File | Yes | PDF file to process (max 50MB) |

**Response**:
```json
{
  "message": "Document uploaded successfully",
  "document_id": 1,
  "filename": "medical_record.pdf",
  "status": "QUEUED",
  "created_at": "2024-02-09T12:00:00",
  "file_size_bytes": 524288
}
```

**Status Codes**:
- `200 OK`: Document uploaded and queued for processing
- `400 Bad Request`: Invalid file type or missing file
- `413 Payload Too Large`: File exceeds size limit
- `500 Internal Server Error`: Server error

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@medical_record.pdf"
```

**JavaScript Example**:
```javascript
const formData = new FormData();
formData.append('file', pdfFile);

const response = await fetch('http://localhost:8000/api/v1/documents/upload', {
  method: 'POST',
  body: formData,
});

const data = await response.json();
console.log('Document ID:', data.document_id);
```

---

### Get Document Status

Retrieve the processing status and extracted data for a specific document.

**Endpoint**: `GET /api/v1/documents/{document_id}`

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| document_id | integer | Yes | ID of the document (path parameter) |

**Response**:
```json
{
  "document_id": 1,
  "filename": "medical_record.pdf",
  "status": "COMPLETED",
  "created_at": "2024-02-09T12:00:00",
  "updated_at": "2024-02-09T12:01:30",
  "document_type": "CHRONOLOGY",
  "file_path": "/code/uploads/medical_record.pdf",
  "extraction_result": {
    "patient_name": "John Doe",
    "events": [
      {
        "date": "2024-01-15",
        "provider": "Memorial Hospital",
        "encounter_type": "Emergency Visit",
        "summary": "Patient presented with...",
        "diagnosis_codes": ["M54.5"],
        "source_refs": [
          {
            "field": "date",
            "page_number": 1,
            "bounding_box": {
              "left": 0.1,
              "top": 0.2,
              "width": 0.15,
              "height": 0.02
            },
            "confidence": 0.98,
            "matched_text": "2024-01-15",
            "strategy": "date"
          }
        ]
      }
    ],
    "_match_summary": {
      "total_fields": 15,
      "matched": 14,
      "unmatched": 1,
      "fuzzy_matched": 2,
      "multiword_matched": 3,
      "match_rate": 0.93
    }
  },
  "ocr_result": "{...}"  // Raw OCR data (stringified JSON)
}
```

**Status Values**:
- `QUEUED`: Document uploaded, waiting for processing
- `PROCESSING`: Currently being processed
- `COMPLETED`: Processing finished successfully
- `FAILED`: Processing failed (check logs)

**Document Types**:
- `CHRONOLOGY`: Medical chronology/records
- `BILL`: Medical billing document

**Status Codes**:
- `200 OK`: Document found and returned
- `404 Not Found`: Document ID doesn't exist
- `500 Internal Server Error`: Database error

**Example**:
```bash
curl http://localhost:8000/api/v1/documents/1
```

**Polling Pattern** (JavaScript):
```javascript
async function waitForProcessing(documentId) {
  while (true) {
    const response = await fetch(`http://localhost:8000/api/v1/documents/${documentId}`);
    const doc = await response.json();
    
    if (doc.status === 'COMPLETED') {
      return doc.extraction_result;
    } else if (doc.status === 'FAILED') {
      throw new Error('Processing failed');
    }
    
    // Poll every 2 seconds
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
}
```

---

### List All Documents

Retrieve a list of all uploaded documents.

**Endpoint**: `GET /api/v1/documents`

**Response**:
```json
{
  "count": 3,
  "documents": [
    {
      "document_id": 3,
      "filename": "latest_record.pdf",
      "status": "QUEUED",
      "document_type": null,
      "created_at": "2024-02-09T12:05:00"
    },
    {
      "document_id": 2,
      "filename": "bill_jan2024.pdf",
      "status": "COMPLETED",
      "document_type": "BILL",
      "created_at": "2024-02-09T12:02:00"
    },
    {
      "document_id": 1,
      "filename": "medical_record.pdf",
      "status": "COMPLETED",
      "document_type": "CHRONOLOGY",
      "created_at": "2024-02-09T12:00:00"
    }
  ]
}
```

**Status Codes**:
- `200 OK`: List returned successfully
- `500 Internal Server Error`: Database error

**Example**:
```bash
curl http://localhost:8000/api/v1/documents
```

---

## Data Models

### Chronology Event

```typescript
interface ChronologyEvent {
  date: string;                      // ISO date format (YYYY-MM-DD)
  provider: string;                  // Provider/facility name
  encounter_type: string;            // Type of medical encounter
  summary: string;                   // Event description
  diagnosis_codes: string[];         // ICD-10 codes
  source_refs: SourceReference[];   // Verification links to PDF
}
```

### Bill Line Item

```typescript
interface BillLineItem {
  date_of_service: string;          // ISO date format
  cpt_code: string;                 // CPT procedure code
  description: string;              // Service description
  charged_amount: number;           // Amount charged
  allowed_amount: number;           // Insurance allowed amount
  source_refs: SourceReference[];   // Verification links to PDF
}
```

### Source Reference

Links extracted data back to the source PDF location.

```typescript
interface SourceReference {
  field: string;                    // Field name (e.g., "date", "provider")
  page_number: number;              // PDF page number (1-indexed)
  bounding_box: {
    left: number;                   // Normalized 0-1
    top: number;                    // Normalized 0-1
    width: number;                  // Normalized 0-1
    height: number;                 // Normalized 0-1
  };
  confidence: number;               // Match confidence (0-1)
  matched_text: string;             // Actual text found in OCR
  strategy?: string;                // Matching strategy used
}
```

**Bounding Box Coordinates**:
- All coordinates are normalized to 0-1 range
- `left`: Distance from left edge (0 = left, 1 = right)
- `top`: Distance from top edge (0 = top, 1 = bottom)
- `width`: Width of box (proportion of page width)
- `height`: Height of box (proportion of page height)

**To convert to pixel coordinates**:
```javascript
const pixelX = boundingBox.left * pageWidth;
const pixelY = boundingBox.top * pageHeight;
const pixelWidth = boundingBox.width * pageWidth;
const pixelHeight = boundingBox.height * pageHeight;
```

---

## Error Handling

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| 400 | Bad Request | Invalid file type, missing parameters |
| 404 | Not Found | Document ID doesn't exist |
| 413 | Payload Too Large | File exceeds size limit (50MB) |
| 500 | Internal Server Error | Database error, file system error |
| 503 | Service Unavailable | Database connection failed |

### Error Response Examples

**Invalid File Type**:
```json
{
  "detail": "Invalid file type: image/png. Only PDF files are accepted."
}
```

**Document Not Found**:
```json
{
  "detail": "Document not found"
}
```

**File Too Large**:
```json
{
  "detail": "File too large. Maximum size is 50MB"
}
```

---

## Rate Limiting

**Current Version**: No rate limiting (MVP)

**Future**: Will implement rate limiting:
- 100 requests per minute per IP
- 20 uploads per hour per IP
- Custom limits for authenticated users

---

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Browse all endpoints
- View request/response schemas
- Test API calls directly from the browser
- Download OpenAPI specification

---

## Webhooks (Future Feature)

**Not Yet Implemented**

Future versions will support webhooks for async notifications:

```json
POST https://your-server.com/webhook
{
  "event": "document.completed",
  "document_id": 1,
  "status": "COMPLETED",
  "timestamp": "2024-02-09T12:01:30Z"
}
```

---

## Need Help?

- **Issues**: File a bug report or feature request
- **Documentation**: See CONTRIBUTING.md for development setup
- **Questions**: Contact the development team

**API Version**: 1.0.0  
**Last Updated**: February 2024
