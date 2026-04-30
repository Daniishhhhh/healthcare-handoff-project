"""AuditLog repository."""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.audit_log import AuditLog, AuditActionEnum
from app.repositories.base import BaseRepository
from typing import List, Optional


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for AuditLog operations."""

    def __init__(self, db: Session):
        super().__init__(db, AuditLog)

    def find_by_entity(self, entity_type: str, entity_id: str, limit: int = 50) -> List[AuditLog]:
        """Find all audit logs for a specific entity."""
        return self.db.query(AuditLog).filter(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id,
        ).order_by(desc(AuditLog.created_at)).limit(limit).all()

    def find_by_user(self, user_id: str, limit: int = 100) -> List[AuditLog]:
        """Find all audit logs created by a specific user."""
        return self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(desc(AuditLog.created_at)).limit(limit).all()

    def get_all_logs(
        self,
        entity_type: Optional[str] = None,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ):
        """Get audit logs with optional filtering."""
        query = self.db.query(AuditLog)

        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            try:
                action_enum = AuditActionEnum[action.upper()]
                query = query.filter(AuditLog.action == action_enum)
            except KeyError:
                pass

        total = query.count()
        logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "logs": logs,
        }
