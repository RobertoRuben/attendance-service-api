from fastapi import UploadFile

from src.app.core.model.file_upload_response import FileUploadResponse
from src.app.core.model.message_response import MessageResponse
from src.app.core.strategies.storage.context.file_storage_context import (
    FileStorageContext,
)
from src.app.core.strategies.storage.enum import StorageType
from src.app.core.strategies.storage.factory import FileStorageStrategyFactory


class FileStorageService:
    """Service for managing file storage operations.

    This service delegates file operations to a storage strategy wrapped by
    FileStorageContext. The storage strategy can be switched at runtime.

    Attributes:
        context (FileStorageContext): Context that holds current strategy.
        current_storage_type (StorageType): Currently selected storage backend.
    """

    def __init__(self, storage_type: StorageType = StorageType.LOCAL, **config):
        """Initialize service with a storage strategy.

        Args:
            storage_type (StorageType): Initial storage backend to use.
            **config: Additional configuration forwarded to the strategy factory.

        Returns:
            None

        Raises:
            Exception: Propagates factory/strategy initialization errors.
        """
        strategy = FileStorageStrategyFactory.create_strategy(storage_type, **config)
        self.context = FileStorageContext(strategy)
        self.current_storage_type = storage_type

    def switch_storage(self, storage_type: StorageType, **kwargs) -> None:
        """Switch to a different storage strategy at runtime.

        Args:
            storage_type (StorageType): New storage backend to switch to.
            **kwargs: Configuration forwarded to the strategy factory.

        Returns:
            None

        Raises:
            Exception: Propagates factory/strategy initialization errors.
        """
        new_strategy = FileStorageStrategyFactory.create_strategy(
            storage_type, **kwargs
        )
        self.context.set_strategy(new_strategy)
        self.current_storage_type = storage_type

    def get_current_storage_type(self) -> StorageType:
        """Return the currently configured storage type.

        Returns:
            StorageType: The current storage backend enum value.
        """
        return self.current_storage_type

    async def upload_file(self, file: UploadFile, filename: str) -> FileUploadResponse:
        """Upload a file using the active storage strategy.

        Args:
            file (UploadFile): File received from FastAPI to be uploaded.
            filename (str): Target filename to persist (e.g. generated UUID + ext).

        Returns:
            FileUploadResponse: Metadata about the stored file.

        Raises:
            Exception: Strategy-specific upload errors may be raised.
        """
        return await self.context.upload_file(file, filename)

    async def delete_file(self, file_path: str) -> MessageResponse:
        """Delete a file using the active storage strategy.

        Args:
            file_path (str): Path or identifier of the file to delete.

        Returns:
            MessageResponse: Result of the deletion operation.

        Raises:
            Exception: Strategy-specific deletion errors may be raised.
        """
        return await self.context.delete_file(file_path)

    async def get_file_url(self, file_path: str) -> str:
        """Get an accessible URL for a stored file.

        Args:
            file_path (str): Storage path or identifier for the file.

        Returns:
            str: Publicly accessible URL (or internal URL) for the file.

        Raises:
            Exception: Strategy-specific errors may be raised.
        """
        return await self.context.get_file_url(file_path)

    async def file_exists(self, file_path: str) -> bool:
        """Check whether a file exists in the active storage.

        Args:
            file_path (str): Storage path or identifier to check.

        Returns:
            bool: True if the file exists, False otherwise.

        Raises:
            Exception: Strategy-specific errors may be raised.
        """
        return await self.context.file_exists(file_path)

    async def get_file_size(self, file_path: str) -> int:
        """Get the size of a stored file in bytes.

        Args:
            file_path (str): Storage path or identifier for the file.

        Returns:
            int: Size in bytes. Implementations may return -1 if file is missing.

        Raises:
            Exception: Strategy-specific errors may be raised.
        """
        return await self.context.get_file_size(file_path)
