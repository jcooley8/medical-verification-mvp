"""
LLM Service for document classification and extraction.

Currently uses MockLLMService for testing without API keys.
Can be replaced with real Claude API integration later.
"""
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MockLLMService:
    """
    Mock LLM service that returns hardcoded JSON responses.
    Used for testing the pipeline without requiring actual LLM API calls.
    """
    
    def classify_document(self, ocr_text: str) -> str:
        """
        Classify document type based on OCR text.
        
        Args:
            ocr_text: The OCR extracted text from the document
            
        Returns:
            str: Either "CHRONOLOGY" or "BILL"
        """
        logger.info("MockLLMService: Classifying document...")
        
        # Simple heuristic: look for billing-related keywords
        text_lower = ocr_text.lower()
        
        billing_keywords = [
            "invoice", "bill", "charged", "cpt", "payment",
            "total charges", "amount due", "claim"
        ]
        
        chronology_keywords = [
            "visit", "consultation", "diagnosis", "treatment",
            "history", "exam", "patient"
        ]
        
        billing_score = sum(1 for kw in billing_keywords if kw in text_lower)
        chronology_score = sum(1 for kw in chronology_keywords if kw in text_lower)
        
        if billing_score > chronology_score:
            logger.info("MockLLMService: Classified as BILL")
            return "BILL"
        else:
            logger.info("MockLLMService: Classified as CHRONOLOGY")
            return "CHRONOLOGY"
    
    def extract_chronology(self, ocr_text: str) -> Dict[str, Any]:
        """
        Extract structured chronology data from medical record.
        
        Args:
            ocr_text: The OCR extracted text from the document
            
        Returns:
            dict: Chronology data matching the schema from PROMPTS.md
        """
        logger.info("MockLLMService: Extracting chronology data...")
        
        # Return hardcoded mock chronology data
        mock_chronology = {
            "patient_name": "Jennifer Martinez",
            "events": [
                {
                    "date": "2024-02-14",
                    "provider": "Memorial Regional Hospital",
                    "encounter_type": "Emergency Visit",
                    "summary": "Patient presented with severe right lower quadrant abdominal pain, nausea, and vomiting. CT scan confirmed acute appendicitis with early perforation.",
                    "diagnosis_codes": ["K35.20"]
                },
                {
                    "date": "2024-02-15",
                    "provider": "Dr. William Chen / Memorial Regional Hospital",
                    "encounter_type": "Surgery/Procedure",
                    "summary": "Laparoscopic appendectomy performed for acute appendicitis. Inflamed appendix with early perforation successfully removed. Patient tolerated procedure well.",
                    "diagnosis_codes": ["K35.30"]
                }
            ]
        }
        
        logger.info(f"MockLLMService: Extracted {len(mock_chronology['events'])} events")
        return mock_chronology
    
    def extract_bill(self, ocr_text: str) -> Dict[str, Any]:
        """
        Extract structured billing data from medical bill.
        
        Args:
            ocr_text: The OCR extracted text from the document
            
        Returns:
            dict: Bill data matching the schema from PROMPTS.md
        """
        logger.info("MockLLMService: Extracting bill data...")
        
        # Return hardcoded mock bill data
        mock_bill = {
            "invoice_number": "INV-2024-0891",
            "total_amount": 685.00,
            "line_items": [
                {
                    "date_of_service": "2024-02-20",
                    "cpt_code": "99214",
                    "description": "Office Visit, Established Pt, L4",
                    "charged_amount": 285.00,
                    "allowed_amount": 210.00
                },
                {
                    "date_of_service": "2024-02-20",
                    "cpt_code": "80053",
                    "description": "Comprehensive Metabolic Panel",
                    "charged_amount": 95.00,
                    "allowed_amount": 68.00
                },
                {
                    "date_of_service": "2024-02-20",
                    "cpt_code": "36415",
                    "description": "Venipuncture (Blood Draw)",
                    "charged_amount": 15.00,
                    "allowed_amount": 8.00
                },
                {
                    "date_of_service": "2024-02-27",
                    "cpt_code": "93000",
                    "description": "Electrocardiogram (EKG)",
                    "charged_amount": 125.00,
                    "allowed_amount": 89.00
                },
                {
                    "date_of_service": "2024-02-27",
                    "cpt_code": "99213",
                    "description": "Office Visit, Established Pt, L3",
                    "charged_amount": 165.00,
                    "allowed_amount": 120.00
                }
            ]
        }
        
        logger.info(f"MockLLMService: Extracted {len(mock_bill['line_items'])} line items")
        return mock_bill


# Future: Real Claude API implementation
class ClaudeAPIService:
    """
    Real Claude API integration (to be implemented).
    
    Usage:
        from anthropic import Anthropic
        
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=CHRONOLOGY_PROMPT,
            messages=[{"role": "user", "content": ocr_text}]
        )
    """
    pass
