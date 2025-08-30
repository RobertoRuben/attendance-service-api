from datetime import datetime
from sqlalchemy import CheckConstraint
from sqlmodel import SQLModel, Field, Column, BIGINT, TEXT, DateTime, text


class Section(SQLModel, table=True):
    """Represents a section in the system.

    :ivar id: The unique identifier for the section.
    :ivar section_name: The name of the section.
    :ivar created_at: The timestamp when the section was created.
    :ivar updated_at: The timestamp when the section was last updated.
    """

    __tablename__ = "sections"
    __table_args__ = CheckConstraint(
        "LENGTH(section_name) > 0", name="check_section_name_not_empty"
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
