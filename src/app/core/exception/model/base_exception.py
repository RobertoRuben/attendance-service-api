from dataclasses import dataclass, field
from datetime import datetime

from fastapi import HTTPException

from .error_detail import ErrorDetail


@dataclass
class BaseHTTPException(HTTPException):
    """
    Base class for all custom HTTP exceptions.
    Provides consistent error formatting using ErrorDetail.
    """

    type_: str = field(
        default=None,
        metadata={
            "description": "URI that identifies the problem type",
            "example": "https://example.com/problems/server-error",
        },
    )
    code: int = field(
        default=500, metadata={"description": "HTTP status code", "example": 500}
    )
    message: str = field(
        default="An unexpected error occurred",
        metadata={
            "description": "Human-readable error message",
            "example": "An unexpected error occurred while processing your request",
        },
    )
    details: str = field(
        default=None,
        metadata={
            "description": "Additional details about the error",
            "example": "Stack trace or additional context information",
        },
    )
    instance: str = field(
        default=None,
        metadata={
            "description": "URI that identifies the specific occurrence of the problem",
            "example": "/api/v1/users/123",
        },
    )
    time: str = field(
        default=None,
        metadata={
            "description": "Timestamp when the error occurred, defaults to current time",
            "example": "2025-08-29T10:30:00",
        },
    )
    headers: dict = field(
        default=None,
        metadata={
            "description": "HTTP headers to include in the response",
            "example": {"WWW-Authenticate": "Bearer"},
        },
    )
    title: str = field(
        default="Server Error",
        metadata={
            "description": "A short, human-readable summary of the problem type",
            "example": "Internal Server Error",
        },
    )

    def __post_init__(self):
        """
        Initialize the HTTPException after dataclass initialization.
        """
        error = ErrorDetail(
            type=self.type_,
            title=self.title,
            status=self.code,
            detail=self.message,
            details=self.details,
            instance=self.instance,
            timestamp=self.time or datetime.now().isoformat(),
        )

        super().__init__(
            status_code=self.code, detail=error.model_dump(), headers=self.headers
        )
