from dataclasses import dataclass, field

from .constants import ErrorTitles, ErrorTypes
from .model import BaseHTTPException


@dataclass
class UnauthorizedException(BaseHTTPException):
    """
    Custom exception for unauthorized access errors.
    Used when authentication credentials are missing or invalid.
    """

    message: str = field(
        default="Authentication credentials are missing or invalid.",
        metadata={
            "description": "Human-readable error message for authentication errors",
            "example": "Invalid or expired authentication token",
        },
    )
    details: str = field(
        default=None,
        metadata={
            "description": "Additional details about the authentication error",
            "example": "Token expired at 2025-08-29T09:30:00",
        },
    )
    instance: str = field(
        default=None,
        metadata={
            "description": "URI that identifies the specific occurrence",
            "example": "/api/v1/protected-resource",
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
        default=ErrorTypes.INVALID_TOKEN,
        metadata={
            "description": "URI that identifies the problem type",
            "example": ErrorTypes.INVALID_TOKEN,
        },
    )
    title: str = field(
        default=ErrorTitles.UNAUTHORIZED,
        metadata={
            "description": "Short summary of the problem type",
            "example": ErrorTitles.UNAUTHORIZED,
        },
    )
    headers: dict = field(
        default=None,
        metadata={
            "description": "Additional headers for unauthorized response",
            "example": {"WWW-Authenticate": 'Bearer realm="api"'},
        },
    )
    code: int = field(
        default=401,
        metadata={
            "description": "HTTP status code for unauthorized access",
            "example": 401,
        },
    )
