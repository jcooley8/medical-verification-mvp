from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import shutil
import logging
from pathlib import Path

from app.schemas import MedicalChronology, MedicalBill
from app.database import get_db, engine, Base
from app.models import Document, DocumentStatus
from app.tasks import process_document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)
logger.info("Database tables created/verified")

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
# Support both Railway (/code) and local development
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/code/uploads"))
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
logger.info(f"Upload directory configured: {UPLOAD_DIR}")

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
    - Validates file size (max 50MB)
    - Saves file to uploads/ directory
    - Creates database record with QUEUED status
    - Triggers Celery task for processing
    """
    logger.info(f"Upload request received: {file.filename} ({file.content_type})")
    
    # Validate file exists
    if not file.filename:
        logger.warning("Upload rejected: No filename provided")
        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )
    
    # Validate file type
    if file.content_type != "application/pdf":
        logger.warning(f"Upload rejected: Invalid file type {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only PDF files are accepted."
        )
    
    # Validate file size (max 50MB)
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "50")) * 1024 * 1024
    file_size = 0
    chunks = []
    
    try:
        # Read file in chunks to check size
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                logger.warning(f"Upload rejected: File too large ({file_size} bytes)")
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
                )
            chunks.append(chunk)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading uploaded file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reading file: {str(e)}"
        )
    
    logger.info(f"File validated: {file.filename} ({file_size} bytes)")
    
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
            for chunk in chunks:
                buffer.write(chunk)
        logger.info(f"File saved: {file_path}")
    except Exception as e:
        logger.error(f"Failed to save file {file_path}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Create database record
    try:
        document = Document(
            filename=filename,
            status=DocumentStatus.QUEUED,
            file_path=str(file_path)
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        logger.info(f"Database record created: document_id={document.id}")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        # Clean up file if database fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    
    # Trigger Celery task
    try:
        process_document.delay(document.id)
        logger.info(f"Processing task queued for document_id={document.id}")
    except Exception as e:
        logger.error(f"Failed to queue processing task: {str(e)}")
        # Document is still in database with QUEUED status
        # Can be retried manually
    
    return {
        "message": "Document uploaded successfully",
        "document_id": document.id,
        "filename": document.filename,
        "status": document.status.value,
        "created_at": document.created_at.isoformat(),
        "file_size_bytes": file_size
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
        
    Raises:
        404: Document not found
        500: Database error
    """
    logger.info(f"Fetching document: document_id={document_id}")
    
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            logger.warning(f"Document not found: document_id={document_id}")
            raise HTTPException(status_code=404, detail="Document not found")
        
        response = {
            "document_id": document.id,
            "filename": document.filename,
            "status": document.status.value,
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat(),
            "document_type": document.document_type.value if document.document_type else None,
            "extraction_result": document.extraction_result,
            "ocr_result": document.ocr_result,
            "file_path": document.file_path  # Useful for debugging
        }
        
        logger.info(f"Document retrieved successfully: document_id={document_id}, status={document.status.value}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

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
