"""Audit log schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List


class AuditLogResponse(BaseModel):
    """Response model for audit log entry."""

    id: str
    user_id: Optional[str]
    entity_type: str
    entity_id: str
    action: str
    old_values: Optional[dict]
    new_values: Optional[dict]
    reason: Optional[str]
    created_at: str

    class Config:
        from_attributes = True
