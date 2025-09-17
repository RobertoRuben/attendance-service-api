from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class StudentResponseDTO(BaseModel):
    """Data Transfer Object for Student response.

    This DTO is used to structure the data sent back to the client
    when a student record is created, updated, or retrieved.

    Attributes:
        id: Unique identifier of the student. Optional for creation requests.
        dni: National identification number (DNI) of the student.
        names: First names of the student.
        paternal_surname: Father's family name.
        maternal_surname: Mother's family name.
        grade_id: Identifier of the grade the student belongs to.
        grade_name: Descriptive name of the grade. Optional field.
        section_id: Identifier of the section within the grade.
        section_name: Descriptive name of the section. Optional field.
        created_at: Timestamp when the student record was created.
        updated_at: Timestamp of the last update to the record. None if never updated.

    Example:
        >>> student = StudentResponseDTO(
        ...     id=1,
        ...     dni="12345678",
        ...     names="John",
        ...     paternal_surname="Doe",
        ...     maternal_surname="Smith",
        ...     grade_id="1",
        ...     grade_name="1°",
        ...     section_id=1,
        ...     section_name="A",
        ...     created_at=datetime.now()
        ... )
    """

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: int | None = Field(
        default=None,
        description="Identifier of the student",
        examples=[1],
    )
    dni: str = Field(
        description="DNI of the student",
        examples=["12345678"],
    )
    names: str = Field(
        description="Names of the student",
        examples=["John"],
    )
    paternal_surname: str = Field(
        description="Paternal surname of the student",
        examples=["Doe"],
    )
    maternal_surname: str = Field(
        description="Maternal surname of the student",
        examples=["Smith"],
    )
    grade_id: int = Field(
        description="Identifier of the grade",
        examples=["1"],
    )
    grade_name: str | None = Field(
        default=None,
        description="Name of the grade",
        examples=["1°"],
    )
    section_id: int = Field(
        description="Identifier of the section",
        examples=[1],
    )
    section_name: str | None = Field(
        default=None,
        description="Name of the section",
        examples=["A"],
    )
    created_at: datetime = Field(
        description="Creation date of the student record",
        examples=[datetime.now()],
    )
    updated_at: datetime | None = Field(
        default=None,
        description="Last update date of the student record",
        examples=[datetime.now()],
    )
