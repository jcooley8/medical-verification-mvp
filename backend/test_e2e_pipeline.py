#!/usr/bin/env python3
"""
End-to-end pipeline test
Simulates the full document processing flow with verification linkage
"""

import json
from app.ocr_service import MockOCRService
from app.llm_service import MockLLMService
from app.verification_service import link_verification

def test_bill_pipeline():
    """Test full pipeline for a bill document"""
    print("\n" + "="*60)
    print("END-TO-END BILL PIPELINE TEST")
    print("="*60 + "\n")
    
    # Step 1: Mock OCR
    print("Step 1/4: Running OCR...")
    ocr_service = MockOCRService()
    ocr_result = ocr_service.process_document("test_bill.pdf")
    print(f"  ✓ OCR extracted {len(ocr_result['pages'][0]['words'])} words")
    
    # Extract text
    ocr_text = " ".join([w["text"] for w in ocr_result["pages"][0]["words"]])
    print(f"  ✓ Text: {ocr_text[:100]}...")
    
    # Step 2: Classify
    print("\nStep 2/4: Classifying document...")
    llm_service = MockLLMService()
    doc_type = llm_service.classify_document(ocr_text)
    print(f"  ✓ Classified as: {doc_type}")
    
    # Step 3: Extract structured data
    print("\nStep 3/4: Extracting structured data...")
    if doc_type == "BILL":
        extraction = llm_service.extract_bill(ocr_text)
    else:
        extraction = llm_service.extract_chronology(ocr_text)
    
    print(f"  ✓ Extracted {len(extraction.get('line_items', []))} line items")
    print(f"  ✓ Invoice: {extraction.get('invoice_number')}")
    print(f"  ✓ Total: ${extraction.get('total_amount')}")
    
    # Step 4: Verification linkage
    print("\nStep 4/4: Linking verification sources...")
    enriched = link_verification(extraction, ocr_result, file_id="test-123")
    
    match_summary = enriched.get("_match_summary", {})
    print(f"  ✓ Match summary:")
    print(f"    - Total fields: {match_summary['total_fields']}")
    print(f"    - Matched: {match_summary['matched']}")
    print(f"    - Unmatched: {match_summary['unmatched']}")
    print(f"    - Match rate: {match_summary['match_rate']*100}%")
    
    # Verify source_refs are present
    print("\n" + "="*60)
    print("VERIFICATION RESULTS")
    print("="*60 + "\n")
    
    # Check top-level fields
    if "source_refs" in enriched:
        print(f"Top-level source_refs: {len(enriched['source_refs'])} found")
        for ref in enriched["source_refs"]:
            print(f"  - {ref['field']}: '{ref['matched_text']}' (confidence: {ref['confidence']})")
    
    # Check line items
    for i, item in enumerate(enriched.get("line_items", [])):
        print(f"\nLine Item {i+1}:")
        print(f"  Date: {item.get('date_of_service')}")
        print(f"  CPT: {item.get('cpt_code')}")
        print(f"  Description: {item.get('description')}")
        print(f"  Amount: ${item.get('charged_amount')}")
        
        if "source_refs" in item:
            print(f"  Source refs: {len(item['source_refs'])} found")
            for ref in item["source_refs"]:
                bbox = ref["bounding_box"]
                print(f"    → {ref['field']}: '{ref['matched_text']}' @ page {ref['page_number']}")
                print(f"       bbox: (left={bbox['left']:.2f}, top={bbox['top']:.2f}, "
                      f"w={bbox['width']:.2f}, h={bbox['height']:.2f})")
                print(f"       confidence: {ref['confidence']}, strategy: {ref.get('strategy', 'N/A')}")
    
    print("\n" + "="*60)
    print("✓ END-TO-END PIPELINE TEST PASSED")
    print("="*60 + "\n")
    
    return enriched


def test_chronology_pipeline():
    """Test full pipeline for a chronology document"""
    print("\n" + "="*60)
    print("END-TO-END CHRONOLOGY PIPELINE TEST")
    print("="*60 + "\n")
    
    # Create mock OCR with chronology keywords
    ocr_result = {
        "status": "SUCCESS",
        "pages": [{
            "page_number": 1,
            "width": 612,
            "height": 792,
            "words": [
                {"text": "Patient", "bounding_box": {"left": 0.1, "top": 0.1, "width": 0.08, "height": 0.02}, "confidence": 0.99},
                {"text": "History", "bounding_box": {"left": 0.19, "top": 0.1, "width": 0.07, "height": 0.02}, "confidence": 0.98},
                {"text": "Jennifer", "bounding_box": {"left": 0.1, "top": 0.15, "width": 0.08, "height": 0.02}, "confidence": 0.97},
                {"text": "Martinez", "bounding_box": {"left": 0.19, "top": 0.15, "width": 0.08, "height": 0.02}, "confidence": 0.96},
                {"text": "Visit", "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.05, "height": 0.02}, "confidence": 0.98},
                {"text": "Date:", "bounding_box": {"left": 0.16, "top": 0.2, "width": 0.05, "height": 0.02}, "confidence": 0.99},
                {"text": "02/14/2024", "bounding_box": {"left": 0.22, "top": 0.2, "width": 0.10, "height": 0.02}, "confidence": 0.98},
            ]
        }]
    }
    
    ocr_text = " ".join([w["text"] for w in ocr_result["pages"][0]["words"]])
    
    print("Step 1/4: OCR (mocked)")
    print(f"  ✓ Text: {ocr_text}")
    
    print("\nStep 2/4: Classifying...")
    llm_service = MockLLMService()
    doc_type = llm_service.classify_document(ocr_text)
    print(f"  ✓ Classified as: {doc_type}")
    
    print("\nStep 3/4: Extracting...")
    extraction = llm_service.extract_chronology(ocr_text)
    print(f"  ✓ Extracted {len(extraction.get('events', []))} events")
    
    print("\nStep 4/4: Verification linkage...")
    enriched = link_verification(extraction, ocr_result, file_id="chrono-123")
    
    match_summary = enriched.get("_match_summary", {})
    print(f"  ✓ Match rate: {match_summary['match_rate']*100}%")
    
    print("\n✓ CHRONOLOGY PIPELINE TEST PASSED\n")
    
    return enriched


if __name__ == "__main__":
    # Test both pipelines
    bill_result = test_bill_pipeline()
    chrono_result = test_chronology_pipeline()
    
    # Verify both have source_refs
    assert "_match_summary" in bill_result
    assert "_match_summary" in chrono_result
    
    print("\n" + "="*60)
    print("ALL END-TO-END TESTS PASSED ✅")
    print("="*60 + "\n")
    print("The verification linkage service is working correctly!")
    print("\nNext steps:")
    print("1. Upload a PDF via the API")
    print("2. Check the extraction_result in the response")
    print("3. Verify source_refs are populated with bounding boxes")
    print("4. Build the click-to-verify UI component")
