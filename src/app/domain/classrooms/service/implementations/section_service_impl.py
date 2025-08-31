from datetime import date
import pendulum

from src.app.core.exception.conflict_exception import ConflictException
from src.app.core.exception.decorator import service_handle_exceptions
from src.app.core.exception.not_found_exception import NotFoundException
from src.app.core.model.message_response import MessageResponse
from src.app.domain.classrooms.dto.request import SectionRequestDTO
from src.app.domain.classrooms.dto.response import (
    SectionPageResponseDTO,
    SectionResponseDTO,
)
from src.app.domain.classrooms.model import Section
from src.app.domain.classrooms.repository.interface import ISectionRepository
from src.app.domain.classrooms.service.interface import ISectionService


class SectionServiceImpl(ISectionService):
    """
    Concrete implementation of the Section service.

    Provides comprehensive functionality for section management,
    including CRUD operations and advanced searches with filters.
    """

    def __init__(self, section_repository: ISectionRepository):
        self.section_repository = section_repository

    @service_handle_exceptions
    async def create_section(
        self, section_request: SectionRequestDTO
    ) -> SectionResponseDTO:
        """
        Create a new section.

        Args:
            section_request (SectionRequestDTO): Data required to create the section.

        Returns:
            SectionResponseDTO: Data of the created section.
        """
        existing_section = await self.section_repository.exists_by(
            section_name=section_request.section_name
        )

        if existing_section:
            raise ConflictException(
                message="Section with this name already exists in the specified grade.",
                details=f"A section with name '{section_request.section_name}' already exists.",
            )

        new_section = Section(
            section_name=section_request.section_name,
        )

        created_section = await self.section_repository.save(new_section)

        return SectionResponseDTO.model_validate(created_section)

    @service_handle_exceptions
    async def get_all_sections(self) -> list[SectionResponseDTO]:
        """
        Retrieve all existing sections.

        Returns:
            list[SectionResponseDTO]: List of all sections.
        """
        sections = await self.section_repository.get_all()
        return [SectionResponseDTO.model_validate(section) for section in sections]

    @service_handle_exceptions
    async def update_section(
        self, section_id: int, section_request: SectionRequestDTO
    ) -> SectionResponseDTO:
        """
        Update an existing section by its identifier.

        Args:
            section_id (int): Identifier of the section to update.
            section_request (SectionRequestDTO): Updated section data.

        Returns:
            SectionPageResponseDTO: Data of the updated section.
        """
        existing_section = await self.section_repository.get_by_id(section_id)

        if not existing_section:
            raise NotFoundException(
                message="Section not found.",
                details=f"Section with ID '{section_id}' does not exist.",
            )

        if existing_section.section_name != section_request.section_name:
            if await self.section_repository.exists_by(
                section_name=section_request.section_name,
            ):
                raise ConflictException(
                    message="Section with this name already exists.",
                    details=f"A section with name '{section_request.section_name}' already exists.",
                )

        update_section = Section(
            section_name=section_request.section_name,
            updated_at=pendulum.now("America/Lima"),
        )

        updated_section = await self.section_repository.update_by_id(
            section_id,
            update_section.model_dump(exclude_none=True, exclude={"id", "created_at"}),
        )

        return SectionResponseDTO.model_validate(updated_section)

    @service_handle_exceptions
    async def delete_section(self, section_id: int) -> MessageResponse:
        """
        Delete a section by its identifier.

        Args:
            section_id (int): Identifier of the section to delete.

        Returns:
            MessageResponse: Message with the operation result.
        """
        existing_section = await self.section_repository.get_by_id(section_id)

        if not existing_section:
            raise NotFoundException(
                message="Section not found.",
                details=f"Section with ID '{section_id}' does not exist.",
            )

        await self.section_repository.delete(section_id)

        return MessageResponse(
            status_code=200,
            success=True,
            message="Section deleted successfully.",
            details=f"Section with ID '{section_id}' has been deleted.",
        )

    @service_handle_exceptions
    async def get_section_by_id(self, section_id: int) -> SectionResponseDTO:
        """
        Retrieve a section by its identifier.

        Args:
            section_id (int): Identifier of the section to query.

        Returns:
            SectionResponseDTO: Data of the requested section.
        """
        section = await self.section_repository.get_by_id(section_id)

        if not section:
            raise NotFoundException(
                message="Section not found.",
                details=f"Section with ID '{section_id}' does not exist.",
            )

        return SectionResponseDTO.model_validate(section)

    @service_handle_exceptions
    async def get_paginated_sections(
        self, page: int, size: int
    ) -> SectionPageResponseDTO:
        """
        Get a paginated list of sections.

        Args:
            page (int): Page number to retrieve.
            size (int): Number of sections per page.

        Returns:
            SectionPageResponseDTO: Paginated section data.
        """
        page_result = await self.section_repository.get_pageable(page, size)

        items = [SectionResponseDTO.model_validate(item) for item in page_result.data]

        return SectionPageResponseDTO(data=items, meta=page_result.meta)

    @service_handle_exceptions
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
        Search sections in a paginated way with optional filters for section name and date ranges.

        Args:
            page (int): Page number to retrieve.
            size (int): Number of sections per page.
            section_name (str | None): Optional section name filter (partial match).
            created_from (date | None): Start date to filter by creation date.
            created_to (date | None): End date to filter by creation date.
            updated_from (date | None): Start date to filter by update date.
            updated_to (date | None): End date to filter by update date.

        Returns:
            SectionPageResponseDTO: Paginated data of filtered sections.
        """
        filters = {}
        where_conditions = {}

        if section_name:
            filters["section_name"] = section_name

        if created_from or created_to:
            date_conditions = {}
            if created_from:
                # Usar pendulum.instance() para crear un datetime desde date + time
                date_conditions["gte"] = pendulum.instance(
                    pendulum.datetime(
                        created_from.year,
                        created_from.month,
                        created_from.day,
                        0,
                        0,
                        0,
                        tz="America/Lima",
                    )
                )
            if created_to:
                date_conditions["lte"] = pendulum.instance(
                    pendulum.datetime(
                        created_to.year,
                        created_to.month,
                        created_to.day,
                        23,
                        59,
                        59,
                        tz="America/Lima",
                    )
                )
            where_conditions["created_at"] = date_conditions

        if updated_from or updated_to:
            update_conditions = {}
            if updated_from:
                update_conditions["gte"] = pendulum.instance(
                    pendulum.datetime(
                        updated_from.year,
                        updated_from.month,
                        updated_from.day,
                        0,
                        0,
                        0,
                        tz="America/Lima",
                    )
                )
            if updated_to:
                update_conditions["lte"] = pendulum.instance(
                    pendulum.datetime(
                        updated_to.year,
                        updated_to.month,
                        updated_to.day,
                        23,
                        59,
                        59,
                        tz="America/Lima",
                    )
                )
            where_conditions["updated_at"] = update_conditions

        page_result = await self.section_repository.find_pageables(
            page=page,
            size=size,
            filters=filters if filters else None,
            where_conditions=where_conditions if where_conditions else None,
        )

        items = [SectionResponseDTO.model_validate(item) for item in page_result.data]

        return SectionPageResponseDTO(data=items, meta=page_result.meta)
