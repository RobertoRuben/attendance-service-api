from pydantic import BaseModel, Field, ConfigDict


class SectionRequestDTO(BaseModel):
    """
    Data transfer object for section creation requests.

    This DTO is used to validate and transfer section data when creating
    a new section in the classroom management system.

    Attributes:
        section_name (str): The name of the section. Must be a non-empty string.
    """
    
    model_config = ConfigDict(extra="forbid")
    
    section_name: str = Field(
        ...,
        description="The name of the section",
        examples=["A", "B", "C", "D"],
        min_length=1,
        max_length=10,
    )