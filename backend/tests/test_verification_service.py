"""
Test suite for verification linkage service.

Tests all 5 matching strategies:
1. Exact code match
2. Amount with currency symbol
3. Date format mismatch
4. Fuzzy provider name match (OCR error)
5. Multi-word description span
"""

import pytest
from app.verification_service import VerificationLinker, link_verification


class TestVerificationLinkage:
    """Test cases matching VERIFICATION_ALGO.md specifications"""
    
    def setup_method(self):
        """Setup for each test"""
        self.linker = VerificationLinker()
    
    def test_case_1_exact_code_match(self):
        """
        Test Case 1: Exact CPT Code Match
        
        Extracted: {"cpt_code": "99214"}
        OCR: {"text": "99214", "bbox": {...}, "confidence": 0.99}
        Expected: confidence = 1.0 (0.99 + 0.05 boost, capped at 1.0)
        """
        extracted = {
            "line_items": [
                {"cpt_code": "99214"}
            ]
        }
        
        ocr_map = {
            "pages": [
                {
                    "page_number": 1,
                    "width": 612,
                    "height": 792,
                    "words": [
                        {
                            "text": "99214",
                            "bounding_box": {"left": 0.15, "top": 0.20, "width": 0.06, "height": 0.02},
                            "confidence": 0.99
                        }
                    ]
                }
            ]
        }
        
        result = link_verification(extracted, ocr_map, file_id="test-file-1")
        
        # Verify structure
        assert "line_items" in result
        assert len(result["line_items"]) == 1
        assert "source_refs" in result["line_items"][0]
        
        # Verify source_ref
        refs = result["line_items"][0]["source_refs"]
        assert len(refs) > 0
        
        cpt_ref = next((r for r in refs if r["field"] == "code"), None)
        assert cpt_ref is not None
        assert cpt_ref["page_number"] == 1
        assert cpt_ref["matched_text"] == "99214"
        assert cpt_ref["confidence"] >= 0.99  # Should be capped at 1.0
        assert cpt_ref["strategy"] == "exact"
        
        print(f"✓ Test Case 1 passed: {cpt_ref}")
    
    def test_case_2_amount_with_currency(self):
        """
        Test Case 2: Amount with Currency Symbol
        
        Extracted: {"charged_amount": 250.00}
        OCR: {"text": "$250.00", "bbox": {...}, "confidence": 0.97}
        Expected: confidence = 1.0 (0.97 + 0.03 exact amount match)
        """
        extracted = {
            "line_items": [
                {"charged_amount": 250.00}
            ]
        }
        
        ocr_map = {
            "pages": [
                {
                    "page_number": 1,
                    "width": 612,
                    "height": 792,
                    "words": [
                        {
                            "text": "$250.00",
                            "bounding_box": {"left": 0.70, "top": 0.25, "width": 0.08, "height": 0.02},
                            "confidence": 0.97
                        }
                    ]
                }
            ]
        }
        
        result = link_verification(extracted, ocr_map, file_id="test-file-2")
        
        # Verify source_ref
        refs = result["line_items"][0]["source_refs"]
        amount_ref = next((r for r in refs if r["field"] == "amount"), None)
        
        assert amount_ref is not None
        assert amount_ref["matched_text"] == "$250.00"
        assert amount_ref["confidence"] >= 0.99
        assert amount_ref["strategy"] == "amount"
        
        print(f"✓ Test Case 2 passed: {amount_ref}")
    
    def test_case_3_date_format_mismatch(self):
        """
        Test Case 3: Date Format Mismatch
        
        Extracted: {"date_of_service": "2024-01-15"}
        OCR: {"text": "01/15/2024", "bbox": {...}, "confidence": 0.98}
        Expected: confidence = 1.0 (0.98 + 0.02 date normalization)
        """
        extracted = {
            "line_items": [
                {"date_of_service": "2024-01-15"}
            ]
        }
        
        ocr_map = {
            "pages": [
                {
                    "page_number": 1,
                    "width": 612,
                    "height": 792,
                    "words": [
                        {
                            "text": "01/15/2024",
                            "bounding_box": {"left": 0.16, "top": 0.15, "width": 0.10, "height": 0.02},
                            "confidence": 0.98
                        }
                    ]
                }
            ]
        }
        
        result = link_verification(extracted, ocr_map, file_id="test-file-3")
        
        # Verify source_ref
        refs = result["line_items"][0]["source_refs"]
        date_ref = next((r for r in refs if r["field"] == "date"), None)
        
        assert date_ref is not None
        assert date_ref["matched_text"] == "01/15/2024"
        assert date_ref["confidence"] >= 0.98
        assert date_ref["strategy"] == "date"
        
        print(f"✓ Test Case 3 passed: {date_ref}")
    
    def test_case_4_fuzzy_provider_match(self):
        """
        Test Case 4: Fuzzy Provider Name Match (OCR Error)
        
        Extracted: {"provider": "Dr. Smith"}
        OCR: {"text": "Dr. Smlth", "bbox": {...}, "confidence": 0.92}
        Fuzzy Ratio: 92% (above 85% threshold)
        Expected: confidence ≈ 0.88 (0.92 - 0.04 penalty)
        """
        extracted = {
            "events": [
                {"provider": "Dr. Smith"}
            ]
        }
        
        ocr_map = {
            "pages": [
                {
                    "page_number": 1,
                    "width": 612,
                    "height": 792,
                    "words": [
                        {
                            "text": "Dr. Smlth",
                            "bounding_box": {"left": 0.30, "top": 0.18, "width": 0.12, "height": 0.02},
                            "confidence": 0.92
                        }
                    ]
                }
            ]
        }
        
        result = link_verification(extracted, ocr_map, file_id="test-file-4")
        
        # Verify source_ref
        refs = result["events"][0]["source_refs"]
        provider_ref = next((r for r in refs if r["field"] == "provider"), None)
        
        assert provider_ref is not None
        assert provider_ref["matched_text"] == "Dr. Smlth"
        assert 0.85 <= provider_ref["confidence"] <= 0.95  # Should have small penalty
        assert provider_ref["strategy"] == "fuzzy"
        
        print(f"✓ Test Case 4 passed: {provider_ref}")
    
    def test_case_5_multiword_description(self):
        """
        Test Case 5: Multi-Word Description Span
        
        Extracted: {"description": "Office Visit, Level 4"}
        OCR: ["Office", "Visit,", "Level", "4"] (4 consecutive words)
        Expected: Union bbox, avg confidence ≈ 0.98
        """
        extracted = {
            "line_items": [
                {"description": "Office Visit, Level 4"}
            ]
        }
        
        ocr_map = {
            "pages": [
                {
                    "page_number": 1,
                    "width": 612,
                    "height": 792,
                    "words": [
                        {
                            "text": "Office",
                            "bounding_box": {"left": 0.20, "top": 0.25, "width": 0.06, "height": 0.02},
                            "confidence": 0.98
                        },
                        {
                            "text": "Visit,",
                            "bounding_box": {"left": 0.27, "top": 0.25, "width": 0.05, "height": 0.02},
                            "confidence": 0.97
                        },
                        {
                            "text": "Level",
                            "bounding_box": {"left": 0.33, "top": 0.25, "width": 0.05, "height": 0.02},
                            "confidence": 0.99
                        },
                        {
                            "text": "4",
                            "bounding_box": {"left": 0.39, "top": 0.25, "width": 0.02, "height": 0.02},
                            "confidence": 0.99
                        }
                    ]
                }
            ]
        }
        
        result = link_verification(extracted, ocr_map, file_id="test-file-5")
        
        # Verify source_ref
        refs = result["line_items"][0]["source_refs"]
        desc_refs = [r for r in refs if r["field"] == "description" and r["strategy"] == "multiword"]
        
        assert len(desc_refs) > 0, "No multiword matches found"
        
        # Find the best (most complete) match
        best_match = max(desc_refs, key=lambda r: len(r["matched_text"]))
        
        assert "Office" in best_match["matched_text"]
        assert "Level 4" in best_match["matched_text"] or "Level" in best_match["matched_text"]
        assert best_match["confidence"] >= 0.95
        assert best_match["strategy"] == "multiword"
        
        # Verify union bounding box
        bbox = best_match["bounding_box"]
        assert bbox["left"] == 0.20  # Min left
        assert bbox["width"] >= 0.20  # Should span multiple words
        
        print(f"✓ Test Case 5 passed: {best_match}")
    
    def test_no_match_found(self):
        """
        Test edge case: No match found (LLM inferred value)
        
        Expected: empty source_refs array
        """
        extracted = {
            "line_items": [
                {"description": "Completely Made Up Service"}
            ]
        }
        
        ocr_map = {
            "pages": [
                {
                    "page_number": 1,
                    "width": 612,
                    "height": 792,
                    "words": [
                        {
                            "text": "Different",
                            "bounding_box": {"left": 0.20, "top": 0.25, "width": 0.06, "height": 0.02},
                            "confidence": 0.98
                        },
                        {
                            "text": "Text",
                            "bounding_box": {"left": 0.27, "top": 0.25, "width": 0.05, "height": 0.02},
                            "confidence": 0.97
                        }
                    ]
                }
            ]
        }
        
        result = link_verification(extracted, ocr_map, file_id="test-file-6")
        
        # Should have empty source_refs
        refs = result["line_items"][0]["source_refs"]
        assert len(refs) == 0
        
        # Match summary should show unmatched
        assert result["_match_summary"]["unmatched"] >= 1
        
        print("✓ No match test passed")
    
    def test_multiple_occurrences(self):
        """
        Test edge case: Same value appears multiple times
        
        Expected: Return highest confidence match or multiple candidates
        """
        extracted = {
            "line_items": [
                {"charged_amount": 150.00}
            ]
        }
        
        ocr_map = {
            "pages": [
                {
                    "page_number": 1,
                    "width": 612,
                    "height": 792,
                    "words": [
                        {
                            "text": "$150.00",
                            "bounding_box": {"left": 0.50, "top": 0.25, "width": 0.08, "height": 0.02},
                            "confidence": 0.95
                        },
                        {
                            "text": "$150.00",
                            "bounding_box": {"left": 0.70, "top": 0.30, "width": 0.08, "height": 0.02},
                            "confidence": 0.98
                        },
                        {
                            "text": "$150.00",
                            "bounding_box": {"left": 0.80, "top": 0.80, "width": 0.08, "height": 0.02},
                            "confidence": 0.85
                        }
                    ]
                }
            ]
        }
        
        result = link_verification(extracted, ocr_map, file_id="test-file-7")
        
        # Should have at least one match
        refs = result["line_items"][0]["source_refs"]
        assert len(refs) >= 1
        
        # If multiple returned, should be ranked by confidence
        if len(refs) > 1:
            for i in range(len(refs) - 1):
                assert refs[i]["confidence"] >= refs[i + 1]["confidence"]
        
        print(f"✓ Multiple occurrences test passed: {len(refs)} candidates returned")
    
    def test_full_bill_integration(self):
        """
        Integration test: Complete bill with multiple fields
        """
        extracted = {
            "invoice_number": "INV-2024-0891",
            "total_amount": 685.00,
            "line_items": [
                {
                    "date_of_service": "2024-02-20",
                    "cpt_code": "99214",
                    "description": "Office Visit, Established Pt, L4",
                    "charged_amount": 285.00,
                    "allowed_amount": 210.00
                }
            ]
        }
        
        ocr_map = {
            "pages": [
                {
                    "page_number": 1,
                    "width": 612,
                    "height": 792,
                    "words": [
                        {"text": "INV-2024-0891", "bounding_box": {"left": 0.1, "top": 0.05, "width": 0.15, "height": 0.02}, "confidence": 0.99},
                        {"text": "$685.00", "bounding_box": {"left": 0.7, "top": 0.08, "width": 0.08, "height": 0.02}, "confidence": 0.98},
                        {"text": "02/20/2024", "bounding_box": {"left": 0.1, "top": 0.20, "width": 0.10, "height": 0.02}, "confidence": 0.97},
                        {"text": "99214", "bounding_box": {"left": 0.25, "top": 0.20, "width": 0.06, "height": 0.02}, "confidence": 0.99},
                        {"text": "Office", "bounding_box": {"left": 0.35, "top": 0.20, "width": 0.06, "height": 0.02}, "confidence": 0.98},
                        {"text": "Visit,", "bounding_box": {"left": 0.42, "top": 0.20, "width": 0.05, "height": 0.02}, "confidence": 0.97},
                        {"text": "Established", "bounding_box": {"left": 0.48, "top": 0.20, "width": 0.10, "height": 0.02}, "confidence": 0.96},
                        {"text": "Pt,", "bounding_box": {"left": 0.59, "top": 0.20, "width": 0.03, "height": 0.02}, "confidence": 0.98},
                        {"text": "L4", "bounding_box": {"left": 0.63, "top": 0.20, "width": 0.02, "height": 0.02}, "confidence": 0.99},
                        {"text": "$285.00", "bounding_box": {"left": 0.70, "top": 0.20, "width": 0.08, "height": 0.02}, "confidence": 0.98},
                        {"text": "$210.00", "bounding_box": {"left": 0.82, "top": 0.20, "width": 0.08, "height": 0.02}, "confidence": 0.97}
                    ]
                }
            ]
        }
        
        result = link_verification(extracted, ocr_map, file_id="test-file-8")
        
        # Verify top-level fields have refs
        assert "source_refs" in result
        assert len(result["source_refs"]) >= 2  # invoice_number + total_amount
        
        # Verify line item has multiple refs
        item_refs = result["line_items"][0]["source_refs"]
        assert len(item_refs) >= 4  # date, cpt, description, charged_amount, allowed_amount
        
        # Verify match summary
        summary = result["_match_summary"]
        assert summary["total_fields"] >= 7
        assert summary["matched"] >= 5
        assert summary["match_rate"] >= 0.6
        
        print(f"✓ Integration test passed: {summary}")
    
    def test_chronology_integration(self):
        """
        Integration test: Complete chronology with events
        """
        extracted = {
            "patient_name": "Jennifer Martinez",
            "events": [
                {
                    "date": "2024-02-14",
                    "provider": "Memorial Regional Hospital",
                    "encounter_type": "Emergency Visit",
                    "diagnosis_codes": ["K35.20"]
                }
            ]
        }
        
        ocr_map = {
            "pages": [
                {
                    "page_number": 1,
                    "width": 612,
                    "height": 792,
                    "words": [
                        {"text": "Jennifer", "bounding_box": {"left": 0.2, "top": 0.10, "width": 0.08, "height": 0.02}, "confidence": 0.98},
                        {"text": "Martinez", "bounding_box": {"left": 0.29, "top": 0.10, "width": 0.08, "height": 0.02}, "confidence": 0.97},
                        {"text": "02/14/2024", "bounding_box": {"left": 0.1, "top": 0.20, "width": 0.10, "height": 0.02}, "confidence": 0.98},
                        {"text": "Memorial", "bounding_box": {"left": 0.25, "top": 0.20, "width": 0.08, "height": 0.02}, "confidence": 0.97},
                        {"text": "Regional", "bounding_box": {"left": 0.34, "top": 0.20, "width": 0.08, "height": 0.02}, "confidence": 0.96},
                        {"text": "Hospital", "bounding_box": {"left": 0.43, "top": 0.20, "width": 0.08, "height": 0.02}, "confidence": 0.98},
                        {"text": "Emergency", "bounding_box": {"left": 0.55, "top": 0.20, "width": 0.09, "height": 0.02}, "confidence": 0.97},
                        {"text": "Visit", "bounding_box": {"left": 0.65, "top": 0.20, "width": 0.05, "height": 0.02}, "confidence": 0.98},
                        {"text": "K35.20", "bounding_box": {"left": 0.75, "top": 0.20, "width": 0.06, "height": 0.02}, "confidence": 0.99}
                    ]
                }
            ]
        }
        
        result = link_verification(extracted, ocr_map, file_id="test-file-9")
        
        # Verify patient name has refs
        assert "source_refs" in result
        patient_ref = next((r for r in result["source_refs"] if r["field"] == "patient_name"), None)
        assert patient_ref is not None
        
        # Verify event has multiple refs
        event_refs = result["events"][0]["source_refs"]
        assert len(event_refs) >= 3  # date, provider, encounter_type, diagnosis_code
        
        # Verify match summary
        summary = result["_match_summary"]
        assert summary["matched"] >= 3
        
        print(f"✓ Chronology integration test passed: {summary}")


if __name__ == "__main__":
    """Run tests manually"""
    test = TestVerificationLinkage()
    
    print("\n" + "="*60)
    print("VERIFICATION LINKAGE SERVICE TEST SUITE")
    print("="*60 + "\n")
    
    try:
        test.setup_method()
        test.test_case_1_exact_code_match()
        
        test.setup_method()
        test.test_case_2_amount_with_currency()
        
        test.setup_method()
        test.test_case_3_date_format_mismatch()
        
        test.setup_method()
        test.test_case_4_fuzzy_provider_match()
        
        test.setup_method()
        test.test_case_5_multiword_description()
        
        test.setup_method()
        test.test_no_match_found()
        
        test.setup_method()
        test.test_multiple_occurrences()
        
        test.setup_method()
        test.test_full_bill_integration()
        
        test.setup_method()
        test.test_chronology_integration()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        raise
