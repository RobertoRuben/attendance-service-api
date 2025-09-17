from typing import Annotated

from fastapi import APIRouter, Depends, Query, Path, Request, status

from src.app.core.exception import (
    BadRequestException,
    ConflictException,
    NotFoundException,
    ServerException,
)
from src.app.core.exception.decorator import (
    controller_handle_exceptions,
)
from src.app.core.model import MessageResponse
from src.app.domain.students.dto.request import StudentRequestDTO
from src.app.domain.students.dto.response import (
    StudentPageResponseDTO,
    StudentResponseDTO,
)
from src.app.domain.students.services.dependencies import (
    get_student_service,
)
from src.app.domain.students.services.interface import IStudentService


router = APIRouter(prefix="/students", tags=["Students"])
"""FastAPI router for student management endpoints.

This router provides RESTful endpoints for student CRUD operations including
creation, retrieval, updates, and deletion. All endpoints follow REST conventions
and include comprehensive error handling with appropriate HTTP status codes.

Routes:
    POST /students: Create a new student
    GET /students: Retrieve all students
    GET /students/search: Search students with filters
    GET /students/paginated: Get paginated students
    GET /students/{student_id}: Get student by ID
    PUT /students/{student_id}: Update existing student
    DELETE /students/{student_id}: Delete student by ID
"""

students_tags_metadata = {
    "name": "Students",
    "description": "Operations related to student management in the educational system",
}
"""Metadata configuration for the Students tag in OpenAPI documentation.

Provides descriptive information about the student endpoints group for
automatic API documentation generation and client SDK creation.
"""


@router.post(
    "",
    response_model=StudentResponseDTO,
    summary="Create a new student",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": StudentResponseDTO,
            "description": "Student successfully created",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid request data or validation errors",
        },
        status.HTTP_409_CONFLICT: {
            "model": ConflictException,
            "description": "Student DNI already exists in system",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error occurred",
        },
    },
    description="""
    Creates a new student record in the educational system with the provided information. The student DNI must be unique 
    across the entire system to prevent duplicates. This endpoint validates all input data including DNI format, 
    names, grade and section references before creating the record. Successfully created students are automatically 
    assigned to their specified grade and section for academic organization.
    """,
)
@controller_handle_exceptions
async def create_student(
    request: Request,
    student_request: StudentRequestDTO,
    student_service: Annotated[IStudentService, Depends(get_student_service)],
) -> StudentResponseDTO:
    """Create a new student record in the educational system.

    Validates all input data and ensures DNI uniqueness across the system before
    creating the student record. The student is automatically assigned to the
    specified grade and section upon successful creation.

    Args:
        request (Request): The incoming HTTP request object containing headers
            and metadata.
        student_request (StudentRequestDTO): Data transfer object containing
            all required student information including personal details, DNI,
            and academic assignment (grade and section IDs).
        student_service (IStudentService): Injected service implementation
            for handling student business logic and data persistence.

    Returns:
        StudentResponseDTO: Complete student information including the newly
            assigned ID, timestamps, and all provided data after successful
            creation and persistence.

    Raises:
        BadRequestException: When the request data fails validation, including
            invalid DNI format, missing required fields, or malformed data.
        ConflictException: When a student with the same DNI already exists
            in the system, preventing duplicate entries.
        ServerException: When an unexpected internal error occurs during
            the creation process, such as database connectivity issues.

    Example:
        >>> POST /students
        >>> {
        ...     "dni": "12345678",
        ...     "names": "John",
        ...     "paternal_surname": "Doe",
        ...     "maternal_surname": "Smith",
        ...     "grade_id": 1,
        ...     "section_id": 1
        ... }
    """
    return await student_service.create_student(student_request=student_request)


