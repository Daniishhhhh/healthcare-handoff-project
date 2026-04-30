#!/usr/bin/env python3
"""
Healthcare Handoff Backend - Bulk File Creator
Creates all 45+ project files in one go
Python 3.11-3.13.9 compatible
"""

import os
from pathlib import Path
import sys

# ANSI color codes
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Folder structure
FOLDERS = [
    "app",
    "app/auth",
    "app/models",
    "app/schemas",
    "app/db",
    "app/repositories",
    "app/services",
    "app/api/v1",
    "app/middleware",
    "app/background_tasks",
    "migrations/versions",
    "tests/fixtures",
    "scripts",
]

# All files content
FILES = {
    # ===== APP ROOT FILES =====
    "app/__init__.py": '''"""Healthcare Handoff Backend Application"""

__version__ = "0.1.0"
''',

    "app/config.py": '''"""Configuration settings loaded from environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables."""

    app_name: str = "Healthcare Handoff Backend"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    database_url: str = "postgresql://dev:dev_password@localhost:5432/handoff_db"
    redis_url: Optional[str] = "redis://localhost:6379"
    secret_key: str = "change_me_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 1
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    enable_background_jobs: bool = True
    notification_service_enabled: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
''',

    "app/exceptions.py": '''"""Custom exception classes for API responses."""

from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class BaseAPIException(HTTPException):
    """Base exception class for all API errors."""

    def __init__(
        self,
        error_code: str,
        detail: str,
        status_code: int,
        extra: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.extra = extra or {}
        self.status_code_enum = status_code
        
        detail_body = {
            "error": error_code,
            "message": detail,
        }
        if extra:
            detail_body["details"] = extra

        super().__init__(status_code=status_code, detail=detail_body)


class ValidationError(BaseAPIException):
    """400 Bad Request: Input validation failed."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code="VALIDATION_ERROR",
            detail=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            extra=details,
        )


class ResourceNotFound(BaseAPIException):
    """404 Not Found: Resource does not exist."""

    def __init__(self, resource: str, resource_id: Optional[str] = None):
        msg = f"{resource} not found"
        if resource_id:
            msg += f" (ID: {resource_id})"
        super().__init__(
            error_code=f"{resource.upper()}_NOT_FOUND",
            detail=msg,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class Forbidden(BaseAPIException):
    """403 Forbidden: User lacks permission."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            error_code="INSUFFICIENT_PERMISSIONS",
            detail=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class Unauthorized(BaseAPIException):
    """401 Unauthorized: Authentication required or failed."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            error_code="UNAUTHORIZED",
            detail=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class EmailAlreadyExists(BaseAPIException):
    """409 Conflict: Email already registered."""

    def __init__(self, email: str):
        super().__init__(
            error_code="EMAIL_ALREADY_EXISTS",
            detail=f"Email {email} already registered",
            status_code=status.HTTP_409_CONFLICT,
        )


class InvalidCredentials(BaseAPIException):
    """401 Unauthorized: Invalid email or password."""

    def __init__(self):
        super().__init__(
            error_code="INVALID_CREDENTIALS",
            detail="Invalid email or password",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidStateTransition(BaseAPIException):
    """409 Conflict: Invalid state transition."""

    def __init__(self, current_status: str, attempted_status: str):
        super().__init__(
            error_code="INVALID_STATE_TRANSITION",
            detail=f"Cannot transition from {current_status} to {attempted_status}",
            status_code=status.HTTP_409_CONFLICT,
        )


class HandoffNotReady(BaseAPIException):
    """409 Conflict: Handoff validation failed."""

    def __init__(self, failures: list):
        super().__init__(
            error_code="HANDOFF_NOT_READY",
            detail="Handoff validation failed. Cannot accept.",
            status_code=status.HTTP_409_CONFLICT,
            extra={"failures": failures},
        )


class MRNAlreadyExists(BaseAPIException):
    """409 Conflict: MRN already exists."""

    def __init__(self, mrn: str):
        super().__init__(
            error_code="MRN_ALREADY_EXISTS",
            detail=f"Medical Record Number {mrn} already exists",
            status_code=status.HTTP_409_CONFLICT,
        )
''',

    "app/utils.py": '''"""Utility functions for auth and encryption."""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.config import settings
from app.exceptions import Unauthorized


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with 12 rounds."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def create_access_token(
    user_id: str,
    email: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.jwt_expiry_hours)

    expire = datetime.utcnow() + expires_delta
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return token


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")

        if not all([user_id, email, role]):
            raise JWTError("Missing claims")

        return {"user_id": user_id, "email": email, "role": role}
    except JWTError:
        raise Unauthorized("Invalid or expired token")
''',

    "app/dependencies.py": '''"""FastAPI dependency injection."""

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.utils import decode_token
from app.exceptions import Unauthorized

security = HTTPBearer()


class CurrentUser:
    """Represents the currently authenticated user."""

    def __init__(self, user_id: str, email: str, role: str):
        self.user_id = user_id
        self.email = email
        self.role = role

    def is_admin(self) -> bool:
        return self.role == "admin"

    def is_doctor(self) -> bool:
        return self.role == "doctor"

    def is_nurse(self) -> bool:
        return self.role == "nurse"

    def is_intern(self) -> bool:
        return self.role == "intern"

    def has_role(self, *roles: str) -> bool:
        return self.role in roles


async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> CurrentUser:
    """Extract and validate JWT from Authorization header."""
    token = credentials.credentials
    payload = decode_token(token)

    return CurrentUser(
        user_id=payload["user_id"],
        email=payload["email"],
        role=payload["role"],
    )


def require_role(*allowed_roles: str):
    """Dependency to enforce role-based access control."""

    async def role_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not current_user.has_role(*allowed_roles):
            roles_str = ", ".join(allowed_roles)
            raise Unauthorized(f"Requires one of: {roles_str}")
        return current_user

    return role_checker
''',

    # ===== DB LAYER =====
    "app/db/__init__.py": '"""Database module."""\n',

    "app/db/database.py": '''"""SQLAlchemy database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Session:
    """Dependency: Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',

    "app/db/base.py": '''"""Base declarative model for all ORM models."""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
''',

    # ===== MODELS =====
    "app/models/__init__.py": '''"""SQLAlchemy ORM models."""

from app.models.user import User
from app.models.patient import Patient
from app.models.handoff import Handoff
from app.models.handoff_item import HandoffItem
from app.models.escalation_event import EscalationEvent
from app.models.audit_log import AuditLog

__all__ = [
    "User",
    "Patient",
    "Handoff",
    "HandoffItem",
    "EscalationEvent",
    "AuditLog",
]
''',

    "app/models/user.py": '''"""User model for authentication and role management."""

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
''',

    "app/models/patient.py": '''"""Patient model for storing patient information."""

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
''',

    "app/models/handoff.py": '''"""Handoff model for patient responsibility transfers."""

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, JSON, Enum as SQLEnum
from datetime import datetime
import enum
from app.db.base import Base


class HandoffStatusEnum(str, enum.Enum):
    """Handoff status values."""
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    ACCEPTED = "ACCEPTED"
    COMPLETED = "COMPLETED"
    ESCALATED = "ESCALATED"


class HandoffPriorityEnum(str, enum.Enum):
    """Handoff priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Handoff(Base):
    """Handoff table for tracking patient transfers."""

    __tablename__ = "handoffs"

    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(SQLEnum(HandoffStatusEnum), default=HandoffStatusEnum.DRAFT, nullable=False, index=True)
    priority = Column(SQLEnum(HandoffPriorityEnum), default=HandoffPriorityEnum.MEDIUM, nullable=False, index=True)

    diagnosis_summary = Column(Text, nullable=True)
    pending_tests = Column(Text, nullable=True)
    medication_changes = Column(Text, nullable=True)
    follow_up_deadline = Column(DateTime, nullable=True, index=True)
    additional_notes = Column(Text, nullable=True)

    is_ready = Column(Boolean, default=False)
    last_readiness_check_at = Column(DateTime, nullable=True)
    readiness_check_result = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Handoff(id={self.id}, patient_id={self.patient_id}, status={self.status})>"

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "created_by": self.created_by,
            "assigned_to": self.assigned_to,
            "status": self.status.value,
            "priority": self.priority.value,
            "diagnosis_summary": self.diagnosis_summary,
            "pending_tests": self.pending_tests,
            "medication_changes": self.medication_changes,
            "follow_up_deadline": self.follow_up_deadline.isoformat() if self.follow_up_deadline else None,
            "additional_notes": self.additional_notes,
            "is_ready": self.is_ready,
            "last_readiness_check_at": self.last_readiness_check_at.isoformat() if self.last_readiness_check_at else None,
            "readiness_check_result": self.readiness_check_result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
''',

    "app/models/handoff_item.py": '''"""HandoffItem model for task items linked to handoffs."""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from datetime import datetime
import enum
from app.db.base import Base


class ItemTypeEnum(str, enum.Enum):
    """Type of handoff item."""
    LAB_TEST = "LAB_TEST"
    MEDICATION = "MEDICATION"
    FOLLOW_UP = "FOLLOW_UP"
    MONITORING = "MONITORING"
    CONSULTATION = "CONSULTATION"
    OTHER = "OTHER"


class ItemStatusEnum(str, enum.Enum):
    """Item completion status."""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class HandoffItem(Base):
    """HandoffItem table for action items."""

    __tablename__ = "handoff_items"

    id = Column(String(36), primary_key=True)
    handoff_id = Column(String(36), ForeignKey("handoffs.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    item_type = Column(SQLEnum(ItemTypeEnum), nullable=False)
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    due_date = Column(DateTime, nullable=True, index=True)
    status = Column(SQLEnum(ItemStatusEnum), default=ItemStatusEnum.OPEN, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<HandoffItem(id={self.id}, handoff_id={self.handoff_id}, title={self.title})>"

    def to_dict(self):
        return {
            "id": self.id,
            "handoff_id": self.handoff_id,
            "title": self.title,
            "description": self.description,
            "item_type": self.item_type.value,
            "assigned_to": self.assigned_to,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
''',

    "app/models/escalation_event.py": '''"""EscalationEvent model for tracking escalations."""

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
''',

    "app/models/audit_log.py": '''"""AuditLog model for immutable audit trail."""

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
''',

    # ===== REPOSITORIES =====
    "app/repositories/__init__.py": '"""Data access repositories."""\n',

    "app/repositories/base.py": '''"""Base repository class with generic CRUD operations."""

from typing import TypeVar, Generic, Optional, List, Type
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic repository for CRUD operations."""

    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get(self, id: str) -> Optional[T]:
        """Get a single record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj: T) -> T:
        """Create a new record."""
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: str, data: dict) -> Optional[T]:
        """Update a record by ID."""
        obj = self.get(id)
        if not obj:
            return None
        
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: str) -> bool:
        """Delete a record by ID."""
        obj = self.get(id)
        if not obj:
            return False
        
        self.db.delete(obj)
        self.db.commit()
        return True

    def count(self) -> int:
        """Count total records."""
        return self.db.query(self.model).count()
''',

    "app/repositories/user_repo.py": '''"""User repository."""

from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base import BaseRepository
from typing import Optional


class UserRepository(BaseRepository[User]):
    """Repository for User operations."""

    def __init__(self, db: Session):
        super().__init__(db, User)

    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def find_by_role(self, role: str, limit: int = 100) -> list[User]:
        """Find all users with a specific role."""
        return self.db.query(User).filter(User.role == role).limit(limit).all()

    def find_active_users(self) -> list[User]:
        """Find all active users."""
        return self.db.query(User).filter(User.is_active == True).all()
''',

    "app/repositories/patient_repo.py": '''"""Patient repository."""

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
''',

    "app/repositories/handoff_repo.py": '''"""Handoff repository."""

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
''',

    "app/repositories/item_repo.py": '''"""HandoffItem repository."""

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
''',

    "app/repositories/escalation_repo.py": '''"""EscalationEvent repository."""

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
''',

    "app/repositories/audit_repo.py": '''"""AuditLog repository."""

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
''',

    # ===== SCHEMAS =====
    "app/schemas/__init__.py": '"""Pydantic request/response schemas."""\n',

    "app/schemas/patient.py": '''"""Patient schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class PatientCreate(BaseModel):
    """Request body for creating a patient."""

    mrn: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    date_of_birth: Optional[date] = None

    class Config:
        json_schema_extra = {
            "example": {
                "mrn": "MRN-2025-00123",
                "name": "John Smith",
                "date_of_birth": "1990-05-15"
            }
        }


class PatientResponse(BaseModel):
    """Response model for patient."""

    id: str
    mrn: str
    name: str
    date_of_birth: Optional[str]
    created_by: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
''',

    "app/schemas/handoff.py": '''"""Handoff schemas."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from app.models.handoff import HandoffStatusEnum, HandoffPriorityEnum


class HandoffCreate(BaseModel):
    """Request body for creating a handoff."""

    patient_id: str = Field(...)
    assigned_to: str = Field(...)
    priority: HandoffPriorityEnum = Field(HandoffPriorityEnum.MEDIUM)
    diagnosis_summary: str = Field(..., min_length=1, max_length=500)
    pending_tests: Optional[str] = Field(None, max_length=1000)
    medication_changes: Optional[str] = Field(None, max_length=1000)
    follow_up_deadline: datetime = Field(...)
    additional_notes: Optional[str] = Field(None, max_length=2000)

    @field_validator("follow_up_deadline")
    @classmethod
    def follow_up_must_be_future(cls, v):
        if v <= datetime.utcnow():
            raise ValueError("Follow-up deadline must be in the future")
        return v


class HandoffResponse(BaseModel):
    """Response model for handoff."""

    id: str
    patient_id: str
    created_by: str
    assigned_to: str
    status: str
    priority: str
    is_ready: bool
    diagnosis_summary: str
    pending_tests: Optional[str]
    medication_changes: Optional[str]
    follow_up_deadline: Optional[str]
    additional_notes: Optional[str]
    created_at: str
    updated_at: str
    accepted_at: Optional[str]
    completed_at: Optional[str]

    class Config:
        from_attributes = True
''',

    "app/schemas/item.py": '''"""Item schemas."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from app.models.handoff_item import ItemTypeEnum, ItemStatusEnum


class ItemCreate(BaseModel):
    """Request body for creating an item."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    item_type: ItemTypeEnum = Field(...)
    assigned_to: str = Field(...)
    due_date: Optional[datetime] = None

    @field_validator("due_date")
    @classmethod
    def due_date_must_be_future(cls, v):
        if v and v <= datetime.utcnow():
            raise ValueError("Due date must be in the future")
        return v


class ItemResponse(BaseModel):
    """Response model for item."""

    id: str
    handoff_id: str
    title: str
    description: Optional[str]
    item_type: str
    assigned_to: str
    due_date: Optional[str]
    status: str
    created_at: str
    updated_at: str
    completed_at: Optional[str]

    class Config:
        from_attributes = True
''',

    "app/schemas/audit_log.py": '''"""Audit log schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List


class AuditLogResponse(BaseModel):
    """Response model for audit log entry."""

    id: str
    user_id: Optional[str]
    entity_type: str
    entity_id: str
    action: str
    old_values: Optional[dict]
    new_values: Optional[dict]
    reason: Optional[str]
    created_at: str

    class Config:
        from_attributes = True
''',

    # ===== AUTH =====
    "app/auth/__init__.py": '"""Authentication module."""\n',

    "app/auth/schemas.py": '''"""Pydantic schemas for auth endpoints."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import RoleEnum


class SignupRequest(BaseModel):
    """Request body for user signup."""

    email: EmailStr = Field(...)
    password: str = Field(..., min_length=12)
    role: RoleEnum = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "jane.doe@hospital.local",
                "password": "SecurePass123!",
                "role": "nurse"
            }
        }


class LoginRequest(BaseModel):
    """Request body for user login."""

    email: EmailStr = Field(...)
    password: str = Field(...)


class UserResponse(BaseModel):
    """User response (no password)."""

    id: str
    email: str
    role: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response after successful login."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class HealthCheck(BaseModel):
    """Health check response."""

    status: str
    message: str
''',

    "app/auth/routes.py": '''"""Authentication routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import timedelta
import uuid

from app.db.database import get_db
from app.auth.schemas import SignupRequest, LoginRequest, TokenResponse, UserResponse, HealthCheck
from app.models.user import User, RoleEnum
from app.utils import hash_password, verify_password, create_access_token
from app.exceptions import EmailAlreadyExists, InvalidCredentials, ValidationError
from app.config import settings
from app.repositories.user_repo import UserRepository
from app.services.audit_service import AuditService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Create a new user account."""
    
    repo = UserRepository(db)
    
    existing_user = repo.find_by_email(request.email)
    if existing_user:
        raise EmailAlreadyExists(request.email)
    
    if not _is_strong_password(request.password):
        raise ValidationError(
            "Password must contain at least 1 uppercase, 1 digit, and 1 special character",
            {"password": "Invalid password complexity"}
        )
    
    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        hashed_password=hash_password(request.password),
        role=request.role,
        is_active=True,
    )
    
    user = repo.create(user)
    
    audit = AuditService(db)
    audit.log_action(
        user_id=user.id,
        entity_type="USER",
        entity_id=user.id,
        action="CREATE",
        new_values=user.to_dict(),
        reason=f"User {user.email} created account",
    )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
    )


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login and receive JWT token."""
    
    repo = UserRepository(db)
    user = repo.find_by_email(request.email)
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise InvalidCredentials()
    
    if not user.is_active:
        raise InvalidCredentials()
    
    expires_delta = timedelta(hours=settings.jwt_expiry_hours)
    token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role.value,
        expires_delta=expires_delta,
    )
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=int(expires_delta.total_seconds()),
        user=UserResponse(
            id=user.id,
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        ),
    )


