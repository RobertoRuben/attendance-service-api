from dataclasses import dataclass, field

from .constants import ErrorTitles, ErrorTypes
from .model import BaseHTTPException


@dataclass
class ServerException(BaseHTTPException):
    """
    Custom exception for unexpected server errors.
    Provides a standardized way to handle and report internal server errors.
    """

    message: str = field(
        default="An unexpected server error occurred.",
        metadata={
            "description": "Human-readable error message for server errors",
            "example": "Internal server error while processing request",
        },
    )
    details: str = field(
        default=None,
        metadata={
            "description": "Additional details about the server error",
            "example": "Service temporarily unavailable due to high load",
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
        default=ErrorTypes.SERVER_ERROR,
        metadata={
            "description": "URI that identifies the problem type",
            "example": ErrorTypes.SERVER_ERROR,
        },
    )
    title: str = field(
        default=ErrorTitles.INTERNAL_SERVER_ERROR,
        metadata={
            "description": "Short summary of the problem type",
            "example": ErrorTitles.INTERNAL_SERVER_ERROR,
        },
    )
    code: int = field(
        default=500,
        metadata={"description": "HTTP status code for server errors", "example": 500},
    )
