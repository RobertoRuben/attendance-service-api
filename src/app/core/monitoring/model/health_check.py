from datetime import datetime
from pydantic import BaseModel, Field


class HealthCheck(BaseModel):
    """
    Represents the health check status of a service.

    Args:
        BaseModel (_type_): _description_
    """

    status: str = Field(
        ...,
        description="The health status of the service",
        examples=["healthy", "unhealthy"],
    )
    timestamp: datetime = Field(
        ..., description="The timestamp of the health check", examples=[datetime.now()]
    )
    service: str = Field(
        ...,
        description="The name of the service being monitored",
        examples=["attendance-service"],
    )
