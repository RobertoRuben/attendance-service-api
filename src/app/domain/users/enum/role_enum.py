from enum import Enum


class RoleEnum(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"
    AUXILIAR = "auxiliar"
    DIRECTOR = "director"
