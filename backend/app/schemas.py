from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

# --- Core Primitive ---

class BoundingBox(BaseModel):
    left: float
    top: float
    width: float
    height: float

class SourceReference(BaseModel):
    file_id: UUID
    page_number: int
    bounding_box: BoundingBox
    confidence: float

class FieldSourceReference(SourceReference):
    """Links a specific field in a parent object to a source location."""
    field: str

# --- Medical Chronology ---

class MedicalEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    date: str
    provider: str
    encounter_type: str
    summary: str
    diagnosis_codes: List[str]
    source_refs: List[FieldSourceReference] = []

class MedicalChronology(BaseModel):
    chronology_id: UUID = Field(default_factory=uuid4)
    patient_name: str
    events: List[MedicalEvent]

# --- Medical Bill ---

class BillLineItem(BaseModel):
    date_of_service: str
    cpt_code: Optional[str] = None
    description: str
    charged_amount: float
    allowed_amount: Optional[float] = None
    source_refs: List[FieldSourceReference] = []

class MedicalBill(BaseModel):
    bill_id: UUID = Field(default_factory=uuid4)
    invoice_number: str
    total_amount: float
    line_items: List[BillLineItem]
