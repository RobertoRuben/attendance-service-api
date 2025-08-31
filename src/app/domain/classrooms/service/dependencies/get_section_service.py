from typing import Annotated

from fastapi import Depends
from src.app.domain.classrooms.repository.dependencies import get_section_repository
from src.app.domain.classrooms.repository.interface import (
    ISectionRepository,
)
from src.app.domain.classrooms.service.implementations import (
    SectionServiceImpl,
)
from src.app.domain.classrooms.service.interface import ISectionService


async def get_section_service(
    section_repository: Annotated[ISectionRepository, Depends(get_section_repository)],
) -> ISectionService:
    """
    Get section service.

    This FastAPI dependency provides an instance of the section service.

    Args:
        section_repository (Annotated[ISectionRepository, Depends]): Section repository dependency.

    Returns:
        ISectionService: Section service implementation.
    """
    return SectionServiceImpl(section_repository=section_repository)
