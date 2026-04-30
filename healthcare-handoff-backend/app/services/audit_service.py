"""Audit logging service."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid

from app.models.audit_log import AuditLog, AuditActionEnum
from app.repositories.audit_repo import AuditLogRepository


class AuditService:
    """Service for audit logging operations."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AuditLogRepository(db)

    def log_action(
        self,
        user_id: Optional[str],
        entity_type: str,
        entity_id: str,
        action: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
    ) -> AuditLog:
        """Log an audit action (immutable insert)."""
        
        if isinstance(action, str):
            try:
                action_enum = AuditActionEnum[action.upper()]
            except KeyError:
                action_enum = AuditActionEnum.UPDATE
        else:
            action_enum = action

        log = AuditLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action_enum,
            old_values=old_values,
            new_values=new_values,
            reason=reason,
            created_at=datetime.utcnow(),
        )

        return self.repo.create(log)

    def get_entity_history(self, entity_type: str, entity_id: str, limit: int = 50):
        """Get all audit logs for a specific entity."""
        return self.repo.find_by_entity(entity_type, entity_id, limit)

    def get_user_actions(self, user_id: str, limit: int = 100):
        """Get all actions performed by a user."""
        return self.repo.find_by_user(user_id, limit)

    def get_all_logs(
        self,
        entity_type: Optional[str] = None,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ):
        """Get audit logs with optional filtering."""
        return self.repo.get_all_logs(entity_type, user_id, action, limit, offset)
