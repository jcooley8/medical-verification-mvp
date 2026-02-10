from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path

from app.schemas import MedicalChronology, MedicalBill
from app.database import get_db, engine, Base
from app.models import Document, DocumentStatus
from app.tasks import process_document

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Medical Verification MVP")

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
UPLOAD_DIR = Path("/code/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
def read_root():
    return {"status": "healthy", "service": "medical-verification-mvp"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint that verifies database connectivity"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {
            "status": "ok",
            "database": "connected",
            "service": "medical-verification-mvp"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "disconnected",
            "error": str(e)
        }

@app.post("/api/v1/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF document for processing.
    
    - Validates file type (must be PDF)
    - Saves file to uploads/ directory
    - Creates database record with QUEUED status
    - Triggers Celery task for processing
    """
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only PDF files are accepted."
        )
    
    # Generate safe filename
    filename = file.filename
    file_path = UPLOAD_DIR / filename
    
    # Handle duplicate filenames
    counter = 1
    while file_path.exists():
        name_parts = filename.rsplit(".", 1)
        if len(name_parts) == 2:
            file_path = UPLOAD_DIR / f"{name_parts[0]}_{counter}.{name_parts[1]}"
        else:
            file_path = UPLOAD_DIR / f"{filename}_{counter}"
        counter += 1
    
    # Save file to disk
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Create database record
    document = Document(
        filename=filename,
        status=DocumentStatus.QUEUED,
        file_path=str(file_path)
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Trigger Celery task
    process_document.delay(document.id)
    
    return {
        "message": "Document uploaded successfully",
        "document_id": document.id,
        "filename": document.filename,
        "status": document.status.value,
        "created_at": document.created_at.isoformat()
    }

@app.get("/api/v1/documents/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Get document status and details.
    
    Returns:
        - Basic document metadata
        - Processing status
        - Document type (CHRONOLOGY or BILL) when classified
        - Extraction result (structured JSON) when completed
        - OCR result (raw) for debugging
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    response = {
        "document_id": document.id,
        "filename": document.filename,
        "status": document.status.value,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat(),
        "document_type": document.document_type.value if document.document_type else None,
        "extraction_result": document.extraction_result,
        "ocr_result": document.ocr_result
    }
    
    return response

@app.get("/api/v1/documents")
def list_documents(db: Session = Depends(get_db)):
    """
    List all documents.
    """
    documents = db.query(Document).order_by(Document.created_at.desc()).all()
    
    return {
        "count": len(documents),
        "documents": [
            {
                "document_id": doc.id,
                "filename": doc.filename,
                "status": doc.status.value,
                "document_type": doc.document_type.value if doc.document_type else None,
                "created_at": doc.created_at.isoformat()
            }
            for doc in documents
        ]
    }

# Placeholder endpoints to demonstrate schema usage
@app.post("/chronology/mock", response_model=MedicalChronology)
def create_mock_chronology(data: MedicalChronology):
    return data

@app.post("/bill/mock", response_model=MedicalBill)
def create_mock_bill(data: MedicalBill):
    return data
