from src.app.core.model.message_response import MessageResponse
from src.app.domain.classrooms.dto.request import GradeRequestDTO
from src.app.domain.classrooms.dto.response import (
    GradeResponseDTO,
    GradePageResponseDTO,
)
from abc import ABC, abstractmethod


class IGradeService(ABC):
    """
    Abstract service interface for Grade use-cases.
    """

    @abstractmethod
    async def create_grade(self, grade_request: GradeRequestDTO) -> GradeResponseDTO:
        """
        Create a new Grade.

        Args:
            grade_request: DTO containing the data required to create a Grade.

        Returns:
            GradeResponseDTO: The created grade as a response DTO.
        """
        pass

    @abstractmethod
    async def get_all_grades(self) -> list[GradeResponseDTO]:
        """
        Retrieve all grades.

        Returns:
            list[GradeResponseDTO]: A list of all grades.
        """
        pass

    @abstractmethod
    async def update_grade(
        self, grade_id: int, grade_request: GradeRequestDTO
    ) -> GradeResponseDTO:
        """
        Update an existing Grade by id.

        Args:
            grade_id: Identifier of the grade to update.
            grade_request: DTO with updated fields.

        Returns:
            GradeResponseDTO: The updated grade.

        Raises:
            NotFoundError: If the grade does not exist.
        """
        pass

    @abstractmethod
    async def delete_grade(self, grade_id: int) -> MessageResponse:
        """
        Delete a Grade by id.

        Args:
            grade_id: Identifier of the grade to delete.

        Returns:
            MessageResponse: Operation result message.

        Raises:
            NotFoundError: If the grade does not exist.
        """
        pass

    @abstractmethod
    async def get_grade_by_id(self, grade_id: int) -> GradeResponseDTO:
        """
        Retrieve a single Grade by id.

        Args:
            grade_id: Identifier of the grade.

        Returns:
            GradeResponseDTO: The requested grade.

        Raises:
            NotFoundError: If the grade does not exist.
        """
        pass

    @abstractmethod
    async def get_pageable_grades(self, page: int, size: int) -> GradePageResponseDTO:
        """
        Get a page of grades using standard pagination parameters.

        Args:
            page: Page number (0-based or 1-based depending on implementation).
            size: Number of items per page.

        Returns:
            GradePageResponseDTO: Paginated grades and metadata.
        """
        pass

    @abstractmethod
    async def find_pageable_grades(self, page: int, size: int) -> GradePageResponseDTO:
        """
        Alternative pageable finder (may apply different filters or ordering).

        Args:
            page: Page number.
            size: Page size.

        Returns:
            GradePageResponseDTO: Paginated result.
        """
        pass
