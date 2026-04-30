"""AuditLog model for immutable audit trail."""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from datetime import datetime
import enum
from app.db.base import Base


class AuditActionEnum(str, enum.Enum):
    """Types of audit actions."""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    ACCEPT = "ACCEPT"
    ESCALATE = "ESCALATE"
    COMPLETE = "COMPLETE"
    REASSIGN = "REASSIGN"


class AuditLog(Base):
    """AuditLog table - INSERT ONLY, immutable."""

    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(36), nullable=False, index=True)
    action = Column(SQLEnum(AuditActionEnum), nullable=False, index=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, entity_type={self.entity_type}, action={self.action})>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "action": self.action.value,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "reason": self.reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
