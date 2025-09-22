from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class UserResponseDTO(BaseModel):
    """Data Transfer Object para la respuesta de User.

    Este DTO estructura los datos devueltos al cliente cuando se crea,
    actualiza o recupera un usuario.

    Attributes:
        id: Identificador único del usuario. Opcional en solicitudes de creación.
        username: Nombre de usuario.
        email: Correo electrónico del usuario.
        role: Rol del usuario (por ejemplo, "admin").
        dni: Documento Nacional de Identidad del usuario.
        names: Nombres del usuario.
        paternal_surname: Apellido paterno.
        maternal_surname: Apellido materno.
        is_active: Indica si el usuario está activo.
        created_at: Marca temporal de creación del registro.
        updated_at: Marca temporal de la última actualización (None si nunca se actualizó).

    Example:
        >>> user = UserResponseDTO(
        ...     id=1,
        ...     username="johndoe",
        ...     email="johndoe@example.com",
        ...     role="admin",
        ...     dni="12345678",
        ...     names="John",
        ...     paternal_surname="Doe",
        ...     maternal_surname="Smith",
        ...     is_active=True,
        ...     created_at=datetime.now()
        ... )
    """

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: int | None = Field(
        default=None,
        description="Identifier of the user",
        examples=[1],
    )
    username: str = Field(
        description="Username of the user",
        examples=["johndoe"],
    )
    email: str = Field(
        description="Email of the user",
        examples=["johndoe@example.com"],
    )
    role: str = Field(
        description="Role of the user",
        examples=["admin"],
    )
    dni: str = Field(
        description="DNI of the user",
        examples=["12345678"],
    )
    names: str = Field(
        description="Names of the user",
        examples=["John"],
    )
    paternal_surname: str = Field(
        description="Paternal surname of the user",
        examples=["Doe"],
    )
    maternal_surname: str = Field(
        description="Maternal surname of the user",
        examples=["Smith"],
    )
    is_active: bool = Field(
        description="Indicates if the user is active",
        examples=[True],
    )
    created_at: datetime = Field(
        description="Creation date of the user record",
        examples=[datetime.now()],
    )
    updated_at: datetime | None = Field(
        default=None,
        description="Last update date of the user record",
        examples=[datetime.now()],
    )
