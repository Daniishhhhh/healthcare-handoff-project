"""Pydantic schemas for patient operations."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date


class PatientCreate(BaseModel):
    """Request body for creating a patient."""

    mrn: str = Field(..., min_length=1, max_length=100, description="Medical Record Number")
    name: str = Field(..., min_length=1, max_length=255, description="Patient full name")
    date_of_birth: Optional[date] = Field(None, description="Patient date of birth")

    class Config:
        json_schema_extra = {
            "example": {
                "mrn": "MRN-2025-00123",
                "name": "John Smith",
                "date_of_birth": "1990-05-15"
            }
        }


class PatientResponse(BaseModel):
    """Response model for patient."""

    id: str
    mrn: str
    name: str
    date_of_birth: Optional[str]
    created_by: str
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)