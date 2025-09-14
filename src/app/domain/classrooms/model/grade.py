from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import (
    Field,
    SQLModel,
    Column,
    BIGINT,
    TEXT,
    CheckConstraint,
    DateTime,
    text,
    Relationship,
)

if TYPE_CHECKING:
    from src.app.domain.students.model import Student


class Grade(SQLModel, table=True):
    """Represents a grade level in the educational system.

    This model stores grade information including the grade name and
    audit timestamps. It maintains relationships with students enrolled
    in this grade.

    The model enforces data integrity through constraints:
    - Grade names cannot be empty or contain only whitespace
    - Grade names must be unique across the system

    Attributes:
        id: Unique identifier for the grade. Auto-generated primary key.
        grade_name: Name of the grade (e.g., "1st Grade", "Kindergarten").
            Must be unique and non-empty.
        created_at: Timestamp when the record was created. Set automatically.
        updated_at: Timestamp of the last record update. Null if never updated.
        students: List of students enrolled in this grade.

    Table Constraints:
        - Grade name must not be empty after trimming whitespace
        - Grade name must be unique across all grades

    Example:
        >>> grade = Grade(grade_name="5th Grade")
        >>> # The grade will be automatically assigned an ID and creation timestamp
    """

    __tablename__ = "grades"
    __table_args__ = (
        CheckConstraint(
            "LENGTH(TRIM(grade_name)) > 0", name="check_grade_name_not_empty"
        ),
    )

    id: int | None = Field(default=None, sa_column=Column(BIGINT, primary_key=True))
    grade_name: str = Field(sa_column=Column(TEXT, nullable=False, unique=True))
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

    students: list["Student"] = Relationship(back_populates="grade")
