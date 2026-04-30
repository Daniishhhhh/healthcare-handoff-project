"""Patient model for storing patient information."""

from sqlalchemy import Column, String, Date, DateTime, ForeignKey
from datetime import datetime
from app.db.base import Base


class Patient(Base):
    """Patient table."""

    __tablename__ = "patients"

    id = Column(String(36), primary_key=True)
    mrn = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Patient(id={self.id}, mrn={self.mrn}, name={self.name})>"

    def to_dict(self):
        return {
            "id": self.id,
            "mrn": self.mrn,
            "name": self.name,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
