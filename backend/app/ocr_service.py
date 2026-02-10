import time
import json
from typing import Dict, Any

class MockOCRService:
    """
    Mock OCR service that simulates AWS Textract without requiring actual AWS credentials.
    Returns dummy OCR output with bounding boxes to test the async worker infrastructure.
    """
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Simulates OCR processing with a delay.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Mock OCR result with words and bounding boxes
        """
        # Simulate processing time
        time.sleep(2)
        
        # Return mock OCR data with realistic structure
        mock_result = {
            "status": "SUCCESS",
            "pages": [
                {
                    "page_number": 1,
                    "width": 612,
                    "height": 792,
                    "words": [
                        {
                            "text": "Medical",
                            "confidence": 0.99,
                            "bounding_box": {"left": 50, "top": 50, "width": 80, "height": 20}
                        },
                        {
                            "text": "Record",
                            "confidence": 0.98,
                            "bounding_box": {"left": 135, "top": 50, "width": 70, "height": 20}
                        },
                        {
                            "text": "Patient:",
                            "confidence": 0.99,
                            "bounding_box": {"left": 50, "top": 100, "width": 60, "height": 18}
                        },
                        {
                            "text": "John",
                            "confidence": 0.97,
                            "bounding_box": {"left": 115, "top": 100, "width": 40, "height": 18}
                        },
                        {
                            "text": "Doe",
                            "confidence": 0.98,
                            "bounding_box": {"left": 160, "top": 100, "width": 35, "height": 18}
                        },
                        {
                            "text": "Date:",
                            "confidence": 0.99,
                            "bounding_box": {"left": 50, "top": 130, "width": 45, "height": 18}
                        },
                        {
                            "text": "2024-01-15",
                            "confidence": 0.96,
                            "bounding_box": {"left": 100, "top": 130, "width": 90, "height": 18}
                        },
                        {
                            "text": "Diagnosis:",
                            "confidence": 0.98,
                            "bounding_box": {"left": 50, "top": 160, "width": 80, "height": 18}
                        },
                        {
                            "text": "M54.5",
                            "confidence": 0.95,
                            "bounding_box": {"left": 135, "top": 160, "width": 55, "height": 18}
                        },
                        {
                            "text": "Low",
                            "confidence": 0.99,
                            "bounding_box": {"left": 195, "top": 160, "width": 35, "height": 18}
                        },
                        {
                            "text": "back",
                            "confidence": 0.99,
                            "bounding_box": {"left": 235, "top": 160, "width": 40, "height": 18}
                        },
                        {
                            "text": "pain",
                            "confidence": 0.98,
                            "bounding_box": {"left": 280, "top": 160, "width": 35, "height": 18}
                        }
                    ]
                }
            ],
            "processed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "file_path": file_path
        }
        
        return mock_result