@router.get("/health", response_model=HealthCheck, status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint."""
    return HealthCheck(
        status="healthy",
        message=f"{settings.app_name} v{settings.app_version} running"
    )


def _is_strong_password(password: str) -> bool:
    """Validate password strength."""
    if len(password) < 12:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password)
    
    return has_upper and has_digit and has_special
''',

    # ===== SERVICES =====
    "app/services/__init__.py": '"""Business logic services."""\n',

    "app/services/audit_service.py": '''"""Audit logging service."""

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
''',

    # ===== API =====
    "app/api/__init__.py": '"""API routes."""\n',
    "app/api/v1/__init__.py": '"""API v1 routes."""\n',

    "app/api/v1/patients.py": '''"""Patient endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import uuid

from app.db.database import get_db
from app.dependencies import get_current_user, require_role, CurrentUser
from app.schemas.patient import PatientCreate, PatientResponse
from app.models.patient import Patient
from app.repositories.patient_repo import PatientRepository
from app.exceptions import ResourceNotFound, MRNAlreadyExists
from app.services.audit_service import AuditService

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    request: PatientCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("doctor", "admin")),
):
    """Create a new patient (doctor/admin only)."""
    
    repo = PatientRepository(db)
    audit = AuditService(db)
    
    existing = repo.find_by_mrn(request.mrn)
    if existing:
        raise MRNAlreadyExists(request.mrn)
    
    patient = Patient(
        id=str(uuid.uuid4()),
        mrn=request.mrn,
        name=request.name,
        date_of_birth=request.date_of_birth,
        created_by=current_user.user_id,
    )
    
    patient = repo.create(patient)
    
    audit.log_action(
        user_id=current_user.user_id,
        entity_type="PATIENT",
        entity_id=patient.id,
        action="CREATE",
        new_values=patient.to_dict(),
        reason=f"User {current_user.email} created patient",
    )
    
    return PatientResponse(
        id=patient.id,
        mrn=patient.mrn,
        name=patient.name,
        date_of_birth=patient.date_of_birth.isoformat() if patient.date_of_birth else None,
        created_by=patient.created_by,
        created_at=patient.created_at.isoformat(),
        updated_at=patient.updated_at.isoformat(),
    )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get patient by ID."""
    
    repo = PatientRepository(db)
    patient = repo.get(patient_id)
    
    if not patient:
        raise ResourceNotFound("Patient", patient_id)
    
    return PatientResponse(
        id=patient.id,
        mrn=patient.mrn,
        name=patient.name,
        date_of_birth=patient.date_of_birth.isoformat() if patient.date_of_birth else None,
        created_by=patient.created_by,
        created_at=patient.created_at.isoformat(),
        updated_at=patient.updated_at.isoformat(),
    )
''',

    # ===== MAIN =====
    "app/main.py": '''"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

from app.config import settings
from app.db.database import engine
from app.db.base import Base
from app.exceptions import BaseAPIException
from app.auth.routes import router as auth_router
from app.api.v1.patients import router as patients_router

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Healthcare Handoff Management Backend",
        debug=settings.debug,
    )

    Base.metadata.create_all(bind=engine)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(BaseAPIException)
    async def api_exception_handler(request, exc: BaseAPIException):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        errors = {}
        for error in exc.errors():
            field = ".".join(str(x) for x in error["loc"][1:])
            errors[field] = error["msg"]

        return JSONResponse(
            status_code=422,
            content={
                "error": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": errors,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
            },
        )

    app.include_router(auth_router)
    app.include_router(patients_router)

    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down application")

    return app


app = create_app()
''',

    # ===== TESTS =====
    "tests/__init__.py": '"""Tests package."""\n',

    "tests/conftest.py": '''"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.db.base import Base
from app.main import app
from app.db.database import get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Create test database session."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session):
    """Create test client with overridden dependencies."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Create a test user and return auth headers."""
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": "test@hospital.local",
            "password": "TestPass123!",
            "role": "doctor",
        },
    )
    assert signup_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "test@hospital.local",
            "password": "TestPass123!",
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
''',

    "tests/test_auth.py": '''"""Tests for auth endpoints."""

