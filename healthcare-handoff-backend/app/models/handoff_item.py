"""HandoffItem model for task items linked to handoffs."""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from datetime import datetime
import enum
from app.db.base import Base


class ItemTypeEnum(str, enum.Enum):
    """Type of handoff item."""
    LAB_TEST = "LAB_TEST"
    MEDICATION = "MEDICATION"
    FOLLOW_UP = "FOLLOW_UP"
    MONITORING = "MONITORING"
    CONSULTATION = "CONSULTATION"
    OTHER = "OTHER"


class ItemStatusEnum(str, enum.Enum):
    """Item completion status."""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class HandoffItem(Base):
    """HandoffItem table for action items."""

    __tablename__ = "handoff_items"

    id = Column(String(36), primary_key=True)
    handoff_id = Column(String(36), ForeignKey("handoffs.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    item_type = Column(SQLEnum(ItemTypeEnum), nullable=False)
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    due_date = Column(DateTime, nullable=True, index=True)
    status = Column(SQLEnum(ItemStatusEnum), default=ItemStatusEnum.OPEN, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<HandoffItem(id={self.id}, handoff_id={self.handoff_id}, title={self.title})>"

    def to_dict(self):
        return {
            "id": self.id,
            "handoff_id": self.handoff_id,
            "title": self.title,
            "description": self.description,
            "item_type": self.item_type.value,
            "assigned_to": self.assigned_to,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
