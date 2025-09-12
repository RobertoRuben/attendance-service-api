from pydantic import BaseModel, Field


class RootResponseDTO(BaseModel):
    """
    Data Transfer Object for the root endpoint response.

    Attributes:
        message: A welcome message for the API.
        version: The current version of the application.
        docs: URL to the Swagger UI documentation.
        redoc: URL to the ReDoc documentation.
        scalar: URL to the GraphQL scalar endpoint.
    """

    message: str = Field(
        ...,
        description="A welcome message for the API",
        example="Attendance Service API",
    )
    version: str = Field(
        ..., description="The current version of the application", example="1.0.0"
    )
    docs: str = Field(
        ...,
        description="URL to the Swagger UI documentation",
        example="http://localhost:8000/api/v1/docs",
    )
    redoc: str = Field(
        ...,
        description="URL to the ReDoc documentation",
        example="http://localhost:8000/api/v1/redoc",
    )
    scalar: str = Field(
        ...,
        description="URL to the GraphQL scalar endpoint",
        example="http://localhost:8000/api/v1/scalar",
    )
