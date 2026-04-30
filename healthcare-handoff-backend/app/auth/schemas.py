"""Pydantic schemas for auth endpoints."""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from app.models.user import RoleEnum


class SignupRequest(BaseModel):
    """Request body for user signup."""

    email: EmailStr = Field(...)
    password: str = Field(..., min_length=12)
    role: RoleEnum = Field(...)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "jane.doe@example.com",
            "password": "SecurePass123!",
            "role": "nurse"
        }
    })


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

    model_config = ConfigDict(from_attributes=True)


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