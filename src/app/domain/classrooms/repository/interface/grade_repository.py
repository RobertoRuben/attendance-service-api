from abc import ABC
from src.app.core.repository.interface import IBaseRepository
from src.app.domain.classrooms.model import Grade


class IGradeRepository(IBaseRepository[Grade], ABC):
    """
    Interface for the Grade repository.
    """

    pass
