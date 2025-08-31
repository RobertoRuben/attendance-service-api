from abc import ABC, abstractmethod
from datetime import date
from src.app.core.model.message_response import MessageResponse
from src.app.domain.classrooms.dto.request import SectionRequestDTO
from src.app.domain.classrooms.dto.response import (
    SectionPageResponseDTO,
    SectionResponseDTO,
)


class ISectionService(ABC):
    """
    Abstract interface for the Section service.

    Defines CRUD operations and advanced search methods for the Section entity.
    """

    @abstractmethod
    async def create_section(
        self, section_request: SectionRequestDTO
    ) -> SectionResponseDTO:
        """
        Create a new section.

        Args:
            section_request (SectionRequestDTO): Data required to create the section.

        Returns:
            SectionResponseDTO: The created section data.
        """
        pass

    @abstractmethod
    async def get_all_sections(self) -> list[SectionResponseDTO]:
        """
        Retrieve all sections.

        Returns:
            list[SectionResponseDTO]: A list of all sections.
        """
        pass

    @abstractmethod
    async def update_section(
        self, section_id: int, section_request: SectionRequestDTO
    ) -> SectionPageResponseDTO:
        """
        Update an existing section by its identifier.

        Args:
            section_id (int): Identifier of the section to update.
            section_request (SectionRequestDTO): Updated section data.

        Returns:
            SectionPageResponseDTO: The updated section data.
        """
        pass

    @abstractmethod
    async def delete_section(self, section_id: int) -> MessageResponse:
        """
        Delete a section by its identifier.

        Args:
            section_id (int): Identifier of the section to delete.

        Returns:
            MessageResponse: Result message of the operation.
        """
        pass

    @abstractmethod
    async def get_section_by_id(self, section_id: int) -> SectionResponseDTO:
        """
        Retrieve a section by its identifier.

        Args:
            section_id (int): Identifier of the section to retrieve.

        Returns:
            SectionResponseDTO: The requested section data.
        """
        pass

    @abstractmethod
    async def get_paginated_sections(
        self, page: int, size: int
    ) -> SectionPageResponseDTO:
        """
        Get a paginated list of sections.

        Args:
            page (int): Page number to retrieve.
            size (int): Number of sections per page.

        Returns:
            SectionPageResponseDTO: Paginated sections data.
        """
        pass

    @abstractmethod
    async def find_pageable_sections(
        self,
        page: int,
        size: int,
        section_name: str | None = None,
        created_from: date | None = None,
        created_to: date | None = None,
        updated_from: date | None = None,
        updated_to: date | None = None,
    ) -> SectionPageResponseDTO:
        """
        Find sections with pagination and optional filters.

        Args:
            page (int): Page number to retrieve.
            size (int): Number of sections per page.
            section_name (str | None): Optional partial match filter for section name.
            created_from (date | None): Optional start date for creation filter.
            created_to (date | None): Optional end date for creation filter.
            updated_from (date | None): Optional start date for update filter.
            updated_to (date | None): Optional end date for update filter.

        Returns:
            SectionPageResponseDTO: Paginated and filtered sections data.
        """
        pass
