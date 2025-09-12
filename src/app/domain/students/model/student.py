from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import UniqueConstraint
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
    """
    Represents a student in the system.

    Args:
        SQLModel (_type_): _description_
        table (bool, optional): _description_. Defaults to True.

    Attributes:
        id (int | None): The unique identifier for the student.
        dni (str): The student's DNI (8-digit unique identifier).
        names (str): The student's first names.
        paternal_surname (str): The student's paternal surname.
        maternal_surname (str): The student's maternal surname.
        grade_id (int): The ID of the grade the student belongs to.
        section_id (int): The ID of the section the student belongs to.
        created_at (datetime | None): The timestamp when the student record was created.
        updated_at (datetime | None): The timestamp when the student record was last updated.
    """

    __tablename__ = "students"
    __table_args__ = (
        CheckConstraint(
            "char_length(dni) = 8 AND dni ~ '^[0-9]{8}$'", name="ck_student_dni_8digits"
        ),
        UniqueConstraint("grade_id", "section_id", name="uq_students_grade_section"),
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
