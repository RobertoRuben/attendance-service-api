from typing import Annotated
from fastapi import Depends

from src.app.domain.classrooms.repository.dependencies import (
    get_grade_repository,
)
from src.app.domain.classrooms.repository.interface import (
    IGradeRepository,
)
from src.app.domain.classrooms.service.implementations import (
    GradeServiceImpl,
)
from src.app.domain.classrooms.service.interface import IGradeService


async def get_grade_service(
    grade_repository: Annotated[IGradeRepository, Depends(get_grade_repository)],
) -> IGradeService:
    """
    Dependency function to get the grade service implementation.

    This function provides an instance of the grade service implementation
    by injecting the required grade repository dependency.

    Args:
        grade_repository: The grade repository implementation provided by
            the dependency injection system.

    Returns:
        IGradeService: An instance of the grade service implementation.
    """
    return GradeServiceImpl(grade_repository=grade_repository)
