from typing import Annotated

from fastapi import Depends
from src.app.domain.classrooms.repository.dependencies import (
    get_grade_repository,
    get_section_repository,
)
from src.app.domain.classrooms.repository.interface import (
    IGradeRepository,
    ISectionRepository,
)
from src.app.domain.students.repository.dependencies import (
    get_student_repository,
)
from src.app.domain.students.repository.interface import (
    IStudentRepository,
)
from src.app.domain.students.services.implementations import (
    StudentServiceImpl,
)
from src.app.domain.students.services.interface import IStudentService


async def get_student_service(
    student_repository: Annotated[IStudentRepository, Depends(get_student_repository)],
    grade_repository: Annotated[IGradeRepository, Depends(get_grade_repository)],
    section_repository: Annotated[ISectionRepository, Depends(get_section_repository)],
) -> IStudentService:
    """Create and return a StudentServiceImpl dependency.

    This factory function is used by FastAPI's dependency injection system to
    construct a StudentServiceImpl configured with the required repositories.
    The repositories themselves are provided as dependencies via `Depends`.

    Args:
        student_repository (IStudentRepository): Repository for student data,
            injected by FastAPI using `get_student_repository`.
        grade_repository (IGradeRepository): Repository for grade data,
            injected by FastAPI using `get_grade_repository`.
        section_repository (ISectionRepository): Repository for section data,
            injected by FastAPI using `get_section_repository`.

    Returns:
        IStudentService: An instance of StudentServiceImpl wired with the
            provided repositories.

    Raises:
        Any exception raised during dependency resolution will propagate to the
        FastAPI request lifecycle (for example, configuration or initialization
        errors from repository factories).

    Example:
        In a route definition you can depend on this service:

        @router.get("/students")
        async def list_students(service: IStudentService = Depends(get_student_service)):
            return await service.get_paginated_students(page=1, size=10)
    """
    return StudentServiceImpl(
        student_repository=student_repository,
        grade_repository=grade_repository,
        section_repository=section_repository,
    )
