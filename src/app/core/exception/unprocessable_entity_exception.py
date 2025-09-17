from dataclasses import dataclass, field

from .constants import ErrorTitles, ErrorTypes
from .model import BaseHTTPException


@dataclass
class UnprocessableEntityException(BaseHTTPException):
    """
    Custom exception for unprocessable entity errors (422).
    Used when the request is well-formed but semantically incorrect.
    Typically used for validation errors.
    """

    message: str = field(
        default="The request contains validation errors.",
        metadata={
            "description": "Human-readable error message for validation errors",
            "example": "The submitted data contains validation errors",
        },
    )
    details: str = field(
        default=None,
        metadata={
            "description": "Additional details about the validation errors",
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
        default=ErrorTypes.VALIDATION_ERROR,
        metadata={
            "description": "URI that identifies the problem type",
            "example": ErrorTypes.VALIDATION_ERROR,
        },
    )
    title: str = field(
        default=ErrorTitles.UNPROCESSABLE_ENTITY,
        metadata={
            "description": "Short summary of the problem type",
            "example": ErrorTitles.UNPROCESSABLE_ENTITY,
        },
    )
    code: int = field(
        default=422,
        metadata={
            "description": "HTTP status code for unprocessable entity",
            "example": 422,
        },
    )
