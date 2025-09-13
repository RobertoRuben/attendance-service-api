from abc import ABC
from src.app.core.repository.interface import IBaseRepository
from src.app.domain.students.model import Student

class IStudentRepository(IBaseRepository[Student], ABC):
    """
    Interface for student repository.
    """
    
    pass