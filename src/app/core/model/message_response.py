from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """
    Message response model for consistent response format.
    """

    message: str = Field(..., description="Human-readable message")
    success: bool = Field(..., description="Indicates if the operation was successful")
    details: str | None = Field(
        None, description="Additional details about the message"
    )
    status_code: int = Field(..., description="HTTP status code")
