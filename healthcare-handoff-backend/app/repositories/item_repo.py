"""HandoffItem repository."""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.handoff_item import HandoffItem, ItemStatusEnum
from app.repositories.base import BaseRepository
from typing import List, Optional
from datetime import datetime


class HandoffItemRepository(BaseRepository[HandoffItem]):
    """Repository for HandoffItem operations."""

    def __init__(self, db: Session):
        super().__init__(db, HandoffItem)

    def find_by_handoff(self, handoff_id: str) -> List[HandoffItem]:
        """Find all items in a handoff."""
        return self.db.query(HandoffItem).filter(
            HandoffItem.handoff_id == handoff_id
        ).order_by(HandoffItem.created_at).all()

    def find_by_assigned_to(self, user_id: str, status: Optional[str] = None) -> List[HandoffItem]:
        """Find items assigned to a user."""
        query = self.db.query(HandoffItem).filter(HandoffItem.assigned_to == user_id)
        if status:
            query = query.filter(HandoffItem.status == status)
        return query.order_by(desc(HandoffItem.due_date)).all()

    def find_overdue(self) -> List[HandoffItem]:
        """Find all overdue items."""
        return self.db.query(HandoffItem).filter(
            HandoffItem.status != ItemStatusEnum.COMPLETED,
            HandoffItem.due_date < datetime.utcnow(),
        ).all()
