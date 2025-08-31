from datetime import datetime
from sqlmodel import (
    Field,
    SQLModel,
    Column,
    BIGINT,
    TEXT,
    CheckConstraint,
    DateTime,
    text,
)


class Grade(SQLModel, table=True):
    """Represents a grade in the system.

    :ivar id: The unique identifier for the grade.
    :ivar grade_name: The name of the grade.
    :ivar created_at: The timestamp when the grade was created.
    :ivar updated_at: The timestamp when the grade was last updated.
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
