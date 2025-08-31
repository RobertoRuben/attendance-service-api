from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request

from src.app.core.exception import (
    BadRequestException,
    ConflictException,
    NotFoundException,
    ServerException,
)
from src.app.core.exception.decorator import controller_handle_exceptions
from src.app.core.model import MessageResponse
from src.app.domain.classrooms.dto.request import GradeRequestDTO
from src.app.domain.classrooms.dto.response import (
    GradePageResponseDTO,
    GradeResponseDTO,
)
from src.app.domain.classrooms.service.dependencies import get_grade_service
from src.app.domain.classrooms.service.interface import IGradeService

router = APIRouter(prefix="/grades", tags=["Grades"])

grades_tags_metadata = {
    "name": "Grades",
    "description": "Operations related to student grades",
}


@router.post(
    "",
    response_model=GradeResponseDTO,
    summary="Create a new grade",
    status_code=201,
    responses={
        201: {"model": GradeResponseDTO, "description": "Successfully created grade."},
        400: {"model": BadRequestException, "description": "Invalid request data."},
        409: {
            "model": ConflictException,
            "description": "A grade with the same name already exists.",
        },
        500: {"model": ServerException, "description": "Internal server error."},
    },
    description="""
    This endpoint creates a new grade.
    """,
)
@controller_handle_exceptions
async def create_grade(
    request: Request,
    grade_request: GradeRequestDTO,
    grade_service: Annotated[IGradeService, Depends(get_grade_service)],
) -> GradeResponseDTO:
    """
    Create a new grade.

    Args:
        request (Request): The incoming request object.
        grade_request (GradeRequestDTO): The grade information to create.
        grade_service (IGradeService): The grade service implementation.

    Returns:
        GradeResponseDTO: The created grade information.

    Raises:
        BadRequestException: If the request data is invalid.
        ConflictException: If a grade with the same name already exists.
        ServerException: If there is an internal server error.
    """
    return await grade_service.create_grade(grade_request=grade_request)


@router.get(
    "",
    response_model=list[GradeResponseDTO],
    summary="Get all grades",
    status_code=200,
    responses={
        200: {
            "model": list[GradeResponseDTO],
            "description": "Successfully retrieved all grades.",
        },
        400: {"model": BadRequestException, "description": "Invalid request data."},
        500: {"model": ServerException, "description": "Internal server error."},
    },
    description="""
    This endpoint retrieves all grades.
    """,
)
@controller_handle_exceptions
async def get_all_grades(
    request: Request,
    grade_service: Annotated[IGradeService, Depends(get_grade_service)],
) -> list[GradeResponseDTO]:
    """
    Get all grades.

    Args:
        request (Request): The incoming request object.
        grade_service (IGradeService): The grade service implementation.

    Returns:
        list[GradeResponseDTO]: The list of all grades.

    Raises:
        ServerException: If there is an internal server error.
    """
    return await grade_service.get_all_grades()


@router.get(
    "/search",
    response_model=GradePageResponseDTO,
    summary="Search grades with filters",
    status_code=200,
    responses={
        200: {
            "model": GradePageResponseDTO,
            "description": "Successfully retrieved filtered grades.",
        },
        400: {"model": BadRequestException, "description": "Invalid request data."},
        500: {"model": ServerException, "description": "Internal server error."},
    },
    description="""
    This endpoint searches grades with optional filters including grade name,
    creation date range, and pagination.
    """,
)
@controller_handle_exceptions
async def search_grades(
    request: Request,
    grade_service: Annotated[IGradeService, Depends(get_grade_service)],
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Number of items per page"),
    grade_name: str | None = Query(
        default=None, description="Filter by grade name (partial match)"
    ),
    created_from: datetime | None = Query(
        default=None, description="Filter grades created from this date"
    ),
    created_to: datetime | None = Query(
        default=None, description="Filter grades created until this date"
    ),
) -> GradePageResponseDTO:
    """
    Search grades with filters.

    Args:
        request (Request): The incoming request object.
        grade_service (IGradeService): The grade service implementation.
        page (int): The page number.
        size (int): The number of items per page.
        grade_name (str | None): Optional grade name filter.
        created_from (datetime | None): Optional start date filter.
        created_to (datetime | None): Optional end date filter.

    Returns:
        GradePageResponseDTO: The paginated and filtered list of grades.

    Raises:
        BadRequestException: If the request parameters are invalid.
        ServerException: If there is an internal server error.
    """
    return await grade_service.find_pageable_grades(
        page=page,
        size=size,
        grade_name=grade_name,
        created_from=created_from,
        created_to=created_to,
    )


