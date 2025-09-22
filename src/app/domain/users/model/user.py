from sqlmodel import SQLModel, Field, BIGINT, TEXT, Column
from sqlalchemy import Boolean, Enum as SQLEnum
from ..enum import RoleEnum


class User(SQLModel, table=True):
    """User database model.

    Represents a user record in the database.

    Attributes:
        id (int | None): Primary key (BigInteger). Auto-incremented when None.
        username (str): Unique username for login.
        role (RoleEnum): User role, constrained to values in RoleEnum.
        password (str): Password hash (store hashed passwords only; never plaintext).
        dni (str): National identification number, unique and required.
        names (str): Given names.
        paternal_surname (str): Paternal surname.
        maternal_surname (str): Maternal surname.
    """

    id: int | None = Field(default=None, sa_column=Column(BIGINT, primary_key=True))
    username: str = Field(sa_column=Column(TEXT, unique=True))
    email: str = Field(sa_column=Column(TEXT, unique=True, nullable=False))
    role: RoleEnum = Field(sa_column=Column(SQLEnum(RoleEnum), nullable=False))
    password: str | None = Field(default=None, sa_column=Column(TEXT, nullable=False))
    dni: str = Field(sa_column=Column(TEXT, unique=True, nullable=False))
    names: str = Field(sa_column=Column(TEXT, nullable=False))
    paternal_surname: str = Field(sa_column=Column(TEXT, nullable=False))
    maternal_surname: str = Field(sa_column=Column(TEXT, nullable=False))
    is_active: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
