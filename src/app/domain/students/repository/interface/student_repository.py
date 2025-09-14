from abc import ABC, abstractmethod
from src.app.core.model.page import Page
from src.app.core.repository.interface import IBaseRepository
from src.app.domain.students.model import Student


class IStudentRepository(IBaseRepository[Student], ABC):
    """Interface for student repository operations.

    This interface extends the base repository functionality with
    student-specific operations. It defines the contract for
    data access operations related to student entities.

    The interface provides specialized methods for retrieving
    student data with related information (grade and section names)
    for presentation purposes.

    Inherits:
        IBaseRepository[Student]: Base repository interface providing
            standard CRUD operations for Student entities.
        ABC: Abstract base class to enforce interface implementation.

    Note:
        All methods in this interface must be implemented by concrete
        repository classes. The interface focuses on data access
        patterns specific to the student domain.
    """

    @abstractmethod
    async def get_pageable_students(
        self,
        page: int,
        size: int,
    ) -> Page:
        """Retrieve paginated students with grade and section information.

        Fetches students in a paginated format, including the descriptive
        names of their associated grade and section for display purposes.
        This method is optimized for presenting student lists in user
        interfaces where grade and section names are needed.

        Args:
            page: The page number to retrieve (1-based indexing).
                Must be a positive integer.
            size: The number of items per page. Must be a positive
                integer, typically between 10 and 100.

        Returns:
            Page: A paginated result containing:
                - items: List of Student objects with populated grade_name
                  and section_name attributes
                - total_items: Total number of students in the system
                - page: Current page number
                - size: Items per page
                - total_pages: Total number of pages available

        Raises:
            ValueError: If page or size parameters are invalid (non-positive).
            RepositoryError: If database operation fails.

        Example:
            >>> repository = StudentRepositoryImpl()
            >>> result = await repository.get_pageable_students(page=1, size=20)
            >>> print(f"Found {result.total_items} students")
            >>> for student in result.items:
            ...     print(f"{student.names} - {student.grade_name} {student.section_name}")
        """
        pass
