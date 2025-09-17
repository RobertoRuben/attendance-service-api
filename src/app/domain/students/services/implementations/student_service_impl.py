import pendulum

from src.app.core.exception import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from src.app.core.exception.decorator import (
    service_handle_exceptions,
)
from src.app.core.model import MessageResponse
from src.app.domain.classrooms.repository.interface import (
    IGradeRepository,
    ISectionRepository,
)
from src.app.domain.students.dto.request import StudentRequestDTO
from src.app.domain.students.dto.response import (
    StudentPageResponseDTO,
    StudentResponseDTO,
)
from src.app.domain.students.model import Student
from src.app.domain.students.repository.interface import (
    IStudentRepository,
)
from src.app.domain.students.services.interface import IStudentService


class StudentServiceImpl(IStudentService):
    """Concrete implementation of the IStudentService interface.

    This service coordinates student-related business logic, including validation
    against related repositories (grade and section), conflict detection, and
    mapping between domain models and DTOs. All public methods are decorated to
    handle domain exceptions consistently.

    Attributes:
        student_repository (IStudentRepository): Repository for student persistence operations.
        grade_repository (IGradeRepository): Repository used to validate grade existence.
        section_repository (ISectionRepository): Repository used to validate section existence.
    """

    def __init__(
        self,
        student_repository: IStudentRepository,
        grade_repository: IGradeRepository,
        section_repository: ISectionRepository,
    ):
        """Initialize the StudentServiceImpl.

        Args:
            student_repository (IStudentRepository): Repository for student data access.
            grade_repository (IGradeRepository): Repository for grade verification.
            section_repository (ISectionRepository): Repository for section verification.
        """
        self.student_repository = student_repository
        self.grade_repository = grade_repository
        self.section_repository = section_repository

    @service_handle_exceptions
    async def create_student(
        self, student_request: StudentRequestDTO
    ) -> StudentResponseDTO:
        """Create a new student after validating related entities and uniqueness.

        Validations performed:
            - Grade existence (raises NotFoundException if missing).
            - Section existence (raises NotFoundException if missing).
            - Unique DNI (raises ConflictException if already in use).

        Args:
            student_request (StudentRequestDTO): DTO containing the student data to create.

        Returns:
            StudentResponseDTO: DTO representing the created student.

        Raises:
            NotFoundException: If grade or section referenced do not exist.
            ConflictException: If the DNI is already used by another student.
        """
        if not (await self.grade_repository.exists_by(id=student_request.grade_id)):
            raise NotFoundException(
                message="Grade not found.",
                details=f"Grade with id '{student_request.grade_id}' does not exist.",
            )

        if not (await self.section_repository.exists_by(id=student_request.section_id)):
            raise NotFoundException(
                message="Section not found.",
                details=f"Section with id '{student_request.section_id}' does not exist.",
            )

        if await self.student_repository.exists_by(dni=student_request.dni):
            raise ConflictException(
                message="DNI already in use.",
                details=f"A student with DNI '{student_request.dni}' already exists.",
            )

        new_student = Student.model_validate(student_request)

        created_student = await self.student_repository.save(new_student)

        return StudentResponseDTO.model_validate(created_student)

    @service_handle_exceptions
    async def get_all_students(self) -> list[StudentResponseDTO]:
        """Retrieve all students from the repository.

        Notes:
            This method raises NotFoundException if there are no students in the system.

        Returns:
            list[StudentResponseDTO]: A list of student DTOs.

        Raises:
            NotFoundException: If no students are found.
        """
        if not (students := await self.student_repository.get_all()):
            raise NotFoundException(
                message="No students found.",
                details="There are no students in the system.",
            )

        return [StudentResponseDTO.model_validate(student) for student in students]

    @service_handle_exceptions
    async def update_student(
        self, student_id, student_request: StudentRequestDTO
    ) -> StudentResponseDTO:
        """Update an existing student's data.

        The method ensures the student exists, validates DNI uniqueness if changed,
        and applies the update. The updated_at timestamp is set to the current
        time in the 'America/Lima' timezone.

        Args:
            student_id (int): Identifier of the student to update.
            student_request (StudentRequestDTO): DTO containing fields to update.

        Returns:
            StudentResponseDTO: DTO representing the updated student.

        Raises:
            NotFoundException: If the student does not exist.
            ConflictException: If the new DNI is already in use by another student.
        """
        existing_student = await self.student_repository.get_by_id(student_id)

        if not existing_student:
            raise NotFoundException(
                message="Student not found.",
                details=f"Student with id '{student_id}' does not exist.",
            )
            
        if not (await self.grade_repository.exists_by(id=student_request.grade_id)):
            raise NotFoundException(
                message="Grade not found.",
                details=f"Grade with id '{student_request.grade_id}' does not exist.",
            )
            
        if not (await self.section_repository.exists_by(id=student_request.section_id)):
            raise NotFoundException(
                message="Section not found.",
                details=f"Section with id '{student_request.section_id}' does not exist.",
            )

        if existing_student.dni != student_request.dni:
            if await self.student_repository.exists_by(dni=student_request.dni):
                raise ConflictException(
                    message="DNI already in use.",
                    details=f"A student with DNI '{student_request.dni}' already exists.",
                )

        update_data = student_request.model_dump() | {
            "updated_at": pendulum.now("America/Lima"),
        }
        
        print("Update data:")
        print(update_data)

        updated_student = await self.student_repository.update_by_id(
            student_id, update_data
        )

        return StudentResponseDTO.model_validate(updated_student)

    @service_handle_exceptions
    async def delete_student(self, student_id: int) -> MessageResponse:
        """Delete a student by its identifier.

        Args:
            student_id (int): Identifier of the student to delete.

        Returns:
            MessageResponse: Message indicating successful deletion.

        Raises:
            NotFoundException: If the student does not exist.
        """
        if not (await self.student_repository.exists_by(id=student_id)):
            raise NotFoundException(
                message="Student not found.",
                details=f"Student with id '{student_id}' does not exist.",
            )

        await self.student_repository.delete_by_id(student_id)

        return MessageResponse(
            message="Student deleted successfully.",
            success=True,
            status_code=200,
            details=f"Student with id '{student_id}' has been deleted.",
        )

    @service_handle_exceptions
    async def get_student_by_id(self, student_id: int) -> StudentResponseDTO:
        """Retrieve a single student by its identifier.

        Args:
            student_id (int): Identifier of the student to retrieve.

        Returns:
            StudentResponseDTO: DTO representing the found student.

        Raises:
            NotFoundException: If the student does not exist.
        """
        if not (student := await self.student_repository.get_by_id(student_id)):
            raise NotFoundException(
                message="Student not found.",
                details=f"Student with id '{student_id}' does not exist.",
            )

        return StudentResponseDTO.model_validate(student)

    @service_handle_exceptions
    async def get_paginated_students(
        self, page: int, size: int
    ) -> StudentPageResponseDTO:
        """Return a paginated list of students with validation for pagination params.

        Args:
            page (int): 1-based page number to retrieve. Must be >= 1.
            size (int): Number of items per page. Must be >= 1.

        Returns:
            StudentPageResponseDTO: DTO containing paginated student DTOs and metadata.

        Raises:
            BadRequestException: If page or size are not positive integers.
        """
        if page < 1 or size < 1:
            raise BadRequestException(
                message="Invalid pagination parameters.",
                details="Page and size must be positive integers.",
            )

        page_result = await self.student_repository.get_pageable_students(page, size)
        items = [
            StudentResponseDTO.model_validate(student) for student in page_result.data
        ]

        return StudentPageResponseDTO(data=items, meta=page_result.meta)

    @service_handle_exceptions
    async def find_students(
        self, page: int, size: int, search_query: str
    ) -> StudentPageResponseDTO:
        """Find students by a search query with pagination.

        Validates pagination parameters, delegates searching to the repository,
        and maps results into response DTOs. If no results are found, a
        NotFoundException is raised.

        Args:
            page (int): 1-based page number to retrieve. Must be >= 1.
            size (int): Number of items per page. Must be >= 1.
            search_query (str): Search string used to filter students.

        Returns:
            StudentPageResponseDTO: DTO containing matching student DTOs and pagination metadata.

        Raises:
            BadRequestException: If page or size are not positive integers.
            NotFoundException: If no students match the provided search query.
        """
        if page < 1 or size < 1:
            raise BadRequestException(
                message="Invalid pagination parameters.",
                details="Page and size must be positive integers.",
            )

        page_result = await self.student_repository.find(page, size, search_query)

        if not page_result.data:
            raise NotFoundException(
                message="No students found matching the criteria.",
                details=f"No students match the search query '{search_query}'.",
            )

        items = [
            StudentResponseDTO.model_validate(student) for student in page_result.data
        ]

        return StudentPageResponseDTO(data=items, meta=page_result.meta)
