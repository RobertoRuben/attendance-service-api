from datetime import datetime
from sqlmodel import (
    Relationship,
    SQLModel,
    Field,
    Column,
    BIGINT,
    TEXT,
    BOOLEAN,
    DateTime,
    text,
)
from src.app.domain.students.enum import PhotoQuality
from src.app.domain.students.model.student import Student


class StudentPhoto(SQLModel, table=True):
    __tablename__ = "students_photos"

    id: int | None = Field(default=None, sa_column=Column(BIGINT, primary_key=True))
    student_id: int = Field(
        sa_column=Column(
            BIGINT,
            nullable=False,
            index=True,
            foreign_key="students.id",
        ),
    )
    file_path: str | None = Field(default=None, sa_column=Column(TEXT, nullable=True))
    file_name: str | None = Field(default=None, sa_column=Column(TEXT, nullable=True))
    photo_quality: PhotoQuality | None = Field(default=None)
    face_detected: bool = Field(
        default=False, sa_column=Column(BOOLEAN, nullable=False)
    )
    face_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

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

    student: "Student" = Relationship(back_populates="photos")
