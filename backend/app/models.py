from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, JSON
from datetime import datetime
import enum
from app.database import Base

class DocumentStatus(enum.Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class DocumentType(enum.Enum):
    CHRONOLOGY = "CHRONOLOGY"
    BILL = "BILL"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.QUEUED, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    file_path = Column(String, nullable=True)  # Store the path to the uploaded file
    ocr_result = Column(String, nullable=True)  # Store OCR result JSON as text
    document_type = Column(SQLEnum(DocumentType), nullable=True)  # CHRONOLOGY or BILL
    extraction_result = Column(JSON, nullable=True)  # Structured extraction data (chronology or bill)
