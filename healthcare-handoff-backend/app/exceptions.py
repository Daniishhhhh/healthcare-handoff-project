"""Custom exception classes for API responses."""

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
