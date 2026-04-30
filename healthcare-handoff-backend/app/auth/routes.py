"""Authentication routes."""

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
