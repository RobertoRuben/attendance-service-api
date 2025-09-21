from src.app.core.strategies.storage.interface import FileStorageStrategy
from src.app.core.strategies.storage.implementations.local_file_storage_strategy import (
    LocalFileStorageStrategy,
)
from src.app.core.strategies.storage.enum import StorageType
from src.app.core.exception import ServerException
from src.app.core.config import settings


class FileStorageStrategyFactory:
    """Factory for creating file storage strategy instances.

    This factory maps StorageType enum members to concrete strategy classes
    and provides several helpers to create configured strategy instances
    (direct creation, creation from settings, and convenience defaults).
    It also allows runtime registration of additional strategies.

    Attributes:
        _strategies (dict[StorageType, type[FileStorageStrategy]]): Mapping of
            supported storage types to their implementing classes.
    """

    _strategies: dict[StorageType, type[FileStorageStrategy]] = {
        StorageType.LOCAL: LocalFileStorageStrategy,
        # StorageType.S3: S3FileStorageStrategy,  # To implement later
        # StorageType.AZURE: AzureFileStorageStrategy,  # To implement later
    }

    @classmethod
    def create_strategy(
        cls, storage_type: StorageType, **kwargs
    ) -> FileStorageStrategy:
        """Create and return a configured file storage strategy.

        The method looks up the concrete strategy class for the given
        StorageType and instantiates it with the provided keyword arguments.

        Args:
            storage_type (StorageType): Enum member specifying which strategy
                to create.
            **kwargs: Strategy-specific configuration parameters forwarded to
                the strategy class constructor (for example base_path,
                create_dirs, credentials, etc.).

        Returns:
            FileStorageStrategy: An instance of the requested strategy class.

        Raises:
            ServerException: If the requested storage_type is not supported.
        """
        if storage_type not in cls._strategies:
            raise ServerException(
                message=f"Storage type {storage_type.value} is not supported", code=500
            )

        strategy_class = cls._strategies[storage_type]
        return strategy_class(**kwargs)

    @classmethod
    def create_from_settings(cls) -> FileStorageStrategy:
        """Create a strategy instance using application settings.

        The function reads settings.STORAGE_TYPE and other relevant settings
        (for example LOCAL_STORAGE_PATH) and returns a properly configured
        strategy instance.

        Returns:
            FileStorageStrategy: Configured strategy based on application
                settings.

        Raises:
            ValueError: If settings.STORAGE_TYPE cannot be converted to a valid
                StorageType enum member.
        """
        storage_type = StorageType(settings.STORAGE_TYPE)

        if storage_type == StorageType.LOCAL:
            return cls.create_strategy(
                storage_type,
                base_path=settings.LOCAL_STORAGE_PATH,
                create_dirs=settings.STORAGE_CREATE_DIRS,
            )

        # Add additional configuration branches for S3, Azure, etc. as needed.
        return cls.create_strategy(storage_type)

    @classmethod
    def create_default_local_strategy(cls) -> FileStorageStrategy:
        """Create a local filesystem strategy using default application settings.

        This convenience helper returns a LocalFileStorageStrategy instance
        configured from environment/application settings (e.g. LOCAL_STORAGE_PATH,
        STORAGE_CREATE_DIRS).

        Returns:
            FileStorageStrategy: Local strategy configured from settings.

        Raises:
            ValueError: If settings contain invalid values for the storage type
                or required settings are missing.
        """
        return cls.create_strategy(
            StorageType.LOCAL,
            base_path=settings.LOCAL_STORAGE_PATH,
            create_dirs=settings.STORAGE_CREATE_DIRS,
        )

    @classmethod
    def register_strategy(
        cls, storage_type: StorageType, strategy_class: type[FileStorageStrategy]
    ) -> None:
        """Register or override a storage strategy implementation.

        This allows registering custom strategy classes at runtime so that
        subsequent calls to create_strategy recognize the new implementation.

        Args:
            storage_type (StorageType): Enum member to register.
            strategy_class (type[FileStorageStrategy]): Concrete class that
                implements the FileStorageStrategy interface.

        Returns:
            None
        """
        cls._strategies[storage_type] = strategy_class

    @classmethod
    def get_available_strategies(cls) -> list[StorageType]:
        """Return the list of supported storage types.

        Returns:
            list[StorageType]: Available StorageType enum members supported
                by the factory.
        """
        return list(cls._strategies.keys())

    @classmethod
    def is_strategy_supported(cls, storage_type: StorageType) -> bool:
        """Check whether a given storage type is supported by the factory.

        Args:
            storage_type (StorageType): Storage type to check.

        Returns:
            bool: True if the storage type is registered, False otherwise.
        """
        return storage_type in cls._strategies
