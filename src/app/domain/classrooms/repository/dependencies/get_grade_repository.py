from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.app.core.db.dependencies import get_async_session
from src.app.core.repository.implementation import BaseRepository
from src.app.domain.classrooms.model import Grade
from src.app.domain.classrooms.repository.interface import IGradeRepository


async def get_grade_repository(
    session: AsyncSession = Depends(get_async_session),
) -> IGradeRepository:
    """
    Get an instance of IGradeRepository.

    Args:
        session (AsyncSession): The database session. Defaults to Depends(get_async_session).

    Returns:
        IGradeRepository: An instance of IGradeRepository.
    """
    return BaseRepository(session=session, entity_class=Grade)