@router.get(
    "/paginated",
    response_model=GradePageResponseDTO,
    summary="Get paginated grades",
    status_code=200,
    responses={
        200: {
            "model": GradePageResponseDTO,
            "description": "Successfully retrieved paginated grades.",
        },
        400: {"model": BadRequestException, "description": "Invalid request data."},
        500: {"model": ServerException, "description": "Internal server error."},
    },
    description="""
    This endpoint retrieves paginated grades using basic pagination.
    """,
)
@controller_handle_exceptions
async def get_paginated_grades(
    request: Request,
    grade_service: Annotated[IGradeService, Depends(get_grade_service)],
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Number of items per page"),
) -> GradePageResponseDTO:
    """
    Get paginated grades.

    Args:
        request (Request): The incoming request object.
        grade_service (IGradeService): The grade service implementation.
        page (int): The page number.
        size (int): The number of items per page.

    Returns:
        GradePageResponseDTO: The paginated list of grades.

    Raises:
        BadRequestException: If the request parameters are invalid.
        ServerException: If there is an internal server error.
    """
    return await grade_service.get_paginated_grades(page=page, size=size)


@router.get(
    "/{grade_id}",
    response_model=GradeResponseDTO,
    summary="Get grade by ID",
    status_code=200,
    responses={
        200: {
            "model": GradeResponseDTO,
            "description": "Successfully retrieved grade.",
        },
        404: {"model": NotFoundException, "description": "Grade not found."},
        400: {"model": BadRequestException, "description": "Invalid grade ID."},
        500: {"model": ServerException, "description": "Internal server error."},
    },
    description="""
    This endpoint retrieves a specific grade by its ID.
    """,
)
@controller_handle_exceptions
async def get_grade_by_id(
    request: Request,
    grade_id: Annotated[
        int, Path(..., ge=1, description="The ID of the grade to retrieve")
    ],
    grade_service: Annotated[IGradeService, Depends(get_grade_service)],
) -> GradeResponseDTO:
    """
    Get a grade by its ID.

    Args:
        request (Request): The incoming request object.
        grade_id (int): The ID of the grade to retrieve.
        grade_service (IGradeService): The grade service implementation.

    Returns:
        GradeResponseDTO: The retrieved grade information.

    Raises:
        NotFoundException: If the grade with the specified ID does not exist.
        BadRequestException: If the grade ID is invalid.
        ServerException: If there is an internal server error.
    """
    return await grade_service.get_grade_by_id(grade_id=grade_id)


@router.put(
    "/{grade_id}",
    response_model=GradeResponseDTO,
    summary="Update an existing grade",
    status_code=200,
    responses={
        200: {"model": GradeResponseDTO, "description": "Successfully updated grade."},
        404: {"model": NotFoundException, "description": "Grade not found."},
        400: {"model": BadRequestException, "description": "Invalid request data."},
        409: {
            "model": ConflictException,
            "description": "A grade with the same name already exists.",
        },
        500: {"model": ServerException, "description": "Internal server error."},
    },
    description="""
    This endpoint updates an existing grade by its ID.
    """,
)
@controller_handle_exceptions
async def update_grade(
    request: Request,
    grade_id: Annotated[
        int, Path(..., ge=1, description="The ID of the grade to update")
    ],
    grade_request: GradeRequestDTO,
    grade_service: Annotated[IGradeService, Depends(get_grade_service)],
) -> GradeResponseDTO:
    """
    Update an existing grade.

    Args:
        request (Request): The incoming request object.
        grade_id (int): The ID of the grade to update.
        grade_request (GradeRequestDTO): The updated grade information.
        grade_service (IGradeService): The grade service implementation.

    Returns:
        GradeResponseDTO: The updated grade information.

    Raises:
        NotFoundException: If the grade with the specified ID does not exist.
        BadRequestException: If the request data is invalid.
        ConflictException: If a grade with the same name already exists.
        ServerException: If there is an internal server error.
    """
    return await grade_service.update_grade(
        grade_id=grade_id, grade_request=grade_request
    )


@router.delete(
    "/{grade_id}",
    response_model=MessageResponse,
    summary="Delete a grade",
    status_code=200,
    responses={
        200: {"model": MessageResponse, "description": "Successfully deleted grade."},
        404: {"model": NotFoundException, "description": "Grade not found."},
        400: {"model": BadRequestException, "description": "Invalid grade ID."},
        500: {"model": ServerException, "description": "Internal server error."},
    },
    description="""
    This endpoint deletes a grade by its ID.
    """,
)
@controller_handle_exceptions
async def delete_grade(
    request: Request,
    grade_id: Annotated[
        int, Path(..., ge=1, description="The ID of the grade to delete")
    ],
    grade_service: Annotated[IGradeService, Depends(get_grade_service)],
) -> MessageResponse:
    """
    Delete a grade by its ID.

    Args:
        request (Request): The incoming request object.
        grade_id (int): The ID of the grade to delete.
        grade_service (IGradeService): The grade service implementation.

    Returns:
        MessageResponse: The response message confirming deletion.

    Raises:
        NotFoundException: If the grade with the specified ID does not exist.
        BadRequestException: If the grade ID is invalid.
        ServerException: If there is an internal server error.
    """
    return await grade_service.delete_grade(grade_id=grade_id)
