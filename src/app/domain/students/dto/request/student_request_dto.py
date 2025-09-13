from pydantic import BaseModel, ConfigDict, Field, field_validator
import re


class StudentRequestDTO(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    dni: str = Field(
        description="The student's DNI (8-digit unique identifier).",
        min_length=8,
        max_length=8,
        examples=["12345678"],
        pattern=r"^[0-9]{8}$",
    )

    names: str = Field(
        min_length=2,
        max_length=100,
        description="Student's first names",
        examples=["Juan Carlos", "María Elena"],
    )

    paternal_surname: str = Field(
        min_length=2,
        max_length=50,
        description="Student's paternal surname",
        examples=["González", "Rodríguez"],
    )

    maternal_surname: str = Field(
        min_length=2,
        max_length=50,
        description="Student's maternal surname",
        examples=["Pérez", "López"],
    )

    grade_id: int = Field(
        gt=0,
        le=11,
        description="Grade level ID",
        examples=[1, 5, 11],
    )

    section_id: int = Field(
        gt=0,
        le=10,
        description="Section ID within the grade",
        examples=[1, 2, 3],
    )

    @field_validator("dni", mode="before")
    @classmethod
    def clean_dni(cls, v) -> str:
        """Remove non-digit characters from DNI"""
        if isinstance(v, str):
            return re.sub(r"[^\d]", "", v)
        return v

    @field_validator("names", "paternal_surname", "maternal_surname", mode="before")
    @classmethod
    def normalize_names(cls, v) -> str:
        """Normalize whitespace and capitalize names"""
        if isinstance(v, str):
            # Normalizar espacios múltiples y aplicar capitalización
            normalized = re.sub(r"\s+", " ", v.strip()).title()
            return normalized
        return v

    @field_validator("dni", mode="after")
    @classmethod
    def validate_dni_patterns(cls, v: str) -> str:
        """Validate DNI against invalid patterns"""
        invalid_patterns = {
            "00000000",
            "12345678",
            "87654321",
            "11111111",
            "22222222",
            "33333333",
            "44444444",
            "55555555",
            "66666666",
            "77777777",
            "88888888",
            "99999999",
        }

        if v in invalid_patterns:
            raise ValueError("El DNI no puede ser una secuencia obvia o repetitiva")

        return v

    @field_validator("names", "paternal_surname", "maternal_surname", mode="after")
    @classmethod
    def validate_name_characters(cls, v: str) -> str:
        """Validate that names contain only valid characters"""
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s'-]+$", v):
            raise ValueError("Solo se permiten letras, espacios, apostrofes y guiones")

        return v
