"""User model for authentication and role management."""

from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from datetime import datetime
import enum
from app.db.base import Base


class RoleEnum(str, enum.Enum):
    """User roles."""
    INTERN = "intern"
    NURSE = "nurse"
    DOCTOR = "doctor"
    ADMIN = "admin"


class User(Base):
    """User table."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(RoleEnum), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
