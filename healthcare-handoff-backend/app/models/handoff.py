"""Handoff model for patient responsibility transfers."""

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, JSON, Enum as SQLEnum
from datetime import datetime
import enum
from app.db.base import Base


class HandoffStatusEnum(str, enum.Enum):
    """Handoff status values."""
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    ACCEPTED = "ACCEPTED"
    COMPLETED = "COMPLETED"
    ESCALATED = "ESCALATED"


class HandoffPriorityEnum(str, enum.Enum):
    """Handoff priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Handoff(Base):
    """Handoff table for tracking patient transfers."""

    __tablename__ = "handoffs"

    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(SQLEnum(HandoffStatusEnum), default=HandoffStatusEnum.DRAFT, nullable=False, index=True)
    priority = Column(SQLEnum(HandoffPriorityEnum), default=HandoffPriorityEnum.MEDIUM, nullable=False, index=True)

    diagnosis_summary = Column(Text, nullable=True)
    pending_tests = Column(Text, nullable=True)
    medication_changes = Column(Text, nullable=True)
    follow_up_deadline = Column(DateTime, nullable=True, index=True)
    additional_notes = Column(Text, nullable=True)

    is_ready = Column(Boolean, default=False)
    last_readiness_check_at = Column(DateTime, nullable=True)
    readiness_check_result = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Handoff(id={self.id}, patient_id={self.patient_id}, status={self.status})>"

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "created_by": self.created_by,
            "assigned_to": self.assigned_to,
            "status": self.status.value,
            "priority": self.priority.value,
            "diagnosis_summary": self.diagnosis_summary,
            "pending_tests": self.pending_tests,
            "medication_changes": self.medication_changes,
            "follow_up_deadline": self.follow_up_deadline.isoformat() if self.follow_up_deadline else None,
            "additional_notes": self.additional_notes,
            "is_ready": self.is_ready,
            "last_readiness_check_at": self.last_readiness_check_at.isoformat() if self.last_readiness_check_at else None,
            "readiness_check_result": self.readiness_check_result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
