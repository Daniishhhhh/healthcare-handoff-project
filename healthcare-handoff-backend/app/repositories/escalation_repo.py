"""EscalationEvent repository."""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.escalation_event import EscalationEvent
from app.repositories.base import BaseRepository
from typing import List


class EscalationEventRepository(BaseRepository[EscalationEvent]):
    """Repository for EscalationEvent operations."""

    def __init__(self, db: Session):
        super().__init__(db, EscalationEvent)

    def find_by_handoff(self, handoff_id: str) -> List[EscalationEvent]:
        """Find all escalation events for a handoff."""
        return self.db.query(EscalationEvent).filter(
            EscalationEvent.handoff_id == handoff_id
        ).order_by(desc(EscalationEvent.created_at)).all()

    def find_recent(self, limit: int = 50) -> List[EscalationEvent]:
        """Find recent escalation events."""
        return self.db.query(EscalationEvent).order_by(
            desc(EscalationEvent.created_at)
        ).limit(limit).all()
