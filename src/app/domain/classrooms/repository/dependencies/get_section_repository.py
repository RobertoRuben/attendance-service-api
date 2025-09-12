from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.app.core.db.dependencies import get_async_session
from src.app.core.repository.implementation import BaseRepository
from src.app.domain.classrooms.model import Section
from src.app.domain.classrooms.repository.interface import ISectionRepository


async def get_section_repository(
    session: AsyncSession = Depends(get_async_session),
) -> ISectionRepository:
    """
    Get Section repository.

    Args:
        session (AsyncSession): The database session to use. Defaults to Depends(get_async_session).

    Returns:
        ISectionRepository: The section repository instance.
    """
    return BaseRepository(session=session, entity_class=Section)
