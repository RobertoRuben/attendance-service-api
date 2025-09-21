from fastapi import UploadFile

from src.app.core.model.file_upload_response import FileUploadResponse
from src.app.core.model.message_response import MessageResponse
from src.app.core.strategies.storage.interface import FileStorageStrategy


class FileStorageContext:
    """Context for file storage operations using the Strategy pattern.

    This class provides a unified interface to perform file storage operations
    (upload, delete, existence check, size retrieval and URL generation) using
    interchangeable storage strategies (for example: local filesystem, S3,
    etc.). Use set_strategy to swap implementations at runtime.

    Attributes:
        _strategy (FileStorageStrategy | None): The active storage strategy.
            May be None until set via set_strategy().
    """

    def __init__(self, strategy: FileStorageStrategy | None = None):
        """Initialize the context.

        Args:
            strategy (FileStorageStrategy | None): Optional initial storage
                strategy. If None, a strategy must be set via set_strategy()
                before invoking other methods.
        """
        self._strategy = strategy

    def set_strategy(self, strategy: FileStorageStrategy) -> None:
        """Set or replace the current storage strategy.

        Args:
            strategy (FileStorageStrategy): Strategy instance to use for
                subsequent storage operations.
        """
        self._strategy = strategy

    def get_strategy(self) -> FileStorageStrategy | None:
        """Return the current storage strategy.

        Returns:
            FileStorageStrategy | None: The configured storage strategy, or
            None if no strategy has been set.
        """
        return self._strategy

    async def upload_file(self, file: UploadFile, filename: str) -> FileUploadResponse:
        """Upload a file using the configured storage strategy.

        Args:
            file (UploadFile): The file-like object to upload.
            filename (str): The target filename or key to store the file as.

        Returns:
            FileUploadResponse: Metadata or result returned by the strategy.

        Raises:
            ValueError: If no strategy is configured.
            Exception: Any strategy-specific exception raised during upload is
                propagated.
        """
        if not self._strategy:
            raise ValueError("No storage strategy configured")

        return await self._strategy.upload_file(file, filename)

    async def delete_file(self, file_path: str) -> MessageResponse:
        """Delete a file using the configured storage strategy.

        Args:
            file_path (str): Path or key of the file to delete.

        Returns:
            MessageResponse: Response or message returned by the strategy
            indicating result of the deletion.

        Raises:
            ValueError: If no strategy is configured.
            Exception: Any strategy-specific exception raised during deletion is
                propagated.
        """
        if not self._strategy:
            raise ValueError("No storage strategy configured")

        return await self._strategy.delete_file(file_path)

    async def get_file_url(self, file_path: str) -> str:
        """Obtain a URL for the specified file using the configured strategy.

        The method expects the strategy to implement an asynchronous method
        named get_file_url_async. That method may return a public URL or a
        presigned URL depending on the strategy implementation.

        Args:
            file_path (str): Path or key of the file.

        Returns:
            str: URL that can be used to access the file.

        Raises:
            ValueError: If no strategy is configured.
            NotImplementedError: If the current strategy does not implement
                get_file_url_async.
        """
        if not self._strategy:
            raise ValueError("No storage strategy configured")

        # Check if strategy has this method
        if hasattr(self._strategy, "get_file_url_async"):
            return await self._strategy.get_file_url_async(file_path)
        else:
            raise NotImplementedError("Current strategy doesn't support get_file_url")

    async def file_exists(self, file_path: str) -> bool:
        """Check whether the specified file exists using the configured strategy.

        Args:
            file_path (str): Path or key of the file to check.

        Returns:
            bool: True if the file exists, False otherwise.

        Raises:
            ValueError: If no strategy is configured.
            NotImplementedError: If the current strategy does not implement
                file_exists_async.
        """
        if not self._strategy:
            raise ValueError("No storage strategy configured")

        # Check if strategy has this method
        if hasattr(self._strategy, "file_exists_async"):
            return await self._strategy.file_exists_async(file_path)
        else:
            raise NotImplementedError("Current strategy doesn't support file_exists")

    async def get_file_size(self, file_path: str) -> int:
        """Get the size of the specified file in bytes using the configured strategy.

        Args:
            file_path (str): Path or key of the file.

        Returns:
            int: File size in bytes. A strategy may return -1 or raise if the
            file is not found; consult the strategy implementation.

        Raises:
            ValueError: If no strategy is configured.
            NotImplementedError: If the current strategy does not implement
                get_file_size_async.
        """
        if not self._strategy:
            raise ValueError("No storage strategy configured")

        # Check if strategy has this method
        if hasattr(self._strategy, "get_file_size_async"):
            return await self._strategy.get_file_size_async(file_path)
        else:
            raise NotImplementedError("Current strategy doesn't support get_file_size")
