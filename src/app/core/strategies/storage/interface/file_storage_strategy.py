from abc import ABC, abstractmethod
from fastapi import UploadFile

from src.app.core.model.file_upload_response import FileUploadResponse
from src.app.core.model.message_response import MessageResponse


class FileStorageStrategy(ABC):
    """Abstract strategy interface for storing files.

    Implementations should provide asynchronous methods to upload and delete
    files. This interface allows the rest of the application to remain storage
    backend agnostic.

    Methods:
        upload_file: Store the provided UploadFile under the given filename and
            return the resulting file path or URL.
        delete_file: Remove the file identified by file_path and return whether
            the deletion succeeded.
        get_file_url_async: Get URL for accessing a stored file.
        file_exists_async: Check if a file exists in storage.
        get_file_size_async: Get the size of a stored file.
    """

    @abstractmethod
    async def upload_file(self, file: UploadFile, filename: str) -> FileUploadResponse:
        """Upload a file and return metadata about the stored file.

        Args:
            file (fastapi.UploadFile): Incoming file object to be stored.
            filename (str): Target filename to use when persisting the file
                (typically a generated UUID with extension).

        Returns:
            FileUploadResponse: Metadata about the uploaded file including its
                storage path or URL, original name, content type, size and upload time.

        Raises:
            Exception: Implementation-specific exceptions may be raised on failure.
        """
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> MessageResponse:
        """Delete a stored file identified by file_path.

        Args:
            file_path (str): The path or URL of the file to delete.

        Returns:
            MessageResponse: Result of the deletion operation including success
                status and any relevant details.

        Raises:
            Exception: Implementation-specific exceptions may be raised on failure.
        """
        pass

    @abstractmethod
    async def get_file_url_async(self, file_path: str) -> str:
        """Return an accessible URL for a stored file.

        Args:
            file_path (str): Storage path or identifier for the file.

        Returns:
            str: A URL that can be used to access the file.

        Raises:
            Exception: Implementation-specific exceptions may be raised on failure.
        """
        pass

    @abstractmethod
    async def file_exists_async(self, file_path: str) -> bool:
        """Check asynchronously whether a file exists in storage.

        Args:
            file_path (str): Storage path or identifier to check.

        Returns:
            bool: True if the file exists, False otherwise.

        Raises:
            Exception: Implementation-specific exceptions may be raised on failure.
        """
        pass

    @abstractmethod
    async def get_file_size_async(self, file_path: str) -> int:
        """Return the size of a stored file in bytes.

        Args:
            file_path (str): Storage path or identifier for the file.

        Returns:
            int: Size of the file in bytes. May return -1 if the file does not exist
                depending on implementation.

        Raises:
            Exception: Implementation-specific exceptions may be raised on failure.
        """
        pass
