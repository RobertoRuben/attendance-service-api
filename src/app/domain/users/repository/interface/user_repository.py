from abc import ABC
from src.app.core.repository.interface import IBaseRepository
from src.app.domain.users.model import User


class IUserRepository(IBaseRepository[User], ABC):
    """
    Interface for the User repository.
    """

    pass