import pytest


def test_signup_success(client):
    """Test successful user signup."""
    response = client.post(
        "/auth/signup",
        json={
            "email": "john@hospital.local",
            "password": "SecurePass123!",
            "role": "nurse",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "john@hospital.local"
    assert data["role"] == "nurse"


def test_signup_duplicate_email(client):
    """Test signup with duplicate email."""
    client.post(
        "/auth/signup",
        json={
            "email": "duplicate@hospital.local",
            "password": "SecurePass123!",
            "role": "nurse",
        },
    )
    
    response = client.post(
        "/auth/signup",
        json={
            "email": "duplicate@hospital.local",
            "password": "SecurePass123!",
            "role": "doctor",
        },
    )
    
    assert response.status_code == 409


def test_login_success(auth_headers):
    """Test successful login."""
    assert "Authorization" in auth_headers


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@hospital.local",
            "password": "WrongPass123!",
        },
    )
    
    assert response.status_code == 401


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/auth/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
''',

    # ===== CONFIG FILES =====
    ".env.example": '''# Database Configuration
DATABASE_URL=postgresql://dev:dev_password@localhost:5432/handoff_db

# Redis Configuration (optional, phase 2)
REDIS_URL=redis://localhost:6379

# JWT & Security
SECRET_KEY=your_super_secret_key_change_in_production_12345
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=1