@router.get(
    "",
    response_model=list[StudentResponseDTO],
    summary="Get all students",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": list[StudentResponseDTO],
            "description": "All students retrieved successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundException,
            "description": "No students found in the system",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error occurred",
        },
    },
    description="""
    Retrieves a complete list of all students enrolled in the educational system. This endpoint returns all students 
    without any filtering or pagination, providing a comprehensive overview of the student body. It's particularly 
    useful for generating complete reports, populating selection lists, or when you need to display all student records. 
    For large datasets, consider using the paginated endpoint for better performance.
    """,
)
@controller_handle_exceptions
async def get_all_students(
    request: Request,
    student_service: Annotated[IStudentService, Depends(get_student_service)],
) -> list[StudentResponseDTO]:
    """Retrieve all students from the educational system.

    Returns a complete, unfiltered list of all student records in the system.
    This endpoint is useful for administrative overviews, report generation,
    and populating dropdown lists or selection components.

    Args:
        request (Request): The incoming HTTP request object containing headers
            and metadata for the retrieval operation.
        student_service (IStudentService): Injected service implementation
            for accessing student data and business logic operations.

    Returns:
        list[StudentResponseDTO]: Complete list of all students in the system,
            each containing full student information including personal details,
            academic assignments, and metadata timestamps.

    Raises:
        NotFoundException: When no students exist in the system, indicating
            an empty database or all student records have been removed.
        ServerException: When an unexpected internal error occurs during
            data retrieval, such as database connectivity or query issues.

    Note:
        This endpoint returns all students without pagination. For systems
        with large student populations, consider using the paginated endpoint
        `/students/paginated` for better performance and user experience.

    Example:
        >>> GET /students
        >>> [
        ...     {
        ...         "id": 1,
        ...         "dni": "12345678",
        ...         "names": "John",
        ...         "paternal_surname": "Doe",
        ...         ...
        ...     }
        ... ]
    """
    return await student_service.get_all_students()


@router.get(
    "/search",
    response_model=StudentPageResponseDTO,
    summary="Search students with filters",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": StudentPageResponseDTO,
            "description": "Filtered students retrieved successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid search query or pagination parameters",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundException,
            "description": "No students found matching the search criteria",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error occurred",
        },
    },
    description="""
    Searches and filters students using multiple criteria including names, surnames, DNI, grade, and section information 
    with partial matching support. This endpoint provides advanced search capabilities with pagination support for 
    efficient data handling. The search query supports multiple terms and can match across different student fields 
    for flexible and comprehensive student discovery within the educational system.
    """,
)
@controller_handle_exceptions
async def search_students(
    request: Request,
    student_service: Annotated[IStudentService, Depends(get_student_service)],
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Number of items per page"),
    search_query: str = Query(
        description="Search query to filter students by name, surname, or DNI"
    ),
) -> StudentPageResponseDTO:
    """Search and filter students with advanced criteria and pagination.

    Performs flexible searching across multiple student fields including names,
    surnames, DNI, and academic information with partial matching support.
    Results are returned in paginated format for efficient data handling.

    Args:
        request (Request): The incoming HTTP request object containing headers
            and metadata for the search operation.
        student_service (IStudentService): Injected service implementation
            for handling search logic and data access operations.
        page (int, optional): Page number to retrieve (1-based indexing).
            Must be a positive integer. Defaults to 1.
        size (int, optional): Number of items per page. Must be between 1 and
            100 to ensure optimal performance. Defaults to 10.
        search_query (str): Search string used to filter students. Supports
            partial matching across names, surnames, DNI, and related fields.

    Returns:
        StudentPageResponseDTO: Paginated response containing matching students
            and pagination metadata including total count, current page, and
            navigation information.

    Raises:
        BadRequestException: When pagination parameters are invalid (negative
            or zero values) or search query format is malformed.
        NotFoundException: When no students match the provided search criteria,
            indicating the query returned empty results.
        ServerException: When an unexpected internal error occurs during
            the search operation, such as database query failures.

    Example:
        >>> GET /students/search?search_query=John&page=1&size=10
        >>> {
        ...     "data": [...],
        ...     "meta": {
        ...         "current_page": 1,
        ...         "per_page": 10,
        ...         "total": 5,
        ...         "total_pages": 1
        ...     }
        ... }
    """
    return await student_service.find_students(
        page=page,
        size=size,
        search_query=search_query,
    )


