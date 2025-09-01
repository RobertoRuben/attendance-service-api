from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request, status

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
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": GradeResponseDTO,
            "description": "Grade successfully created",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid request data or validation errors",
        },
        status.HTTP_409_CONFLICT: {
            "model": ConflictException,
            "description": "Grade name already exists in system",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error occurred",
        },
    },
    description="""
    Creates a new grade level in the educational system with the provided information. The grade name must be unique 
    across the entire system to prevent duplicates. This endpoint validates all input data including grade name, 
    level number, and associated metadata before creating the record. Successfully created grades can then be used 
    to organize students and sections within the academic structure.
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
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": list[GradeResponseDTO],
            "description": "All grades retrieved successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid request parameters",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error occurred",
        },
    },
    description="""
    Retrieves a complete list of all grade levels available in the educational system. This endpoint returns all grades 
    without any filtering or pagination, providing a comprehensive overview of the academic structure. It's particularly 
    useful for populating dropdown menus, generating reports, or when you need to display all available grade options. 
    For large datasets, consider using the paginated endpoint for better performance.
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
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": GradePageResponseDTO,
            "description": "Filtered grades retrieved successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid filter or pagination parameters",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error occurred",
        },
    },
    description="""
    Searches and filters grades using multiple criteria including grade name (with partial matching support) and creation 
    date ranges. This endpoint provides advanced search capabilities with pagination support for efficient data handling. 
    All filter parameters are optional and can be combined to create precise search queries. The partial name matching 
    allows for flexible searching, while date range filters help find grades created within specific time periods.
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
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": GradePageResponseDTO,
            "description": "Paginated grades retrieved successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid pagination parameters",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error occurred",
        },
    },
    description="""
    Retrieves grades using basic pagination controls for efficient data browsing and display. This endpoint provides 
    simple pagination without filtering capabilities, making it ideal for displaying grades in tables, lists, or grid 
    views where performance is important. The page size is configurable with a maximum limit of 100 items per page 
    to ensure optimal response times and prevent excessive data transfer.
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
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": GradeResponseDTO,
            "description": "Grade retrieved successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundException,
            "description": "Grade not found with specified ID",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid grade ID format",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error occurred",
        },
    },
    description="""
    Retrieves detailed information for a specific grade level using its unique identifier. This endpoint is used when 
    you need complete grade information including all associated metadata and relationships. The grade ID must be a 
    positive integer, and the system will return comprehensive grade details if the record exists. This is commonly 
    used for grade detail views, editing forms, or when building hierarchical academic structures.
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
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": GradeResponseDTO,
            "description": "Grade updated successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundException,
            "description": "Grade not found with specified ID",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid request data or grade ID",
        },
        status.HTTP_409_CONFLICT: {
            "model": ConflictException,
            "description": "Grade name already exists in system",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error occurred",
        },
    },
    description="""
    Updates the information of an existing grade level identified by its unique ID. This endpoint performs a complete 
    update of the grade data with the provided information, maintaining data integrity and validation rules. The system 
    verifies that the grade exists, validates the new data, and checks for name conflicts before applying changes. 
    All grade names must remain unique across the system to prevent duplicates and maintain academic structure consistency.
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
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": MessageResponse,
            "description": "Grade deleted successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundException,
            "description": "Grade not found with specified ID",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid grade ID format",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error occurred",
        },
    },
    description="""
    Permanently removes a grade level from the educational system using its unique identifier. This operation is 
    irreversible and will completely delete the grade record along with all associated metadata. The system validates 
    that the grade exists and checks for any dependencies (such as associated sections or students) before performing 
    the deletion. A confirmation message is returned upon successful completion of the delete operation.
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
