from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.core.db.database import AsyncSessionLocal


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an AsyncSession configured with:
      - expire_on_commit=False  (mantiene los objetos en memoria tras commit)
      - autoflush=False         (flush explícito con @transactional)

    Cada petición de FastAPI obtendrá su propia sesión asíncrona,
    y se cerrará automáticamente al terminar el request.
    """
    async with AsyncSessionLocal() as session:
        yield session
