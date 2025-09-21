from functools import lru_cache
from src.app.core.strategies.storage.service.storage_service import FileStorageService
from src.app.core.strategies.storage.enum import StorageType
from src.app.core.config import settings


@lru_cache()
def get_file_storage_service() -> FileStorageService:
    """Return a cached FileStorageService instance for dependency injection.

    This function is intended to be used as a FastAPI dependency provider.
    The LRU cache decorator ensures the service instance is created once and
    reused (singleton-like behavior) for the lifetime of the process. The
    service is configured using application settings.

    Returns:
        FileStorageService: A configured and cached storage service instance.

    Raises:
        ValueError: If settings.STORAGE_TYPE cannot be converted to a valid
            StorageType enum member.
    """
    storage_type = StorageType(settings.STORAGE_TYPE)

    return FileStorageService(
        storage_type=storage_type,
        base_path=settings.LOCAL_STORAGE_PATH,
        create_dirs=settings.STORAGE_CREATE_DIRS,
    )


def get_file_storage_service_factory() -> FileStorageService:
    """Create and return a fresh FileStorageService instance.

    Unlike get_file_storage_service, this factory function does not cache the
    created instance. Use it when a new service instance per consumer is
    required (for testing or transient lifecycles).

    Returns:
        FileStorageService: A newly created storage service configured from
            application settings.

    Raises:
        ValueError: If settings.STORAGE_TYPE is invalid.
    """
    storage_type = StorageType(settings.STORAGE_TYPE)

    return FileStorageService(
        storage_type=storage_type,
        base_path=settings.LOCAL_STORAGE_PATH,
        create_dirs=settings.STORAGE_CREATE_DIRS,
    )
