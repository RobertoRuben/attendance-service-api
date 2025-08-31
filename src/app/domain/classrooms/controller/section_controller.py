from datetime import date

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
from src.app.domain.classrooms.dto.request import SectionRequestDTO
from src.app.domain.classrooms.dto.response import (
    SectionPageResponseDTO,
    SectionResponseDTO,
)
from src.app.domain.classrooms.service.dependencies import get_section_service
from src.app.domain.classrooms.service.interface import ISectionService

router = APIRouter(prefix="/sections", tags=["Sections"])

sections_tags_metadata = {
    "name": "Sections",
    "description": "Operations related to classroom sections",
}


@router.post(
    "",
    response_model=SectionResponseDTO,
    summary="Create a new section",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": SectionResponseDTO,
            "description": "Section successfully created",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid request data",
        },
        status.HTTP_409_CONFLICT: {
            "model": ConflictException,
            "description": "Section name already exists in grade",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error",
        },
    },
    description="""
    Creates a new classroom section with the provided information. The section name must be unique within the specified grade level. 
    This endpoint validates the input data and ensures no duplicate section names exist in the same grade before creating the section.
    """,
)
@controller_handle_exceptions
async def create_section(
    request: Request,
    section_request: SectionRequestDTO,
    section_service: Annotated[ISectionService, Depends(get_section_service)],
) -> SectionResponseDTO:
    """
    Create a new section.

    Args:
        request (Request): The incoming request object.
        section_request (SectionRequestDTO): The section information to create.
        section_service (ISectionService): The section service implementation.

    Returns:
        SectionResponseDTO: The created section information.

    Raises:
        BadRequestException: If the request data is invalid.
        ConflictException: If a section with the same name already exists in the grade.
        ServerException: If there is an internal server error.
    """
    return await section_service.create_section(section_request=section_request)


@router.get(
    "",
    response_model=list[SectionResponseDTO],
    summary="Get all sections",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": list[SectionResponseDTO],
            "description": "All sections retrieved successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid request parameters",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error",
        },
    },
    description="""
    Retrieves a complete list of all available classroom sections in the system. This endpoint returns all sections without 
    any filtering or pagination, making it suitable for small datasets or when you need a complete overview of all sections. 
    For large datasets, consider using the paginated endpoint instead.
    """,
)
@controller_handle_exceptions
async def get_all_sections(
    request: Request,
    section_service: Annotated[ISectionService, Depends(get_section_service)],
) -> list[SectionResponseDTO]:
    """
    Get all sections.

    Args:
        request (Request): The incoming request object.
        section_service (ISectionService): The section service implementation.

    Returns:
        list[SectionResponseDTO]: The list of all sections.

    Raises:
        ServerException: If there is an internal server error.
    """
    return await section_service.get_all_sections()


@router.get(
    "/search",
    response_model=SectionPageResponseDTO,
    summary="Search sections with filters",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": SectionPageResponseDTO,
            "description": "Filtered sections retrieved successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid filter parameters",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error",
        },
    },
    description="""
    Searches and filters sections using multiple criteria including section name (partial matching), creation date ranges, 
    and update date ranges. Results are returned with pagination support for efficient data handling. This endpoint is ideal 
    for advanced search scenarios where users need to find specific sections based on various attributes. All filter parameters 
    are optional and can be combined for precise results.
    """,
)
@controller_handle_exceptions
async def search_sections(
    request: Request,
    section_service: Annotated[ISectionService, Depends(get_section_service)],
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Number of items per page"),
    section_name: str | None = Query(
        default=None, description="Filter by section name (partial match)"
    ),
    created_from: date | None = Query(
        default=None,
        description="Filter sections created from this date",
        example="2025-01-01",
    ),
    created_to: date | None = Query(
        default=None,
        description="Filter sections created until this date",
        example="2025-02-01",
    ),
    updated_from: date | None = Query(
        default=None,
        description="Filter sections updated from this date",
        example="2025-01-01",
    ),
    updated_to: date | None = Query(
        default=None,
        description="Filter sections updated until this date",
        example="2025-02-01",
    ),
) -> SectionPageResponseDTO:
    """
    Search sections with filters.

    Args:
        request (Request): The incoming request object.
        section_service (ISectionService): The section service implementation.
        page (int): The page number.
        size (int): The number of items per page.
        section_name (str | None): Optional section name filter.
        created_from (date | None): Optional start date filter for creation.
        created_to (date | None): Optional end date filter for creation.
        updated_from (date | None): Optional start date filter for updates.
        updated_to (date | None): Optional end date filter for updates.

    Returns:
        SectionPageResponseDTO: The paginated and filtered list of sections.

    Raises:
        BadRequestException: If the request parameters are invalid.
        ServerException: If there is an internal server error.
    """
    return await section_service.find_pageable_sections(
        page=page,
        size=size,
        section_name=section_name,
        created_from=created_from,
        created_to=created_to,
        updated_from=updated_from,
        updated_to=updated_to,
    )


