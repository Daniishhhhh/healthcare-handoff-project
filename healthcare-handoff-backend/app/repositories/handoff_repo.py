"""Handoff repository."""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.handoff import Handoff, HandoffStatusEnum
from app.repositories.base import BaseRepository
from typing import Optional, List


class HandoffRepository(BaseRepository[Handoff]):
    """Repository for Handoff operations."""

    def __init__(self, db: Session):
        super().__init__(db, Handoff)

    def find_by_patient(self, patient_id: str) -> List[Handoff]:
        """Find all handoffs for a patient."""
        return self.db.query(Handoff).filter(Handoff.patient_id == patient_id).all()

    def find_by_assigned_to(self, user_id: str, status: Optional[str] = None) -> List[Handoff]:
        """Find handoffs assigned to a user."""
        query = self.db.query(Handoff).filter(Handoff.assigned_to == user_id)
        if status:
            query = query.filter(Handoff.status == status)
        return query.order_by(desc(Handoff.created_at)).all()

    def find_by_created_by(self, user_id: str, status: Optional[str] = None) -> List[Handoff]:
        """Find handoffs created by a user."""
        query = self.db.query(Handoff).filter(Handoff.created_by == user_id)
        if status:
            query = query.filter(Handoff.status == status)
        return query.order_by(desc(Handoff.created_at)).all()

    def find_active_handoffs(self) -> List[Handoff]:
        """Find all active handoffs."""
        return self.db.query(Handoff).filter(
            Handoff.status.in_([HandoffStatusEnum.ACCEPTED, HandoffStatusEnum.PENDING_REVIEW])
        ).all()
