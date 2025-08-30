from dataclasses import dataclass, field

from .constants import ErrorTitles, ErrorTypes
from .model import BaseHTTPException


@dataclass
class InvalidFieldException(BaseHTTPException):
    """
    Custom exception for invalid field errors.
    Used when a field provided doesn't exist in the model.
    """

    message: str = field(
        default="Invalid field provided.",
        metadata={
            "description": "Human-readable error message for invalid fields",
            "example": "Field 'unknownField' is not valid for this model",
        },
    )
    details: str = field(
        default=None,
        metadata={
            "description": "Additional details about the invalid field",
            "example": "Valid fields are: name, email, age, created_at",
        },
    )
    instance: str = field(
        default=None,
        metadata={
            "description": "URI that identifies the specific occurrence",
            "example": "/api/v1/users/filter",
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
        default=ErrorTypes.INVALID_FIELD,
        metadata={
            "description": "URI that identifies the problem type",
            "example": ErrorTypes.INVALID_FIELD,
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
        metadata={
            "description": "HTTP status code for invalid field errors",
            "example": 400,
        },
    )
