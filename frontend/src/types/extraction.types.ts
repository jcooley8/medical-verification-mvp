// Type definitions for extraction results and source references

export interface BoundingBox {
  left: number;   // 0-1 normalized
  top: number;    // 0-1 normalized
  width: number;  // 0-1 normalized
  height: number; // 0-1 normalized
}

export interface SourceReference {
  field: string;
  page_number: number;
  bounding_box: BoundingBox;
  confidence: number;
  text: string;
}

export interface ChronologyEvent {
  date: string;
  provider: string;
  facility: string;
  event_type: string;
  description: string;
  source_refs: SourceReference[];
}

export interface BillLineItem {
  cpt_code: string;
  description: string;
  quantity: number;
  unit_price: number;
  total: number;
  date_of_service: string;
  source_refs: SourceReference[];
}

export interface ExtractionResult {
  document_id: string;
  chronology?: ChronologyEvent[];
  bills?: BillLineItem[];
  pdf_url?: string;
  total_pages?: number;
}

export interface HighlightRegion {
  id: string;
  boundingBox: BoundingBox;
  field: string;
  confidence: number;
  isPrimary: boolean;
}

export interface PixelBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface PageDimensions {
  width: number;
  height: number;
}
