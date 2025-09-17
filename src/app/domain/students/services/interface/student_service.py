from abc import ABC, abstractmethod

from src.app.core.model import MessageResponse
from src.app.domain.students.dto.request import StudentRequestDTO
from src.app.domain.students.dto.response import (
    StudentPageResponseDTO,
    StudentResponseDTO,
)


class IStudentService(ABC):
    """Student service interface.

    Defines the contract for student-related business operations. Implementations
    should provide asynchronous behavior and raise domain-specific exceptions
    when appropriate.

    Responsibilities:
        * Create, read, update and delete student records.
        * Provide paginated retrieval of students.
        * Return DTOs suitable for API responses.
    """

    @abstractmethod
    async def create_student(
        self, student_request: StudentRequestDTO
    ) -> StudentResponseDTO:
        """Create a new student.

        Args:
            student_request (StudentRequestDTO): DTO containing student data to create.

        Returns:
            StudentResponseDTO: DTO representing the created student.
        """
        pass

    @abstractmethod
    async def get_all_students(self) -> list[StudentResponseDTO]:
        """Retrieve all students.

        Returns:
            list[StudentResponseDTO]: A list of student DTOs.

        Notes:
            Use with caution for large datasets. Prefer paginated endpoints for production.
        """
        pass

    @abstractmethod
    async def update_student(
        self, student_id: int, student_request: StudentRequestDTO
    ) -> StudentResponseDTO:
        """Update an existing student by id.

        Args:
            student_id (int): Identifier of the student to update.
            student_request (StudentRequestDTO): DTO with fields to update.

        Returns:
            StudentResponseDTO: DTO representing the updated student.
        """
        pass

    @abstractmethod
    async def delete_student(self, student_id: int) -> MessageResponse:
        """Delete a student by id.

        Args:
            student_id (int): Identifier of the student to delete.

        Returns:
            MessageResponse: Operation result message.
        """
        pass

    @abstractmethod
    async def get_student_by_id(self, student_id: int) -> StudentResponseDTO:
        """Retrieve a single student by id.

        Args:
            student_id (int): Identifier of the student to retrieve.

        Returns:
            StudentResponseDTO: DTO representing the found student.
        """
        pass

    @abstractmethod
    async def get_paginated_students(
        self, page: int, size: int
    ) -> StudentPageResponseDTO:
        """Get a paginated list of students.

        Args:
            page (int): 1-based page number to retrieve.
            size (int): Number of items per page.

        Returns:
            StudentPageResponseDTO: Paginated DTO containing students and pagination metadata.
        """
        pass

    @abstractmethod
    async def find_students(
        self, page: int, size: int, search_query: str
    ) -> StudentPageResponseDTO:
        """Find students by criteria with pagination.

        Args:
            page (int): 1-based page number to retrieve.
            size (int): Number of items per page.
            search_dict (dict[str, str]): Dictionary of field-value pairs to filter students.

        Returns:
            StudentPageResponseDTO: Paginated DTO containing matching students and pagination metadata.
        """
        pass
