from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.app.core.db.dependencies import get_async_session
from src.app.core.repository.implementation import BaseRepository
from src.app.domain.users.model import User
from src.app.domain.users.repository import IUserRepository


async def get_user_repository(
    session: AsyncSession = Depends(get_async_session),
) -> IUserRepository:
    """Provide a user repository implementation.

    This function is intended to be used as a FastAPI dependency. It receives an
    AsyncSession (injected via get_async_session) and returns a repository
    implementation for the User entity using BaseRepository.

    Args:
        session (AsyncSession): Async SQLAlchemy session injected by FastAPI.

    Returns:
        IUserRepository: An instance of a repository that implements IUserRepository
            and is configured to operate on the User entity.
    """
    return BaseRepository(session=session, entity_class=User)