@router.get(
    "/paginated",
    response_model=StudentPageResponseDTO,
    summary="Get paginated students",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": StudentPageResponseDTO,
            "description": "Paginated students retrieved successfully",
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
    Retrieves students using basic pagination controls for efficient data browsing and display. This endpoint provides 
    simple pagination without filtering capabilities, making it ideal for displaying students in tables, lists, or grid 
    views where performance is important. The page size is configurable with a maximum limit of 100 items per page 
    to ensure optimal response times and prevent excessive data transfer.
    """,
)
@controller_handle_exceptions
async def get_paginated_students(
    request: Request,
    student_service: Annotated[IStudentService, Depends(get_student_service)],
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Number of items per page"),
) -> StudentPageResponseDTO:
    """Retrieve students with basic pagination controls.

    Provides efficient access to student data using simple pagination without
    filtering capabilities. Ideal for table displays, grid views, and general
    browsing interfaces where performance is prioritized.

    Args:
        request (Request): The incoming HTTP request object containing headers
            and metadata for the pagination request.
        student_service (IStudentService): Injected service implementation
            for handling paginated data retrieval and business logic.
        page (int, optional): Page number to retrieve using 1-based indexing.
            Must be a positive integer. Defaults to 1.
        size (int, optional): Number of items per page. Must be between 1 and
            100 to maintain optimal performance and prevent excessive data
            transfer. Defaults to 10.

    Returns:
        StudentPageResponseDTO: Paginated response containing the requested
            page of students and comprehensive pagination metadata including
            total count, current page, total pages, and navigation information.

    Raises:
        BadRequestException: When pagination parameters are invalid, such as
            negative page numbers, zero or negative page sizes, or values
            exceeding the maximum allowed limits.
        ServerException: When an unexpected internal error occurs during
            data retrieval, including database connectivity issues or
            query execution failures.

    Example:
        >>> GET /students/paginated?page=2&size=20
        >>> {
        ...     "data": [...],
        ...     "meta": {
        ...         "current_page": 2,
        ...         "per_page": 20,
        ...         "total": 150,
        ...         "total_pages": 8
        ...     }
        ... }
    """
    return await student_service.get_paginated_students(page=page, size=size)


@router.get(
    "/{student_id}",
    response_model=StudentResponseDTO,
    summary="Get student by ID",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": StudentResponseDTO,
            "description": "Student retrieved successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundException,
            "description": "Student not found with specified ID",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid student ID format",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error occurred",
        },
    },
    description="""
    Retrieves detailed information for a specific student using their unique identifier. This endpoint returns complete 
    student information including personal details, academic assignment (grade and section), and metadata such as 
    creation and update timestamps. The student ID must be a positive integer, and the system will return comprehensive 
    student details if the record exists. This is commonly used for student profile views, editing forms, or detailed reports.
    """,
)
@controller_handle_exceptions
async def get_student_by_id(
    request: Request,
    student_id: Annotated[
        int, Path(..., ge=1, description="The ID of the student to retrieve")
    ],
    student_service: Annotated[IStudentService, Depends(get_student_service)],
) -> StudentResponseDTO:
    """Retrieve detailed information for a specific student by their ID.

    Returns complete student information including personal details, academic
    assignments, and metadata timestamps. This endpoint is commonly used for
    student profile views, editing forms, and detailed reporting.

    Args:
        request (Request): The incoming HTTP request object containing headers
            and metadata for the retrieval operation.
        student_id (int): Unique identifier of the student to retrieve. Must
            be a positive integer representing an existing student record.
        student_service (IStudentService): Injected service implementation
            for accessing student data and handling business logic operations.

    Returns:
        StudentResponseDTO: Complete student information including personal
            details (DNI, names, surnames), academic assignment (grade and
            section), and metadata (creation and update timestamps).

    Raises:
        NotFoundException: When no student exists with the specified ID,
            indicating the record has been deleted or never existed.
        BadRequestException: When the student ID format is invalid, such as
            negative numbers, zero, or non-numeric values.
        ServerException: When an unexpected internal error occurs during
            data retrieval, including database connectivity or query issues.

    Example:
        >>> GET /students/123
        >>> {
        ...     "id": 123,
        ...     "dni": "12345678",
        ...     "names": "John",
        ...     "paternal_surname": "Doe",
        ...     "maternal_surname": "Smith",
        ...     "grade_id": 1,
        ...     "section_id": 1,
        ...     "created_at": "2023-01-01T10:00:00Z"
        ... }
    """
    return await student_service.get_student_by_id(student_id=student_id)


@router.put(
    "/{student_id}",
    response_model=StudentResponseDTO,
    summary="Update an existing student",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": StudentResponseDTO,
            "description": "Student updated successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundException,
            "description": "Student not found with specified ID",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid request data or student ID",
        },
        status.HTTP_409_CONFLICT: {
            "model": ConflictException,
            "description": "Student DNI already exists in system",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error occurred",
        },
    },
    description="""
    Updates the information of an existing student identified by their unique ID. This endpoint performs a complete 
    update of the student data with the provided information, maintaining data integrity and validation rules. The system 
    verifies that the student exists, validates the new data, and checks for DNI conflicts before applying changes. 
    All student DNIs must remain unique across the system to prevent duplicates and maintain data consistency.
    """,
)
@controller_handle_exceptions
async def update_student(
    request: Request,
    student_id: Annotated[
        int, Path(..., ge=1, description="The ID of the student to update")
    ],
    student_request: StudentRequestDTO,
    student_service: Annotated[IStudentService, Depends(get_student_service)],
) -> StudentResponseDTO:
    """Update an existing student's information with complete data validation.

    Performs a comprehensive update of student data while maintaining data
    integrity and validation rules. The system verifies student existence,
    validates new data, and ensures DNI uniqueness before applying changes.

    Args:
        request (Request): The incoming HTTP request object containing headers
            and metadata for the update operation.
        student_id (int): Unique identifier of the student to update. Must
            be a positive integer representing an existing student record.
        student_request (StudentRequestDTO): Data transfer object containing
            all updated student information including personal details, DNI,
            and academic assignment information.
        student_service (IStudentService): Injected service implementation
            for handling update logic and data persistence operations.

    Returns:
        StudentResponseDTO: Complete updated student information including
            all modified fields, unchanged data, and updated metadata
            timestamps reflecting the successful modification.

    Raises:
        NotFoundException: When no student exists with the specified ID,
            preventing the update operation from proceeding.
        BadRequestException: When the request data fails validation, including
            invalid student ID format, missing required fields, or malformed
            data in the update payload.
        ConflictException: When the new DNI already exists in the system
            for another student, preventing duplicate DNI entries.
        ServerException: When an unexpected internal error occurs during
            the update process, such as database connectivity or transaction
            management issues.

    Example:
        >>> PUT /students/123
        >>> {
        ...     "dni": "87654321",
        ...     "names": "Jane",
        ...     "paternal_surname": "Smith",
        ...     "maternal_surname": "Johnson",
        ...     "grade_id": 2,
        ...     "section_id": 1
        ... }
    """
    return await student_service.update_student(
        student_id=student_id, student_request=student_request
    )


@router.delete(
    "/{student_id}",
    response_model=MessageResponse,
    summary="Delete a student",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": MessageResponse,
            "description": "Student deleted successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundException,
            "description": "Student not found with specified ID",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid student ID format",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error occurred",
        },
    },
    description="""
    Permanently removes a student record from the educational system using their unique identifier. This operation is 
    irreversible and will completely delete the student record along with all associated academic data. The system 
    validates that the student exists and checks for any dependencies (such as attendance records or grades) before 
    performing the deletion. A confirmation message is returned upon successful completion of the delete operation.
    """,
)
@controller_handle_exceptions
async def delete_student(
    request: Request,
    student_id: Annotated[
        int, Path(..., ge=1, description="The ID of the student to delete")
    ],
    student_service: Annotated[IStudentService, Depends(get_student_service)],
) -> MessageResponse:
    """Permanently delete a student record from the educational system.

    Removes a student record completely from the system, including all
    associated academic data. This operation is irreversible and includes
    validation checks for student existence and dependency management.

    Args:
        request (Request): The incoming HTTP request object containing headers
            and metadata for the deletion operation.
        student_id (int): Unique identifier of the student to delete. Must
            be a positive integer representing an existing student record.
        student_service (IStudentService): Injected service implementation
            for handling deletion logic and data management operations.

    Returns:
        MessageResponse: Confirmation message indicating successful deletion
            with operation details, status information, and relevant metadata
            about the completed deletion process.

    Raises:
        NotFoundException: When no student exists with the specified ID,
            preventing the deletion operation from proceeding.
        BadRequestException: When the student ID format is invalid, such as
            negative numbers, zero, or non-numeric values provided in the
            request path.
        ServerException: When an unexpected internal error occurs during
            the deletion process, including database connectivity issues,
            transaction failures, or dependency constraint violations.

    Warning:
        This operation is irreversible. All student data including academic
        records, attendance history, and associated information will be
        permanently removed from the system.

    Example:
        >>> DELETE /students/123
        >>> {
        ...     "message": "Student deleted successfully.",
        ...     "success": true,
        ...     "status_code": 200,
        ...     "details": "Student with id '123' has been deleted."
        ... }
    """
    return await student_service.delete_student(student_id=student_id)
