from datetime import datetime
from sqlmodel import (
    Relationship,
    SQLModel,
    Field,
    Column,
    ForeignKey,
    BIGINT,
    TEXT,
    BOOLEAN,
    DateTime,
    text,
)
from pgvector.sqlalchemy import Vector
from src.app.domain.students.enum import PhotoQuality
from src.app.domain.students.model.student import Student


class StudentPhoto(SQLModel, table=True):
    __tablename__ = "students_photos"

    id: int | None = Field(default=None, sa_column=Column(BIGINT, primary_key=True))
    student_id: int = Field(
        sa_column=Column(
            BIGINT,
            ForeignKey(
                "students.id", name="fk_student_photos_student", ondelete="CASCADE"
            ),
            nullable=False,
            index=True,
        ),
    )
    file_path: str | None = Field(default=None, sa_column=Column(TEXT, nullable=True))
    file_name: str | None = Field(default=None, sa_column=Column(TEXT, nullable=True))
    photo_quality: PhotoQuality | None = Field(default=None)
    face_detected: bool = Field(
        default=False, sa_column=Column(BOOLEAN, nullable=False)
    )
    face_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    embedding_model: str | None = Field(
        default=None, sa_column=Column(TEXT, nullable=True)
    )
    face_embedding: list[float] | None = Field(
        default=None,
        sa_column=Column(Vector(4096), nullable=True),
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

    student: "Student" = Relationship(back_populates="photos")
