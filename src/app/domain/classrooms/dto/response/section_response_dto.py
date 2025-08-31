from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class SectionResponseDTO(BaseModel):
    """
    Data Transfer Object for Section responses.

    This DTO is used to represent the data returned in Section-related API responses.

    Attributes:
        id: Unique identifier for the section.
        section_name: Name of the section.
        created_at: Timestamp when the section was created.
        updated_at: Timestamp when the section was last updated.
    """

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: int = Field(
        ...,
        description="Identifier of the section",
        examples=[1, 2, 3],
    )
    section_name: str = Field(
        ...,
        description="The name of the section",
        examples=["A", "B", "C", "D"],
    )
    created_at: datetime = Field(
        ...,
        description="The creation timestamp in ISO 8601 format",
        examples=["2023-01-01T00:00:00Z", "2023-01-02T00:00:00Z"],
    )
    updated_at: datetime | None = Field(
        default=None,
        description="The last update timestamp in ISO 8601 format or None",
        example="2023-01-03T00:00:00Z",
    )
