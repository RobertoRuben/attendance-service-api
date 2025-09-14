from pydantic import BaseModel, ConfigDict, Field, field_validator
import re


class StudentRequestDTO(BaseModel):
    """Data Transfer Object for Student creation and update requests.

    This DTO validates and sanitizes student data from client requests
    before processing. It enforces business rules and data integrity
    constraints for the Peruvian educational system.

    The validation includes:
    - DNI format and pattern validation (8 digits, no obvious sequences)
    - Name normalization and character validation (Spanish characters)
    - Grade and section range validation
    - Automatic whitespace cleanup and capitalization

    Attributes:
        dni: National identification number. Must be exactly 8 digits.
            Automatically cleaned of non-digit characters.
        names: Student's first names. Normalized to title case with
            single spaces between words.
        paternal_surname: Father's family name. Normalized and validated
            for valid Spanish characters.
        maternal_surname: Mother's family name. Normalized and validated
            for valid Spanish characters.
        grade_id: Grade level identifier. Must be between 1 and 11.
        section_id: Section identifier within the grade. Must be between 1 and 10.

    Validation Rules:
        - DNI cannot be obvious patterns (00000000, 12345678, etc.)
        - Names can only contain letters, spaces, apostrophes, and hyphens
        - All text fields are automatically stripped and normalized
        - Grade and section IDs must be positive and within valid ranges

    Example:
        >>> student_data = StudentRequestDTO(
        ...     dni="  1234-5678  ",  # Will be cleaned to "12345678"
        ...     names="  juan   carlos  ",  # Will become "Juan Carlos"
        ...     paternal_surname="garcía",  # Will become "García"
        ...     maternal_surname="lópez",   # Will become "López"
        ...     grade_id=5,
        ...     section_id=2
        ... )

    Raises:
        ValueError: When DNI contains invalid patterns or names contain
            invalid characters.
        ValidationError: When field constraints are not met.
    """

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
        """Clean DNI by removing non-digit characters.

        Args:
            v: The DNI value to clean.

        Returns:
            str: DNI with only digit characters.
        """
        if isinstance(v, str):
            return re.sub(r"[^\d]", "", v)
        return v

    @field_validator("names", "paternal_surname", "maternal_surname", mode="before")
    @classmethod
    def normalize_names(cls, v) -> str:
        """Normalize whitespace and capitalize names.

        Removes extra whitespace and applies title case formatting
        to ensure consistent name storage.

        Args:
            v: The name string to normalize.

        Returns:
            str: Normalized name with proper capitalization.
        """
        if isinstance(v, str):
            # Normalizar espacios múltiples y aplicar capitalización
            normalized = re.sub(r"\s+", " ", v.strip()).title()
            return normalized
        return v

    @field_validator("dni", mode="after")
    @classmethod
    def validate_dni_patterns(cls, v: str) -> str:
        """Validate DNI against invalid patterns.

        Rejects DNIs that follow obvious patterns like sequential
        numbers or repeated digits, which are commonly used as
        test data or invalid identifiers.

        Args:
            v: The DNI string to validate.

        Returns:
            str: The validated DNI.

        Raises:
            ValueError: If DNI matches an invalid pattern.
        """
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
        """Validate that names contain only valid characters.

        Ensures names only contain letters (including Spanish accented
        characters), spaces, apostrophes, and hyphens. This prevents
        injection attacks and maintains data consistency.

        Args:
            v: The name string to validate.

        Returns:
            str: The validated name.

        Raises:
            ValueError: If name contains invalid characters.
        """
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s'-]+$", v):
            raise ValueError("Solo se permiten letras, espacios, apostrofes y guiones")

        return v
