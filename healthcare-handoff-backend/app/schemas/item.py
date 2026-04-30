"""Pydantic schemas for handoff item operations."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.handoff_item import ItemTypeEnum, ItemStatusEnum


class ItemCreate(BaseModel):
    """Request body for creating an item."""

    title: str = Field(..., min_length=1, max_length=255, description="Item title")
    description: Optional[str] = Field(None, max_length=1000, description="Item description")
    item_type: ItemTypeEnum = Field(..., description="Type of item")
    assigned_to: str = Field(..., description="User ID to assign item to")
    due_date: Optional[datetime] = Field(None, description="Due date for completion")

    @field_validator("due_date")
    @classmethod
    def due_date_must_be_future(cls, v):
        if v and v <= datetime.utcnow():
            raise ValueError("Due date must be in the future")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Order chest X-ray",
                "description": "Confirm resolution of infiltrate",
                "item_type": "LAB_TEST",
                "assigned_to": "uuid-456",
                "due_date": "2025-01-17T12:00:00"
            }
        }


class ItemUpdate(BaseModel):
    """Request body for updating an item."""

    status: Optional[ItemStatusEnum] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None

    @field_validator("due_date")
    @classmethod
    def due_date_must_be_future(cls, v):
        if v and v <= datetime.utcnow():
            raise ValueError("Due date must be in the future")
        return v


class ItemResponse(BaseModel):
    """Response model for item."""

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
    completed_at: Optional[str]

    model_config = ConfigDict(from_attributes=True)