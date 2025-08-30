from dataclasses import dataclass, field

from .constants import ErrorTitles, ErrorTypes
from .model import BaseHTTPException


@dataclass
class DatabaseException(BaseHTTPException):
    """
    Custom exception for database errors.
    Used when an error occurs in the database.
    """

    message: str = field(
        default="An error occurred in the database.",
        metadata={
            "description": "Human-readable error message for database errors",
            "example": "Database connection failed",
        },
    )
    details: str = field(
        default=None,
        metadata={
            "description": "Additional details about the database error",
            "example": "Connection timeout after 30 seconds",
        },
    )
    instance: str = field(
        default=None,
        metadata={
            "description": "URI that identifies the specific occurrence",
            "example": "/api/v1/users/123",
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
        default=ErrorTypes.DATABASE_ERROR,
        metadata={
            "description": "URI that identifies the problem type",
            "example": ErrorTypes.DATABASE_ERROR,
        },
    )
    title: str = field(
        default=ErrorTitles.DATABASE_ERROR,
        metadata={
            "description": "Short summary of the problem type",
            "example": ErrorTitles.DATABASE_ERROR,
        },
    )
    code: int = field(
        default=500,
        metadata={
            "description": "HTTP status code for database errors",
            "example": 500,
        },
    )