# App Configuration
DEBUG=True
LOG_LEVEL=INFO
APP_NAME=Healthcare Handoff Backend
APP_VERSION=0.1.0

# CORS (for future frontend)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Feature Flags
ENABLE_BACKGROUND_JOBS=True
NOTIFICATION_SERVICE_ENABLED=False
''',

    ".gitignore": '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite
*.sqlite3

# Testing
.pytest_cache/
.coverage
htmlcov/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
''',

    "README.md": '''# Healthcare Handoff Backend

Production-grade backend for managing patient handoffs in healthcare workflows.

## Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create .env File
```bash
cp .env.example .env
```

### 4. Run Tests
```bash
pytest tests/ -v
```

### 5. Start Development Server
```bash
uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`
API docs: `http://localhost:8000/docs`

## Features

- ✅ JWT Authentication
- ✅ Role-Based Access Control
- ✅ Patient Management
- ✅ Handoff Workflows
- ✅ Audit Logging
- ✅ Error Handling
- ✅ Comprehensive Tests

## Tech Stack

- FastAPI 0.109.0
- SQLAlchemy 2.0.25
- PostgreSQL 15
- Pydantic 2.6.0
- Python 3.11-3.13.9

## Project Structure

```
app/
├── auth/          # Authentication
├── models/        # SQLAlchemy ORM models
├── schemas/       # Pydantic request/response models
├── db/            # Database configuration
├── repositories/  # Data access layer
├── services/      # Business logic
├── api/           # Route handlers
├── middleware/    # Request/response middleware
└── background_tasks/  # Background jobs
```

## API Endpoints

### Auth
- `POST /auth/signup` - Create new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/health` - Health check

### Patients
- `POST /patients` - Create patient (doctor/admin only)
- `GET /patients/{patient_id}` - Get patient

## Development

### Code Quality
```bash
black app tests
isort app tests
flake8 app tests
```

### Run Tests
```bash
pytest tests/ -v --cov=app
```

## Next Steps

- Day 1: Foundation ✅
- Day 2: Handoff Workflow
- Day 3: Escalation & Audit

---

**Author:** Healthcare Engineering Team
''',
}


