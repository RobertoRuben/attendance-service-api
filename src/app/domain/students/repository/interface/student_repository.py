from abc import ABC, abstractmethod
from src.app.core.model.page import Page
from src.app.core.repository.interface import IBaseRepository
from src.app.domain.students.model import Student


class IStudentRepository(IBaseRepository[Student], ABC):
    """
    Interface for student repository.
    """

    @abstractmethod
    async def get_pageable_students(
        self,
        page: int,
        size: int,
    ) -> Page:
        """
        Get paginated students with only grade_name and section_name included.
        
        Args:
            page: Page number
            size: Items per page
            where_conditions: Optional filter conditions
            
        Returns:
            Page: Paginated students with grade_name and section_name
        """
        pass