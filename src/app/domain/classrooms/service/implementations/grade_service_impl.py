from datetime import datetime
from src.app.core.exception.conflict_exception import ConflictException
from src.app.core.exception.decorator import service_handle_exceptions
from src.app.core.exception.not_found_exception import NotFoundException
from src.app.core.model.message_response import MessageResponse
from src.app.domain.classrooms.dto.request import GradeRequestDTO
from src.app.domain.classrooms.dto.response import (
    GradePageResponseDTO,
    GradeResponseDTO,
)
from src.app.domain.classrooms.model import Grade
from src.app.domain.classrooms.repository.interface import IGradeRepository
from src.app.domain.classrooms.service.interface import IGradeService


class GradeServiceImpl(IGradeService):
    def __init__(self, grade_repository: IGradeRepository):
        self.grade_repository = grade_repository

    @service_handle_exceptions
    async def create_grade(self, grade_request: GradeRequestDTO) -> GradeResponseDTO:
        """
        Create a new grade.

        Args:
            grade_request (GradeRequestDTO): The grade information to create.

        Returns:
            GradeResponseDTO: The created grade information.
        """
        existing_grade_name = await self.grade_repository.exists_by(
            grade_name=grade_request.grade_name
        )

        if existing_grade_name:
            raise ConflictException(
                message="Grade with this name already exists.",
                details=f"A grade with name '{grade_request.grade_name}' already exists.",
            )

        new_grade = Grade(
            grade_name=grade_request.grade_name,
        )

        created_grade = await self.grade_repository.save(new_grade)

        return GradeResponseDTO.model_validate(created_grade)

    @service_handle_exceptions
    async def get_all_grades(self) -> list[GradeResponseDTO]:
        """
        Get all grades.

        Returns:
            list[GradeResponseDTO]: The list of all grades.
        """
        grades = await self.grade_repository.get_all()
        return [GradeResponseDTO.model_validate(grade) for grade in grades]

    @service_handle_exceptions
    async def update_grade(
        self, grade_id: int, grade_request: GradeRequestDTO
    ) -> GradeResponseDTO:
        """
        Update an existing grade.

        Args:
            grade_id (int): The ID of the grade to update.
            grade_request (GradeRequestDTO): The new grade information.

        Returns:
            GradeResponseDTO: The updated grade information.
        """
        existing_grade = await self.grade_repository.get_by_id(grade_id)

        if not existing_grade:
            raise NotFoundException(
                message="Grade not found.",
                details=f"Grade with ID '{grade_id}' does not exist.",
            )

        if existing_grade.grade_name != grade_request.grade_name:
            if await self.grade_repository.exists_by(
                grade_name=grade_request.grade_name
            ):
                raise ConflictException(
                    message="Grade with this name already exists.",
                    details=f"A grade with name '{grade_request.grade_name}' already exists.",
                )

        updated_grade = await self.grade_repository.update_by_id(
            grade_id=grade_id, grade_data=grade_request
        )

        return GradeResponseDTO.model_validate(updated_grade)

    @service_handle_exceptions
    async def delete_grade(self, grade_id: int) -> MessageResponse:
        """
        Delete a grade by its ID.

        Args:
            grade_id (int): The ID of the grade to delete.

        Returns:
            MessageResponse: The response message.
        """
        existing_grade = await self.grade_repository.get_by_id(grade_id)

        if not existing_grade:
            raise NotFoundException(
                message="Grade not found.",
                details=f"Grade with ID '{grade_id}' does not exist.",
            )

        await self.grade_repository.delete_by_id(grade_id)

        return MessageResponse(
            status_code=200,
            success=True,
            message="Grade deleted successfully.",
            details=f"Grade with ID '{grade_id}' has been deleted.",
        )

    @service_handle_exceptions
    async def get_grade_by_id(self, grade_id: int) -> GradeResponseDTO:
        """
        Get a grade by its ID.

        Args:
            grade_id (int): The ID of the grade to retrieve.

        Returns:
            GradeResponseDTO: The retrieved grade information.
        """
        grade = await self.grade_repository.get_by_id(grade_id)

        if not grade:
            raise NotFoundException(
                message="Grade not found.",
                details=f"Grade with ID '{grade_id}' does not exist.",
            )

        return GradeResponseDTO.model_validate(grade)

    @service_handle_exceptions
    async def get_pageable_grades(self, page: int, size: int) -> GradePageResponseDTO:
        """
        Get a paginated list of grades.

        Args:
            page (int): The page number.
            size (int): The number of items per page.

        Returns:
            GradePageResponseDTO: The paginated list of grades.
        """
        grades = await self.grade_repository.get_pageable(page, size)
        total = await self.grade_repository.count()

        return GradePageResponseDTO(
            items=[GradeResponseDTO.model_validate(grade) for grade in grades],
            total=total,
            page=page,
            size=size,
        )

    @service_handle_exceptions
    async def find_pageable_grades(
        self,
        page: int,
        size: int,
        grade_name: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> GradePageResponseDTO:
        """
        Find a paginated list of grades with optional search criteria.

        Args:
            page (int): The page number.
            size (int): The number of items per page.
            grade_name (str | None): Optional grade name filter (partial match).
            created_from (datetime | None): Optional start date for creation filter.
            created_to (datetime | None): Optional end date for creation filter.

        Returns:
            GradePageResponseDTO: The paginated list of grades matching the criteria.
        """
        filters = {}
        where_conditions = {}

        if grade_name:
            filters["grade_name"] = grade_name

        if created_from or created_to:
            date_conditions = {}
            if created_from:
                date_conditions["gte"] = created_from
            if created_to:
                date_conditions["lte"] = created_to
            where_conditions["created_at"] = date_conditions

        page_result = await self.grade_repository.find_pageables(
            page=page,
            size=size,
            filters=filters if filters else None,
            where_conditions=where_conditions if where_conditions else None,
        )

        items = [GradeResponseDTO.model_validate(item) for item in page_result.data]

        return GradePageResponseDTO(data=items, meta=page_result.meta)
