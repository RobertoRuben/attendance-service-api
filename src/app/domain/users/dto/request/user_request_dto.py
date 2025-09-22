from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr
import re

from src.app.domain.users.enum import RoleEnum


class UserRequestDTO(BaseModel):
    """Data Transfer Object for User creation and update requests.

    Validations:
        - dni: cleaned of non-digits and validated (8 digits, no trivial patterns).
        - username: normalized, constrained to allowed characters and length.
        - email: validated by EmailStr.
        - password: minimum length and basic complexity rules.
        - names / paternal_surname / maternal_surname: whitespace normalized,
          title-cased and character-validated (Spanish letters allowed).

    Attributes:
        username: login username (3-30 chars; letters, digits, ., _, -).
        email: valid email address.
        role: RoleEnum value.
        password: plaintext password provided by client (must satisfy strength rules).
        dni: 8-digit Peruvian DNI.
        names: given names.
        paternal_surname: paternal family name.
        maternal_surname: maternal family name.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    username: str = Field(
        min_length=3,
        max_length=30,
        description="Username for login (letters, digits, dot, underscore, hyphen).",
        examples=["juan.perez", "user_01"],
        pattern=r"^[A-Za-z0-9_.-]+$",
    )

    email: EmailStr = Field(
        description="User email address.",
        examples=["user@example.com"],
    )

    role: RoleEnum = Field(
        description="User role (RoleEnum).",
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        description="User password (must meet complexity requirements).",
        examples=["P@ssw0rd!"],
    )

    dni: str = Field(
        description="User DNI (8-digit unique identifier).",
        min_length=8,
        max_length=8,
        examples=["12345678"],
        pattern=r"^\d{8}$",  # Solo dígitos, más específico que [0-9]
    )

    names: str = Field(
        min_length=2,
        max_length=100,
        description="User given names.",
        examples=["Juan Carlos", "María Elena"],
    )

    paternal_surname: str = Field(
        min_length=2,
        max_length=50,
        description="Paternal surname.",
        examples=["González"],
    )

    maternal_surname: str = Field(
        min_length=2,
        max_length=50,
        description="Maternal surname.",
        examples=["Pérez"],
    )

    @field_validator("dni", mode="before")
    @classmethod
    def clean_dni(cls, v) -> str:
        """Remove non-digit characters from DNI.

        Args:
            v: raw dni value.

        Returns:
            Cleaned DNI string containing only digits.
        """
        if isinstance(v, str):
            return re.sub(r"\D", "", v)  # \D es más específico que [^\d]
        return v

    @field_validator("names", "paternal_surname", "maternal_surname", mode="before")
    @classmethod
    def normalize_names(cls, v) -> str:
        """Normalize whitespace and capitalize names.

        Collapses multiple spaces and applies title case.
        Note: str_strip_whitespace=True already handles outer whitespace.

        Args:
            v: raw name string.

        Returns:
            Normalized name string.
        """
        if isinstance(v, str):
            # No need for .strip() due to str_strip_whitespace=True
            normalized = re.sub(r"\s+", " ", v).title()
            return normalized
        return v

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, v) -> str:
        """Normalize username (convert to lowercase).

        Note: str_strip_whitespace=True already handles whitespace.

        Args:
            v: raw username.

        Returns:
            Normalized username.
        """
        if isinstance(v, str):
            # No need for .strip() due to str_strip_whitespace=True
            return v.lower()
        return v

    @field_validator("dni", mode="after")
    @classmethod
    def validate_dni_patterns(cls, v: str) -> str:
        """Reject trivial or clearly invalid DNI patterns.

        Note: Field pattern=r'^\d{8}$' already ensures exactly 8 digits.

        Args:
            v: cleaned DNI string.

        Returns:
            DNI if valid.

        Raises:
            ValueError: when DNI is an invalid/trivial pattern.
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
            raise ValueError(
                "DNI cannot be an obvious sequential or repetitive pattern"
            )
        return v

    @field_validator("names", "paternal_surname", "maternal_surname", mode="after")
    @classmethod
    def validate_name_characters(cls, v: str) -> str:
        """Ensure names contain only allowed characters.

        Allowed: letters (including Spanish accents), spaces, apostrophes and hyphens.

        Raises:
            ValueError: if invalid characters are present.
        """
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s'-]+$", v):
            raise ValueError(
                "Only letters, spaces, apostrophes and hyphens are allowed in names"
            )
        return v

    @field_validator("username", mode="after")
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        """Validate username format rules.

        Note: Field pattern already validates allowed characters.
        This adds additional business rules.

        Raises:
            ValueError: on invalid username format.
        """
        if v[0] in "._-" or v[-1] in "._-":
            raise ValueError("Username cannot start or end with '.', '_' or '-'")
        return v

    @field_validator("password", mode="after")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Basic password strength validation.

        Note: Field min_length=8 already ensures minimum length.
        This adds complexity requirements.

        Requires at least one lowercase, one uppercase, one digit and one special char.

        Raises:
            ValueError: if password does not meet complexity requirements.
        """
        patterns = [
            r"[a-z]",
            r"[A-Z]",
            r"\d",
            r"[^\w\s]",
        ]
        if not all(re.search(p, v) for p in patterns):
            raise ValueError(
                "Password must contain at least one lowercase, one uppercase, one digit and one special character"
            )
        return v