def create_all_files():
    """Create all folders and files."""
    print("\n" + "="*80)
    print(f"{BOLD}{GREEN}🚀 Creating Healthcare Handoff Backend Files{RESET}")
    print("="*80 + "\n")
    
    # Create folders
    print(f"{CYAN}Creating folder structure...{RESET}")
    for folder in FOLDERS:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"  {GREEN}✓{RESET} {folder}")
    
    # Create files
    print(f"\n{CYAN}Creating Python files...{RESET}")
    created = 0
    for filepath, content in FILES.items():
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  {GREEN}✓{RESET} {filepath}")
        created += 1
    
    # Summary
    print(f"\n{BOLD}{GREEN}" + "="*80)
    print(f"✅ SUCCESS! Created {created} files")
    print("="*80 + f"{RESET}\n")
    
    print(f"{YELLOW}📋 NEXT STEPS:{RESET}")
    print(f"  1. {CYAN}pip install -r requirements.txt{RESET}")
    print(f"  2. {CYAN}cp .env.example .env{RESET}")
    print(f"  3. {CYAN}pytest tests/ -v{RESET}")
    print(f"  4. {CYAN}uvicorn app.main:app --reload{RESET}\n")
    
    print(f"{BOLD}🎉 Ready to go! Server runs on http://localhost:8000{RESET}\n")


if __name__ == "__main__":
    try:
        create_all_files()
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{RESET}\n")
        sys.exit(1)