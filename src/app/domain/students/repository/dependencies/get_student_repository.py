from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.app.core.db.dependencies import get_async_session
from src.app.core.repository.implementation import BaseRepository
from src.app.domain.students.model import Student
from src.app.domain.students.repository.interface import IStudentRepository


async def get_student_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> IStudentRepository:
    """
    Get the student repository.

    Args:
        session (Annotated[AsyncSession, Depends]): The database session.

    Returns:
        IStudentRepository: The student repository.
    """
    return BaseRepository(session=session, entity_class=Student)
