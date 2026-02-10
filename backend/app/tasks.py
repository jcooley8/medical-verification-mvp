import json
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Document, DocumentStatus, DocumentType
from app.ocr_service import MockOCRService
from app.llm_service import MockLLMService
from app.verification_service import link_verification
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.process_document")
def process_document(document_id: int):
    """
    Process a document through the full pipeline:
    1. OCR extraction
    2. Document classification (CHRONOLOGY or BILL)
    3. Structured data extraction
    
    Args:
        document_id: ID of the document to process
    """
    db = SessionLocal()
    try:
        # Fetch the document
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            logger.error(f"Document {document_id} not found")
            return {"status": "error", "message": "Document not found"}
        
        logger.info(f"Processing document {document_id}: {document.filename}")
        
        # Update status to PROCESSING
        document.status = DocumentStatus.PROCESSING
        db.commit()
        
        # Step 1: Run Mock OCR
        ocr_service = MockOCRService()
        logger.info(f"Step 1/3: Running Mock OCR on {document.file_path}...")
        ocr_result = ocr_service.process_document(document.file_path)
        
        logger.info(f"Mock OCR completed for document {document_id}")
        
        # Store OCR result
        document.ocr_result = json.dumps(ocr_result)
        db.commit()
        
        # Extract text from OCR result for LLM processing
        # Concatenate all word text from all pages
        ocr_text = ""
        for page in ocr_result.get("pages", []):
            words = page.get("words", [])
            page_text = " ".join([word["text"] for word in words])
            ocr_text += page_text + "\n"
        
        logger.info(f"Extracted {len(ocr_text)} characters of text from OCR")
        
        # Step 2: Classify document type
        llm_service = MockLLMService()
        logger.info(f"Step 2/3: Classifying document type...")
        
        doc_type_str = llm_service.classify_document(ocr_text)
        document.document_type = DocumentType[doc_type_str]
        db.commit()
        
        logger.info(f"Document {document_id} classified as: {doc_type_str}")
        
        # Step 3: Extract structured data based on document type
        logger.info(f"Step 3/4: Extracting structured data for {doc_type_str}...")
        
        if document.document_type == DocumentType.CHRONOLOGY:
            extraction_result = llm_service.extract_chronology(ocr_text)
        elif document.document_type == DocumentType.BILL:
            extraction_result = llm_service.extract_bill(ocr_text)
        else:
            raise ValueError(f"Unknown document type: {document.document_type}")
        
        logger.info(f"Extracted data for document {document_id}")
        
        # Step 4: Verification Linkage - attach source_refs
        logger.info(f"Step 4/4: Linking extracted data to source locations...")
        
        enriched_result = link_verification(
            extracted_json=extraction_result,
            ocr_map=ocr_result,
            file_id=str(document.id)
        )
        
        logger.info(f"Verification linkage completed: {enriched_result.get('_match_summary', {})}")
        
        # Store enriched extraction result and mark as COMPLETED
        document.extraction_result = enriched_result
        document.status = DocumentStatus.COMPLETED
        db.commit()
        
        logger.info(f"Document {document_id} processing completed successfully")
        
        return {
            "status": "success",
            "document_id": document_id,
            "filename": document.filename,
            "document_type": doc_type_str,
            "words_extracted": len(ocr_result.get("pages", [{}])[0].get("words", [])),
            "extraction_summary": {
                "chronology_events": len(enriched_result.get("events", [])) if doc_type_str == "CHRONOLOGY" else None,
                "bill_line_items": len(enriched_result.get("line_items", [])) if doc_type_str == "BILL" else None
            },
            "verification_summary": enriched_result.get("_match_summary", {})
        }
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        
        # Update status to FAILED
        if document:
            document.status = DocumentStatus.FAILED
            db.commit()
        
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()
