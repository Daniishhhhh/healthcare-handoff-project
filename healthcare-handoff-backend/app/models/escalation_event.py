"""EscalationEvent model for tracking escalations."""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from datetime import datetime
from app.db.base import Base


class EscalationEvent(Base):
    """EscalationEvent table for audit trail of escalations."""

    __tablename__ = "escalation_events"

    id = Column(String(36), primary_key=True)
    handoff_id = Column(String(36), ForeignKey("handoffs.id", ondelete="CASCADE"), nullable=False, index=True)
    triggered_by = Column(String(50), nullable=False)
    reason = Column(String(255), nullable=False)
    action_taken = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<EscalationEvent(id={self.id}, handoff_id={self.handoff_id}, reason={self.reason})>"

    def to_dict(self):
        return {
            "id": self.id,
            "handoff_id": self.handoff_id,
            "triggered_by": self.triggered_by,
            "reason": self.reason,
            "action_taken": self.action_taken,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
