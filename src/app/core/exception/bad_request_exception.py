from dataclasses import dataclass, field

from .constants import ErrorTitles, ErrorTypes
from .model import BaseHTTPException


@dataclass
class BadRequestException(BaseHTTPException):
    """
    Custom exception for bad request errors.
    Used when the client sends invalid or malformed data.
    """

    message: str = field(
        default="The request contains invalid parameters.",
        metadata={
            "description": "Human-readable error message for bad request",
            "example": "Invalid email format provided",
        },
    )
    details: str = field(
        default=None,
        metadata={
            "description": "Additional details about the validation error",
            "example": "Field 'email' must be a valid email address",
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
        default=ErrorTypes.BAD_REQUEST,
        metadata={
            "description": "URI that identifies the problem type",
            "example": ErrorTypes.BAD_REQUEST,
        },
    )
    title: str = field(
        default=ErrorTitles.BAD_REQUEST,
        metadata={
            "description": "Short summary of the problem type",
            "example": ErrorTitles.BAD_REQUEST,
        },
    )
    code: int = field(
        default=400,
        metadata={"description": "HTTP status code for bad request", "example": 400},
    )