@router.get(
    "/paginated",
    response_model=SectionPageResponseDTO,
    summary="Get paginated sections",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": SectionPageResponseDTO,
            "description": "Paginated sections retrieved successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid pagination parameters",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error",
        },
    },
    description="""
    Retrieves sections with basic pagination controls for efficient data browsing. This endpoint provides simple pagination 
    without any filtering capabilities, making it perfect for displaying sections in a paginated table or list view. 
    It supports configurable page size with a maximum limit of 100 items per page to ensure optimal performance.
    """,
)
@controller_handle_exceptions
async def get_paginated_sections(
    request: Request,
    section_service: Annotated[ISectionService, Depends(get_section_service)],
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Number of items per page"),
) -> SectionPageResponseDTO:
    """
    Get paginated sections.

    Args:
        request (Request): The incoming request object.
        section_service (ISectionService): The section service implementation.
        page (int): The page number.
        size (int): The number of items per page.

    Returns:
        SectionPageResponseDTO: The paginated list of sections.

    Raises:
        BadRequestException: If the request parameters are invalid.
        ServerException: If there is an internal server error.
    """
    return await section_service.get_paginated_sections(page=page, size=size)


@router.get(
    "/{section_id}",
    response_model=SectionResponseDTO,
    summary="Get section by ID",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": SectionResponseDTO,
            "description": "Section retrieved successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundException,
            "description": "Section not found",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid section ID",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error",
        },
    },
    description="""
    Retrieves detailed information for a specific section using its unique identifier. This endpoint is used to fetch 
    complete section details when you know the exact section ID. The ID must be a positive integer, and the endpoint 
    will return a 404 error if the section doesn't exist in the system.
    """,
)
@controller_handle_exceptions
async def get_section_by_id(
    request: Request,
    section_id: Annotated[
        int, Path(..., ge=1, description="The ID of the section to retrieve")
    ],
    section_service: Annotated[ISectionService, Depends(get_section_service)],
) -> SectionResponseDTO:
    """
    Get a section by its ID.

    Args:
        request (Request): The incoming request object.
        section_id (int): The ID of the section to retrieve.
        section_service (ISectionService): The section service implementation.

    Returns:
        SectionResponseDTO: The retrieved section information.

    Raises:
        NotFoundException: If the section with the specified ID does not exist.
        BadRequestException: If the section ID is invalid.
        ServerException: If there is an internal server error.
    """
    return await section_service.get_section_by_id(section_id=section_id)


@router.put(
    "/{section_id}",
    response_model=SectionResponseDTO,
    summary="Update an existing section",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": SectionResponseDTO,
            "description": "Section updated successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundException,
            "description": "Section not found",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid request data",
        },
        status.HTTP_409_CONFLICT: {
            "model": ConflictException,
            "description": "Section name already exists in grade",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error",
        },
    },
    description="""
    Updates the information of an existing section identified by its ID. This endpoint performs a complete update of the section 
    data with the provided information. It validates that the section exists, checks for name conflicts within the same grade, 
    and ensures data integrity before applying the changes. The section name must remain unique within its grade level.
    """,
)
@controller_handle_exceptions
async def update_section(
    request: Request,
    section_id: Annotated[
        int, Path(..., ge=1, description="The ID of the section to update")
    ],
    section_request: SectionRequestDTO,
    section_service: Annotated[ISectionService, Depends(get_section_service)],
) -> SectionPageResponseDTO:
    """
    Update an existing section.

    Args:
        request (Request): The incoming request object.
        section_id (int): The ID of the section to update.
        section_request (SectionRequestDTO): The updated section information.
        section_service (ISectionService): The section service implementation.

    Returns:
        SectionPageResponseDTO: The updated section information.

    Raises:
        NotFoundException: If the section with the specified ID does not exist.
        BadRequestException: If the request data is invalid.
        ConflictException: If a section with the same name already exists in the grade.
        ServerException: If there is an internal server error.
    """
    return await section_service.update_section(
        section_id=section_id, section_request=section_request
    )


@router.delete(
    "/{section_id}",
    response_model=MessageResponse,
    summary="Delete a section",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": MessageResponse,
            "description": "Section deleted successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundException,
            "description": "Section not found",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid section ID",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error",
        },
    },
    description="""
    Permanently removes a section from the system using its unique identifier. This operation is irreversible and will 
    completely delete the section and all its associated data. The endpoint validates that the section exists before 
    performing the deletion and returns a confirmation message upon successful completion.
    """,
)
@controller_handle_exceptions
async def delete_section(
    request: Request,
    section_id: Annotated[
        int, Path(..., ge=1, description="The ID of the section to delete")
    ],
    section_service: Annotated[ISectionService, Depends(get_section_service)],
) -> MessageResponse:
    """
    Delete a section by its ID.

    Args:
        request (Request): The incoming request object.
        section_id (int): The ID of the section to delete.
        section_service (ISectionService): The section service implementation.

    Returns:
        MessageResponse: The response message confirming deletion.

    Raises:
        NotFoundException: If the section with the specified ID does not exist.
        BadRequestException: If the section ID is invalid.
        ServerException: If there is an internal server error.
    """
    return await section_service.delete_section(section_id=section_id)
