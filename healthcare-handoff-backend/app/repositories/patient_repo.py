"""Patient repository."""

from sqlalchemy.orm import Session
from app.models.patient import Patient
from app.repositories.base import BaseRepository
from typing import Optional


class PatientRepository(BaseRepository[Patient]):
    """Repository for Patient operations."""

    def __init__(self, db: Session):
        super().__init__(db, Patient)

    def find_by_mrn(self, mrn: str) -> Optional[Patient]:
        """Find patient by Medical Record Number."""
        return self.db.query(Patient).filter(Patient.mrn == mrn).first()

    def find_by_created_by(self, user_id: str, limit: int = 100) -> list[Patient]:
        """Find patients created by a specific user."""
        return self.db.query(Patient).filter(Patient.created_by == user_id).limit(limit).all()
