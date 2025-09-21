from src.app.core.strategies.storage.factory import FileStorageStrategyFactory
from src.app.core.strategies.storage.enum import StorageType
from src.app.core.config import settings


def get_file_storage_factory() -> FileStorageStrategyFactory:
    """Return a FileStorageStrategyFactory instance.

    This function provides a factory instance that can be used to create
    concrete storage strategies (for example, local or cloud-based
    implementations). The factory itself is lightweight and created on each
    call; if a singleton factory is required, the caller should cache it.

    Returns:
        FileStorageStrategyFactory: A new factory instance.
    """
    return FileStorageStrategyFactory()


def create_local_strategy():
    """Create a local storage strategy configured from application settings.

    Uses the FileStorageStrategyFactory to instantiate a local filesystem
    strategy configured using values from the global settings.

    Returns:
        Any: Concrete storage strategy instance created by the factory. The
            exact type depends on the factory implementation (commonly a class
            implementing the FileStorageStrategy interface).

    Raises:
        KeyError: If expected settings (e.g. LOCAL_STORAGE_PATH) are missing.
        ValueError: If the factory rejects the provided configuration.
    """
    return FileStorageStrategyFactory.create_strategy(
        StorageType.LOCAL,
        base_path=settings.LOCAL_STORAGE_PATH,
        create_dirs=settings.STORAGE_CREATE_DIRS,
    )
