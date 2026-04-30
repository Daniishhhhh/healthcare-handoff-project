"""Pydantic schemas for handoff operations."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.handoff import HandoffStatusEnum, HandoffPriorityEnum


class HandoffItemResponse(BaseModel):
    """Response model for handoff item."""

    id: str
    handoff_id: str
    title: str
    description: Optional[str]
    item_type: str
    assigned_to: str
    assigned_to_name: Optional[str] = None
    due_date: Optional[str]
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class HandoffCreate(BaseModel):
    """Request body for creating a handoff."""

    patient_id: str = Field(..., description="Patient ID")
    assigned_to: str = Field(..., description="User ID to assign responsibility to")
    priority: HandoffPriorityEnum = Field(HandoffPriorityEnum.MEDIUM, description="Handoff priority")
    diagnosis_summary: str = Field(..., min_length=1, max_length=500, description="Diagnosis summary")
    pending_tests: Optional[str] = Field(None, max_length=1000, description="Pending tests/investigations")
    medication_changes: Optional[str] = Field(None, max_length=1000, description="Medication changes and rationale")
    follow_up_deadline: datetime = Field(..., description="When follow-up must occur")
    additional_notes: Optional[str] = Field(None, max_length=2000, description="Additional clinical notes")

    @field_validator("follow_up_deadline")
    @classmethod
    def follow_up_must_be_future(cls, v):
        if v <= datetime.utcnow():
            raise ValueError("Follow-up deadline must be in the future")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "uuid-123",
                "assigned_to": "uuid-456",
                "priority": "HIGH",
                "diagnosis_summary": "Acute bronchitis, treated with antibiotics",
                "pending_tests": "Chest X-ray, sputum culture",
                "medication_changes": "Started Amoxicillin 500mg q8h, D/C Ibuprofen",
                "follow_up_deadline": "2025-01-22T17:00:00",
                "additional_notes": "Patient reports SOB improving"
            }
        }


class HandoffUpdate(BaseModel):
    """Request body for updating a handoff (only DRAFT status)."""

    priority: Optional[HandoffPriorityEnum] = None
    diagnosis_summary: Optional[str] = Field(None, min_length=1, max_length=500)
    pending_tests: Optional[str] = Field(None, max_length=1000)
    medication_changes: Optional[str] = Field(None, max_length=1000)
    follow_up_deadline: Optional[datetime] = None
    additional_notes: Optional[str] = Field(None, max_length=2000)

    @field_validator("follow_up_deadline")
    @classmethod
    def follow_up_must_be_future(cls, v):
        if v and v <= datetime.utcnow():
            raise ValueError("Follow-up deadline must be in the future")
        return v


class ReadinessCheckFailure(BaseModel):
    """A single readiness check failure."""

    code: str = Field(..., description="Failure code")
    message: str = Field(..., description="Human-readable message")
    severity: str = Field(..., description="ERROR or WARNING")
    suggested_fix: str = Field(..., description="How to fix this issue")


class ReadinessCheckResponse(BaseModel):
    """Response from readiness check endpoint."""

    handoff_id: str
    is_ready: bool
    checked_at: str
    failures: List[ReadinessCheckFailure]
    passed_checks: List[str]


class HandoffResponse(BaseModel):
    """Response model for handoff (full details)."""

    id: str
    patient_id: str
    patient_name: Optional[str] = None
    created_by: str
    created_by_name: Optional[str] = None
    assigned_to: str
    assigned_to_name: Optional[str] = None
    status: str
    priority: str
    is_ready: bool
    readiness_check_result: Optional[dict] = None
    diagnosis_summary: str
    pending_tests: Optional[str]
    medication_changes: Optional[str]
    follow_up_deadline: Optional[str]
    additional_notes: Optional[str]
    items: List[HandoffItemResponse] = []
    created_at: str
    updated_at: str
    accepted_at: Optional[str]
    completed_at: Optional[str]

    model_config = ConfigDict(from_attributes=True)