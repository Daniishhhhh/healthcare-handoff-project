"""FastAPI dependency injection."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
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


async def get_current_user(credentials = Depends(security)) -> CurrentUser:
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
            raise Unauthorized(f"Requires one of: {', '.join(allowed_roles)}")
        return current_user

    return role_checker