from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import (
    SQLModel,
    Field,
    Column,
    BIGINT,
    VARCHAR,
    TEXT,
    DateTime,
    CheckConstraint,
    Relationship,
    ForeignKey,
    text,
)

if TYPE_CHECKING:
    from src.app.domain.classrooms.model import Section, Grade


class Student(SQLModel, table=True):
    """Represents a student in the educational system.

    This model stores student information including personal details,
    academic placement (grade and section), and audit timestamps.

    The model enforces data integrity through constraints:
    - DNI must be exactly 8 digits
    - Each student must have a unique grade-section combination
    - Foreign key relationships ensure referential integrity

    Attributes:
        id: Unique identifier for the student. Auto-generated primary key.
        dni: National identification number. Must be exactly 8 digits.
        names: Student's first names.
        paternal_surname: Student's father's family name.
        maternal_surname: Student's mother's family name.
        grade_id: Foreign key reference to the student's grade.
        section_id: Foreign key reference to the student's section.
        created_at: Timestamp when the record was created. Set automatically.
        updated_at: Timestamp of the last record update. Null if never updated.
        grade: Relationship to the Grade model.
        section: Relationship to the Section model.

    Table Constraints:
        - DNI must be 8 numeric characters
        - Unique combination of grade_id and section_id per student
        - Foreign keys prevent deletion of referenced grades/sections

    Example:
        >>> student = Student(
        ...     dni="12345678",
        ...     names="María José",
        ...     paternal_surname="García",
        ...     maternal_surname="López",
        ...     grade_id=1,
        ...     section_id=2
        ... )
    """

    __tablename__ = "students"
    __table_args__ = (
        CheckConstraint(
            "char_length(dni) = 8 AND dni ~ '^[0-9]{8}$'", name="ck_student_dni_8digits"
        ),
    )

    id: int | None = Field(default=None, sa_column=Column(BIGINT, primary_key=True))
    dni: str = Field(
        sa_column=Column(VARCHAR(8), unique=True, index=True, nullable=False)
    )
    names: str = Field(sa_column=Column(TEXT, nullable=False))
    paternal_surname: str = Field(sa_column=Column(TEXT, nullable=False))
    maternal_surname: str = Field(sa_column=Column(TEXT, nullable=False))
    grade_id: int = Field(
        sa_column=Column(
            BIGINT,
            ForeignKey("grades.id", name="fk_students_grade", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    section_id: int = Field(
        sa_column=Column(
            BIGINT,
            ForeignKey("sections.id", name="fk_students_section", ondelete="RESTRICT"),
            nullable=False,
        ),
    )

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

    grade: "Grade" = Relationship(back_populates="students")
    section: "Section" = Relationship(back_populates="students")
