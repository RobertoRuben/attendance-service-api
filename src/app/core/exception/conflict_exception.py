from dataclasses import dataclass, field

from .constants import ErrorTitles, ErrorTypes
from .model import BaseHTTPException


@dataclass
class ConflictException(BaseHTTPException):
    """
    Custom exception for conflict-related errors.
    Used when a resource already exists or there is a conflict in data operations.
    """

    message: str = field(
        default="A conflict occurred with the requested operation.",
        metadata={
            "description": "Human-readable error message for conflicts",
            "example": "User with this email already exists",
        },
    )
    details: str = field(
        default=None,
        metadata={
            "description": "Additional details about the conflict",
            "example": "Email 'user@example.com' is already registered",
        },
    )
    instance: str = field(
        default=None,
        metadata={
            "description": "URI that identifies the specific occurrence",
            "example": "/api/v1/users",
        },
    )
    time: str = field(
        default=None,
        metadata={
            "description": "Timestamp when the error occurred",
            "example": "2025-08-29T10:30:00",
        },
    )
    type_: str = field(
        default=ErrorTypes.CONFLICT,
        metadata={
            "description": "URI that identifies the problem type",
            "example": ErrorTypes.CONFLICT,
        },
    )
    title: str = field(
        default=ErrorTitles.CONFLICT,
        metadata={
            "description": "Short summary of the problem type",
            "example": ErrorTitles.CONFLICT,
        },
    )
    code: int = field(
        default=409,
        metadata={"description": "HTTP status code for conflicts", "example": 409},
    )
