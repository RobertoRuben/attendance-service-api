from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.app.core.db.dependencies import get_async_session
from src.app.domain.students.repository.implementations import StudentRepositoryImpl
from src.app.domain.students.repository.interface import IStudentRepository


async def get_student_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> IStudentRepository:
    """Create and return a student repository instance.

    This dependency injection function provides a configured student
    repository for use in FastAPI endpoints. It creates a BaseRepository
    instance specialized for Student entities with an active database session.

    The function serves as a factory for student repository instances,
    ensuring proper database session management through FastAPI's
    dependency injection system.

    Args:
        session: Asynchronous database session injected by FastAPI.
            Automatically managed lifecycle (created per request,
            closed after response).

    Returns:
        IStudentRepository: A repository instance configured for Student
            operations with the provided database session. The instance
            provides all CRUD operations defined in the interface.

    Note:
        This function is designed to be used with FastAPI's Depends()
        mechanism. The database session is automatically injected and
        managed by the framework's dependency system.
    """
    return StudentRepositoryImpl(session=session)
