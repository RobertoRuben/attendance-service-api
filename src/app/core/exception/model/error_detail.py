from pydantic import BaseModel, Field
from datetime import datetime


class ErrorDetail(BaseModel):
    """
    Error detail model for consistent error response format.

    This model is used to provide a standardized response format for errors
    :ivar title: str: The type of the error
    :ivar status: int: HTTP status code
    :ivar detail: str: The error message
    :ivar details: str: Additional details about the error
    :ivar timestamp: str: Timestamp of when the error occurred
    """

    type: str | None = Field(
        default=None, description="URI that identifies the problem type"
    )
    title: str = Field(
        ..., description="A short, human-readable summary of the problem type"
    )
    status: int = Field(..., description="HTTP status code")
    detail: str = Field(
        ...,
        description="A human-readable explanation specific to this occurrence of the problem",
    )
    instance: str | None = Field(
        default=None,
        description="URI that identifies the specific occurrence of the problem",
    )
    timestamp: str = Field(
        datetime.now().isoformat(), description="Timestamp when the error occurred"
    )

    details: str | None = Field(
        default=None, description="Additional details about the error"
    )
