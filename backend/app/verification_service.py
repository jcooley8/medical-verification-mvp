"""
Verification Linkage Service

This module implements the verification linkage algorithm that matches extracted
structured data back to source locations in OCR output, enabling click-to-verify UI.

Implements 5 matching strategies:
1. Exact string match (for codes, IDs)
2. Normalized amount match (for currency values)
3. Date normalization (for various date formats)
4. Fuzzy string match (for names with OCR errors)
5. Multi-word span matching (for descriptions)
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dateutil import parser
from rapidfuzz import fuzz
import copy

logger = logging.getLogger(__name__)


class VerificationLinker:
    """Main class for linking extracted data to OCR source locations"""
    
    def __init__(self):
        self.match_stats = {
            "total_fields": 0,
            "matched": 0,
            "unmatched": 0,
            "fuzzy_matched": 0,
            "multiword_matched": 0
        }
    
    def link_verification(
        self, 
        extracted_json: Dict[str, Any], 
        ocr_map: Dict[str, Any],
        file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for verification linkage.
        
        Args:
            extracted_json: Structured data from LLM extraction
            ocr_map: OCR output with words and bounding boxes
            file_id: UUID of the source file (optional)
        
        Returns:
            Enriched JSON with source_refs populated
        """
        logger.info("Starting verification linkage...")
        self.match_stats = {
            "total_fields": 0,
            "matched": 0,
            "unmatched": 0,
            "fuzzy_matched": 0,
            "multiword_matched": 0
        }
        
        # Deep copy to avoid modifying the original
        enriched = copy.deepcopy(extracted_json)
        
        # Process based on document type
        if "events" in enriched:
            # Chronology document
            self._process_chronology(enriched, ocr_map, file_id)
        elif "line_items" in enriched:
            # Bill document
            self._process_bill(enriched, ocr_map, file_id)
        
        # Add match summary
        enriched["_match_summary"] = {
            "total_fields": self.match_stats["total_fields"],
            "matched": self.match_stats["matched"],
            "unmatched": self.match_stats["unmatched"],
            "fuzzy_matched": self.match_stats["fuzzy_matched"],
            "multiword_matched": self.match_stats["multiword_matched"],
            "match_rate": round(
                self.match_stats["matched"] / max(self.match_stats["total_fields"], 1),
                2
            )
        }
        
        logger.info(f"Verification linkage completed: {enriched['_match_summary']}")
        return enriched
    
    def _process_chronology(
        self,
        chronology: Dict[str, Any],
        ocr_map: Dict[str, Any],
        file_id: Optional[str]
    ):
        """Process chronology document events"""
        # Link patient name
        if "patient_name" in chronology:
            self._link_field(
                chronology, "patient_name", chronology["patient_name"],
                ocr_map, file_id, "name"
            )
        
        # Link each event's fields
        for event in chronology.get("events", []):
            if "source_refs" not in event:
                event["source_refs"] = []
            
            # Link date
            if "date" in event:
                refs = self._find_matches(
                    event["date"], ocr_map, "date", file_id
                )
                event["source_refs"].extend(refs)
            
            # Link provider name
            if "provider" in event:
                refs = self._find_matches(
                    event["provider"], ocr_map, "provider", file_id
                )
                event["source_refs"].extend(refs)
            
            # Link encounter type
            if "encounter_type" in event:
                refs = self._find_matches(
                    event["encounter_type"], ocr_map, "encounter_type", file_id
                )
                event["source_refs"].extend(refs)
            
            # Link diagnosis codes
            for code in event.get("diagnosis_codes", []):
                refs = self._find_matches(
                    code, ocr_map, "diagnosis_code", file_id
                )
                event["source_refs"].extend(refs)
    
    def _process_bill(
        self,
        bill: Dict[str, Any],
        ocr_map: Dict[str, Any],
        file_id: Optional[str]
    ):
        """Process bill document line items"""
        # Link invoice number
        if "invoice_number" in bill:
            self._link_field(
                bill, "invoice_number", bill["invoice_number"],
                ocr_map, file_id, "code"
            )
        
        # Link total amount
        if "total_amount" in bill:
            self._link_field(
                bill, "total_amount", bill["total_amount"],
                ocr_map, file_id, "amount"
            )
        
        # Link each line item's fields
        for item in bill.get("line_items", []):
            if "source_refs" not in item:
                item["source_refs"] = []
            
            # Link date of service
            if "date_of_service" in item:
                refs = self._find_matches(
                    item["date_of_service"], ocr_map, "date", file_id
                )
                item["source_refs"].extend(refs)
            
            # Link CPT code
            if "cpt_code" in item:
                refs = self._find_matches(
                    item["cpt_code"], ocr_map, "code", file_id
                )
                item["source_refs"].extend(refs)
            
            # Link description
            if "description" in item:
                refs = self._find_matches(
                    item["description"], ocr_map, "description", file_id
                )
                item["source_refs"].extend(refs)
            
            # Link charged amount
            if "charged_amount" in item:
                refs = self._find_matches(
                    item["charged_amount"], ocr_map, "amount", file_id
                )
                item["source_refs"].extend(refs)
            
            # Link allowed amount
            if "allowed_amount" in item:
                refs = self._find_matches(
                    item["allowed_amount"], ocr_map, "amount", file_id
                )
                item["source_refs"].extend(refs)
    
    def _link_field(
        self,
        parent_obj: Dict[str, Any],
        field_name: str,
        value: Any,
        ocr_map: Dict[str, Any],
        file_id: Optional[str],
        field_type: str
    ):
        """Link a single top-level field"""
        if "source_refs" not in parent_obj:
            parent_obj["source_refs"] = []
        
        refs = self._find_matches(value, ocr_map, field_type, file_id, field_name)
        parent_obj["source_refs"].extend(refs)
    
    def _find_matches(
        self,
        value: Any,
        ocr_map: Dict[str, Any],
        field_type: str,
        file_id: Optional[str],
        field_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find all potential matches for a value in the OCR map.
        
        Args:
            value: The extracted value to find
            ocr_map: OCR output with words and bounding boxes
            field_type: Type hint for matching strategy (code, amount, date, name, description)
            file_id: UUID of source file
            field_name: Name of the field being matched
        
        Returns:
            List of source_ref dictionaries
        """
        self.match_stats["total_fields"] += 1
        candidates = []
        
        # Strategy 1: Exact String Match
        if field_type in ["code", "string"]:
            candidates.extend(
                self._exact_match(value, ocr_map)
            )
        
        # Strategy 2: Normalized Amount Match
        if field_type == "amount":
            candidates.extend(
                self._amount_match(value, ocr_map)
            )
        
        # Strategy 3: Date Normalization
        if field_type == "date":
            candidates.extend(
                self._date_match(value, ocr_map)
            )
        
        # Strategy 4: Fuzzy String Match
        if field_type in ["name", "provider", "encounter_type", "description"]:
            candidates.extend(
                self._fuzzy_match(value, ocr_map, field_type)
            )
        
        # Strategy 5: Multi-Word Span Match
        if field_type in ["description", "provider", "encounter_type", "name"]:
            candidates.extend(
                self._multiword_match(value, ocr_map)
            )
        
        # Rank and select best matches
        best_refs = self._rank_and_select(candidates, field_type)
        
        # Format as source_refs
        result = []
        for candidate in best_refs:
            source_ref = {
                "field": field_name or field_type,
                "page_number": candidate["page_number"],
                "bounding_box": candidate["bbox"],
                "confidence": round(candidate["confidence"], 2),
                "matched_text": candidate["matched_text"]
            }
            
            if file_id:
                source_ref["file_id"] = file_id
            
            if "strategy" in candidate:
                source_ref["strategy"] = candidate["strategy"]
            
            result.append(source_ref)
        
        # Update stats
        if result:
            self.match_stats["matched"] += 1
            if any(r.get("strategy") == "fuzzy" for r in result):
                self.match_stats["fuzzy_matched"] += 1
            if any(r.get("strategy") == "multiword" for r in result):
                self.match_stats["multiword_matched"] += 1
        else:
            self.match_stats["unmatched"] += 1
        
        return result
    
    def _exact_match(
        self,
        value: Any,
        ocr_map: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Strategy 1: Exact string matching"""
        candidates = []
        value_str = str(value).strip()
        
        for page in ocr_map.get("pages", []):
            page_num = page.get("page_number", 1)
            
            for word in page.get("words", []):
                if word["text"].strip() == value_str:
                    candidates.append({
                        "page_number": page_num,
                        "bbox": self._normalize_bbox(word["bounding_box"], page),
                        "confidence": word.get("confidence", 0.95) + 0.05,  # Exact match boost
                        "matched_text": word["text"],
                        "strategy": "exact"
                    })
        
        return candidates
    
    def _amount_match(
        self,
        value: Any,
        ocr_map: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Strategy 2: Normalized amount matching"""
        candidates = []
        normalized_value = self._normalize_amount(value)
        
        if normalized_value is None:
            return candidates
        
        for page in ocr_map.get("pages", []):
            page_num = page.get("page_number", 1)
            
            for word in page.get("words", []):
                ocr_amount = self._normalize_amount(word["text"])
                
                if ocr_amount is not None:
                    # Check if amounts match within tolerance
                    if abs(ocr_amount - normalized_value) < 0.01:
                        boost = 0.03 if ocr_amount == normalized_value else 0.01
                        candidates.append({
                            "page_number": page_num,
                            "bbox": self._normalize_bbox(word["bounding_box"], page),
                            "confidence": word.get("confidence", 0.95) + boost,
                            "matched_text": word["text"],
                            "strategy": "amount"
                        })
        
        return candidates
    
    def _date_match(
        self,
        value: Any,
        ocr_map: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Strategy 3: Date normalization matching"""
        candidates = []
        canonical_date = self._parse_date(value)
        
        if canonical_date is None:
            return candidates
        
        for page in ocr_map.get("pages", []):
            page_num = page.get("page_number", 1)
            
            for word in page.get("words", []):
                ocr_date = self._parse_date(word["text"])
                
                if ocr_date == canonical_date:
                    candidates.append({
                        "page_number": page_num,
                        "bbox": self._normalize_bbox(word["bounding_box"], page),
                        "confidence": word.get("confidence", 0.95) + 0.02,
                        "matched_text": word["text"],
                        "strategy": "date"
                    })
        
        return candidates
    
    def _fuzzy_match(
        self,
        value: Any,
        ocr_map: Dict[str, Any],
        field_type: str
    ) -> List[Dict[str, Any]]:
        """Strategy 4: Fuzzy string matching for names/descriptions"""
        candidates = []
        value_str = str(value).strip()
        
        # Set threshold based on field type
        threshold = 85 if field_type in ["name", "provider"] else 75
        
        for page in ocr_map.get("pages", []):
            page_num = page.get("page_number", 1)
            
            for word in page.get("words", []):
                ratio = fuzz.ratio(value_str.lower(), word["text"].lower())
                
                if ratio >= threshold:
                    # Calculate penalty based on fuzzy score
                    penalty = (100 - ratio) / 100 * 0.5
                    confidence = word.get("confidence", 0.95) - penalty
                    
                    candidates.append({
                        "page_number": page_num,
                        "bbox": self._normalize_bbox(word["bounding_box"], page),
                        "confidence": max(0.0, confidence),
                        "matched_text": word["text"],
                        "strategy": "fuzzy",
                        "fuzzy_ratio": ratio
                    })
        
        return candidates
    
    def _multiword_match(
        self,
        value: Any,
        ocr_map: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Strategy 5: Multi-word span matching"""
        candidates = []
        value_str = str(value).strip()
        
        # Only try multi-word if value has multiple words
        if len(value_str.split()) < 2:
            return candidates
        
        for page in ocr_map.get("pages", []):
            page_num = page.get("page_number", 1)
            words = page.get("words", [])
            
            # Sliding window of up to 10 consecutive words
            max_window = min(10, len(words))
            
            for window_size in range(2, max_window + 1):
                for i in range(len(words) - window_size + 1):
                    span = words[i:i + window_size]
                    concatenated = " ".join([w["text"] for w in span])
                    
                    ratio = fuzz.ratio(value_str.lower(), concatenated.lower())
                    
                    if ratio >= 80:
                        # Compute union bounding box
                        union_bbox = self._compute_union_bbox(span, page)
                        
                        # Average OCR confidence
                        avg_confidence = sum(w.get("confidence", 0.95) for w in span) / len(span)
                        
                        candidates.append({
                            "page_number": page_num,
                            "bbox": union_bbox,
                            "confidence": avg_confidence,
                            "matched_text": concatenated,
                            "strategy": "multiword",
                            "word_count": len(span),
                            "fuzzy_ratio": ratio
                        })
        
        return candidates
    
    def _rank_and_select(
        self,
        candidates: List[Dict[str, Any]],
        field_type: str
    ) -> List[Dict[str, Any]]:
        """
        Rank candidates by confidence and select best match(es).
        
        Returns top candidate or top-3 if there's ambiguity.
        """
        if not candidates:
            return []
        
        # Sort by confidence descending
        candidates.sort(key=lambda c: c["confidence"], reverse=True)
        
        # If top candidate is very confident and clearly better, return it alone
        if candidates[0]["confidence"] >= 0.90:
            if len(candidates) == 1 or \
               candidates[0]["confidence"] - candidates[1]["confidence"] > 0.15:
                return [candidates[0]]
        
        # If multiple candidates are close in confidence, return top 3
        if len(candidates) > 1 and candidates[1]["confidence"] >= 0.75:
            return candidates[:3]
        
        # Otherwise return the best one
        return [candidates[0]]
    
    def _normalize_amount(self, text: Any) -> Optional[float]:
        """Strip currency symbols, commas; parse as float"""
        if isinstance(text, (int, float)):
            return float(text)
        
        # Remove all non-digit and non-decimal point characters
        cleaned = re.sub(r'[^\d.]', '', str(text))
        
        try:
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def _parse_date(self, text: Any) -> Optional[str]:
        """Parse date string to YYYY-MM-DD canonical format"""
        try:
            dt = parser.parse(str(text))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError, parser.ParserError):
            return None
    
    def _normalize_bbox(
        self,
        bbox: Dict[str, float],
        page: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Normalize bounding box coordinates to 0-1 range if needed.
        If bbox values are already < 1, assume already normalized.
        Otherwise, normalize using page dimensions.
        """
        # Check if already normalized (all values < 2)
        if all(v <= 2 for v in [
            bbox.get("left", 0),
            bbox.get("top", 0),
            bbox.get("width", 0),
            bbox.get("height", 0)
        ]):
            return bbox
        
        # Normalize using page dimensions
        page_width = page.get("width", 612)
        page_height = page.get("height", 792)
        
        return {
            "left": bbox.get("left", 0) / page_width,
            "top": bbox.get("top", 0) / page_height,
            "width": bbox.get("width", 0) / page_width,
            "height": bbox.get("height", 0) / page_height
        }
    
    def _compute_union_bbox(
        self,
        words: List[Dict[str, Any]],
        page: Dict[str, Any]
    ) -> Dict[str, float]:
        """Compute bounding box that encompasses all words"""
        # First normalize all bboxes
        normalized = [self._normalize_bbox(w["bounding_box"], page) for w in words]
        
        min_left = min(b["left"] for b in normalized)
        min_top = min(b["top"] for b in normalized)
        max_right = max(b["left"] + b["width"] for b in normalized)
        max_bottom = max(b["top"] + b["height"] for b in normalized)
        
        return {
            "left": min_left,
            "top": min_top,
            "width": max_right - min_left,
            "height": max_bottom - min_top
        }


# Convenience function for direct use
def link_verification(
    extracted_json: Dict[str, Any],
    ocr_map: Dict[str, Any],
    file_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Link extracted data to OCR source locations.
    
    Args:
        extracted_json: Structured data from LLM extraction
        ocr_map: OCR output with words and bounding boxes
        file_id: UUID of the source file (optional)
    
    Returns:
        Enriched JSON with source_refs populated
    """
    linker = VerificationLinker()
    return linker.link_verification(extracted_json, ocr_map, file_id)
