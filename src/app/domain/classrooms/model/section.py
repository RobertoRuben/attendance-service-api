from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import (
    SQLModel,
    Field,
    Column,
    BIGINT,
    TEXT,
    DateTime,
    text,
    CheckConstraint,
    Relationship,
)

if TYPE_CHECKING:
    from src.app.domain.students.model import Student


class Section(SQLModel, table=True):
    """Represents a section within a grade in the educational system.

    This model stores section information including the section name and
    audit timestamps. Sections are used to divide students within the same
    grade into different classroom groups.

    The model enforces data integrity through constraints:
    - Section names cannot be empty or contain only whitespace
    - Section names must be unique across the system

    Attributes:
        id: Unique identifier for the section. Auto-generated primary key.
        section_name: Name of the section (e.g., "A", "B", "Blue", "Red").
            Must be unique and non-empty.
        created_at: Timestamp when the record was created. Set automatically.
        updated_at: Timestamp of the last record update. Null if never updated.
        students: List of students assigned to this section.

    Table Constraints:
        - Section name must not be empty after trimming whitespace
        - Section name must be unique across all sections

    Example:
        >>> section = Section(section_name="Section A")
        >>> # The section will be automatically assigned an ID and creation timestamp
    """

    __tablename__ = "sections"
    __table_args__ = (
        CheckConstraint(
            "LENGTH(TRIM(section_name)) > 0", name="check_section_name_not_empty"
        ),
    )

    id: int | None = Field(default=None, sa_column=Column(BIGINT, primary_key=True))
    section_name: str = Field(sa_column=Column(TEXT, nullable=False, unique=True))
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
    )

    students: list["Student"] = Relationship(back_populates="section")
