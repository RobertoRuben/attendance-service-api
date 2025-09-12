from abc import ABC
from src.app.core.repository.interface import IBaseRepository
from src.app.domain.classrooms.model import Section


class ISectionRepository(IBaseRepository[Section], ABC):
    """
    Interface for Section repository.
    """

    pass
