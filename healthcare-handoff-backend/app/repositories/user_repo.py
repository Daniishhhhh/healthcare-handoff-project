"""User repository."""

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
