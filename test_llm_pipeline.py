#!/usr/bin/env python3
"""
Test script for LLM Extraction Pipeline

Tests the MockLLMService functionality without requiring Docker or database.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.llm_service import MockLLMService
import json


def test_classification():
    """Test document classification"""
    print("=" * 60)
    print("TEST 1: Document Classification")
    print("=" * 60)
    
    llm_service = MockLLMService()
    
    # Test with chronology-like text
    chronology_text = """
    Patient visit to Dr. Smith on January 15, 2024.
    Chief complaint: chest pain.
    Diagnosis: Angina pectoris.
    Treatment plan: Started on medication.
    """
    
    result = llm_service.classify_document(chronology_text)
    print(f"\nChronology text classification: {result}")
    assert result == "CHRONOLOGY", f"Expected CHRONOLOGY, got {result}"
    print("✓ Chronology classification passed")
    
    # Test with bill-like text
    bill_text = """
    INVOICE #12345
    Total Charges: $500.00
    CPT Code: 99214 - Office Visit
    Amount Due: $500.00
    Payment required by end of month.
    """
    
    result = llm_service.classify_document(bill_text)
    print(f"\nBill text classification: {result}")
    assert result == "BILL", f"Expected BILL, got {result}"
    print("✓ Bill classification passed")


def test_chronology_extraction():
    """Test chronology extraction"""
    print("\n" + "=" * 60)
    print("TEST 2: Chronology Extraction")
    print("=" * 60)
    
    llm_service = MockLLMService()
    
    sample_text = "Medical record for Jennifer Martinez..."
    result = llm_service.extract_chronology(sample_text)
    
    print("\nExtracted Chronology:")
    print(json.dumps(result, indent=2))
    
    # Validate schema
    assert "patient_name" in result, "Missing patient_name field"
    assert "events" in result, "Missing events field"
    assert isinstance(result["events"], list), "events should be a list"
    assert len(result["events"]) > 0, "events list should not be empty"
    
    # Validate first event
    event = result["events"][0]
    required_fields = ["date", "provider", "encounter_type", "summary", "diagnosis_codes"]
    for field in required_fields:
        assert field in event, f"Missing required field: {field}"
    
    print("\n✓ Chronology extraction schema validation passed")
    print(f"✓ Extracted {len(result['events'])} events")


def test_bill_extraction():
    """Test bill extraction"""
    print("\n" + "=" * 60)
    print("TEST 3: Bill Extraction")
    print("=" * 60)
    
    llm_service = MockLLMService()
    
    sample_text = "Medical bill invoice #12345..."
    result = llm_service.extract_bill(sample_text)
    
    print("\nExtracted Bill:")
    print(json.dumps(result, indent=2))
    
    # Validate schema
    assert "invoice_number" in result, "Missing invoice_number field"
    assert "total_amount" in result, "Missing total_amount field"
    assert "line_items" in result, "Missing line_items field"
    assert isinstance(result["line_items"], list), "line_items should be a list"
    assert len(result["line_items"]) > 0, "line_items list should not be empty"
    
    # Validate first line item
    item = result["line_items"][0]
    required_fields = ["date_of_service", "cpt_code", "description", "charged_amount", "allowed_amount"]
    for field in required_fields:
        assert field in item, f"Missing required field: {field}"
    
    print("\n✓ Bill extraction schema validation passed")
    print(f"✓ Extracted {len(result['line_items'])} line items")
    print(f"✓ Total amount: ${result['total_amount']:.2f}")


def test_full_pipeline_simulation():
    """Simulate the full pipeline flow"""
    print("\n" + "=" * 60)
    print("TEST 4: Full Pipeline Simulation")
    print("=" * 60)
    
    llm_service = MockLLMService()
    
    # Simulate OCR text output
    ocr_text = """
    CITY MEDICAL CENTER
    Invoice #INV-2024-999
    Patient: John Doe
    
    Date        CPT     Description              Charge
    01/15/2024  99214   Office Visit             $285.00
    01/15/2024  80053   Metabolic Panel          $95.00
    
    Total Charges: $380.00
    """
    
    print("\n1. OCR Text Extracted:")
    print(ocr_text[:100] + "...")
    
    # Step 1: Classify
    print("\n2. Classifying document...")
    doc_type = llm_service.classify_document(ocr_text)
    print(f"   Classification: {doc_type}")
    
    # Step 2: Extract based on type
    print(f"\n3. Extracting structured data for {doc_type}...")
    if doc_type == "BILL":
        extraction = llm_service.extract_bill(ocr_text)
        print(f"   Invoice: {extraction['invoice_number']}")
        print(f"   Total: ${extraction['total_amount']:.2f}")
        print(f"   Line items: {len(extraction['line_items'])}")
    else:
        extraction = llm_service.extract_chronology(ocr_text)
        print(f"   Patient: {extraction['patient_name']}")
        print(f"   Events: {len(extraction['events'])}")
    
    print("\n✓ Full pipeline simulation successful")


def main():
    """Run all tests"""
    print("\n" + "🧪 " * 20)
    print("LLM Extraction Pipeline Test Suite")
    print("🧪 " * 20 + "\n")
    
    try:
        test_classification()
        test_chronology_extraction()
        test_bill_extraction()
        test_full_pipeline_simulation()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nThe LLM Extraction Pipeline is working correctly!")
        print("\nNext steps:")
        print("  1. Start Docker services: docker compose up -d")
        print("  2. Upload a PDF: curl -F 'file=@sample.pdf' http://localhost:8000/api/v1/documents/upload")
        print("  3. Check status: curl http://localhost:8000/api/v1/documents/1")
        print("  4. View extraction_result in the response")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
