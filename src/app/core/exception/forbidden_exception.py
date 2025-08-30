from dataclasses import dataclass, field

from .constants import ErrorTitles, ErrorTypes
from .model import BaseHTTPException


@dataclass
class ForbiddenException(BaseHTTPException):
    """
    Custom exception for forbidden access errors.
    Used when the client does not have permission to access the requested resource.
    """

    message: str = field(
        default="You don't have permission to access this resource.",
        metadata={
            "description": "Human-readable error message for forbidden access",
            "example": "Access denied: insufficient privileges",
        },
    )
    details: str = field(
        default=None,
        metadata={
            "description": "Additional details about the permission error",
            "example": "Required role: admin, current role: user",
        },
    )
    instance: str = field(
        default=None,
        metadata={
            "description": "URI that identifies the specific occurrence",
            "example": "/api/v1/admin/users",
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
        default=ErrorTypes.MISSING_PERMISSION,
        metadata={
            "description": "URI that identifies the problem type",
            "example": ErrorTypes.MISSING_PERMISSION,
        },
    )
    title: str = field(
        default=ErrorTitles.FORBIDDEN,
        metadata={
            "description": "Short summary of the problem type",
            "example": ErrorTitles.FORBIDDEN,
        },
    )
    headers: dict = field(
        default=None,
        metadata={
            "description": "Additional headers for forbidden response",
            "example": {"WWW-Authenticate": 'Bearer realm="api"'},
        },
    )
    code: int = field(
        default=403,
        metadata={
            "description": "HTTP status code for forbidden access",
            "example": 403,
        },
    )
