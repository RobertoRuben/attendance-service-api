from dataclasses import dataclass, field

from .constants import ErrorTitles, ErrorTypes
from .model import BaseHTTPException


@dataclass
class NotFoundException(BaseHTTPException):
    """
    Custom exception for not found errors.
    Used when a resource is not found in the database.
    """

    message: str = field(
        default="The requested resource was not found.",
        metadata={
            "description": "Human-readable error message for not found resources",
            "example": "User with ID 123 not found",
        },
    )
    details: str = field(
        default=None,
        metadata={
            "description": "Additional details about the missing resource",
            "example": "No user exists with the specified identifier",
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
        default=ErrorTypes.NOT_FOUND,
        metadata={
            "description": "URI that identifies the problem type",
            "example": ErrorTypes.NOT_FOUND,
        },
    )
    title: str = field(
        default=ErrorTitles.NOT_FOUND,
        metadata={
            "description": "Short summary of the problem type",
            "example": ErrorTitles.NOT_FOUND,
        },
    )
    code: int = field(
        default=404,
        metadata={
            "description": "HTTP status code for not found errors",
            "example": 404,
        },
    )
