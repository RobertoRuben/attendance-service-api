from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class GradeResponseDTO(BaseModel):
    """
    DTO de respuesta para Grade.

    Atributos:
        id: Identificador único del grado.
        grade_name: Nombre del grado.
        created_at: Fecha y hora de creación (ISO 8601).
        updated_at: Fecha y hora de última actualización (ISO 8601) o None.
    """

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: int = Field(
        ...,
        description="Identificador único del grado.",
        example=1,
    )
    grade_name: str = Field(
        ...,
        description="Nombre del grado.",
        example="1°",
    )
    created_at: datetime = Field(
        ...,
        description="Fecha y hora de creación (ISO 8601).",
        example="2025-08-30T12:34:56Z",
    )
    updated_at: datetime | None = Field(
        default=None,
        description="Fecha y hora de última actualización (ISO 8601) o None.",
        example="2025-08-30T12:34:56Z",
    )
