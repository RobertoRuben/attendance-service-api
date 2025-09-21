import os
import aiofiles
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile

from src.app.core.config import settings
from src.app.core.model.file_upload_response import FileUploadResponse
from src.app.core.model.message_response import MessageResponse
from src.app.core.strategies.storage.interface import FileStorageStrategy
from src.app.core.exception import ServerException
from src.app.core.strategies.storage.helpers import FileValidator, PathHelper


class LocalFileStorageStrategy(FileStorageStrategy):
    """Local file system storage implementation.

    This strategy stores uploaded files in a local directory structure.
    It is suitable for development and small-scale deployments.

    Attributes:
        base_path (Path): Base directory where files are stored.
    """

    def __init__(self, base_path: str = None, create_dirs: bool = None):
        """Initialize the local storage strategy.

        Args:
            base_path (str, optional): Base directory where files will be stored.
                If None, the value from settings.LOCAL_STORAGE_PATH is used.
            create_dirs (bool, optional): Whether to create directories if they
                don't exist. If None, the value from settings.STORAGE_CREATE_DIRS
                is used.
        """
        if base_path is None:
            base_path = settings.LOCAL_STORAGE_PATH
        if create_dirs is None:
            create_dirs = settings.STORAGE_CREATE_DIRS

        self.base_path = Path(base_path)
        if create_dirs:
            os.makedirs(self.base_path, exist_ok=True)

    async def upload_file(self, file: UploadFile, filename: str) -> FileUploadResponse:
        """Upload a file to local storage.

        The method validates the uploaded file (type, filename and size),
        writes it asynchronously to the configured base directory and returns
        a FileUploadResponse with metadata.

        Args:
            file (UploadFile): File to upload.
            filename (str): Target filename (should include extension).

        Returns:
            FileUploadResponse: Metadata about the uploaded file.

        Raises:
            ServerException: If validation fails or an error occurs while saving.
        """
        try:
            # Validate file is an image
            if not FileValidator.is_valid_image(file.content_type):
                raise ServerException(
                    message="Invalid file type. Only images are allowed.",
                    details=f"Content type '{file.content_type}' is not supported",
                    code=400,
                )

            if not FileValidator.is_safe_filename(filename):
                raise ServerException(
                    message="Invalid filename",
                    details=f"Filename '{filename}' contains invalid characters",
                    code=400,
                )

            await file.seek(0)

            content = await file.read()
            file_size = len(content)

            if not FileValidator.validate_file_size(file_size):
                raise ServerException(
                    message="File too large",
                    details=f"File size {file_size} bytes exceeds maximum allowed size",
                    code=413,
                )

            file_path = self.base_path / filename

            os.makedirs(file_path.parent, exist_ok=True)

            async with aiofiles.open(file_path, "wb") as buffer:
                await buffer.write(content)

            try:
                relative_path = str(file_path.relative_to(Path.cwd()))
            except ValueError:
                relative_path = str(file_path)

            return FileUploadResponse(
                filename=filename,
                original_filename=file.filename or filename,
                file_path=relative_path,
                content_type=file.content_type or "application/octet-stream",
                size=file_size,
                upload_time=datetime.utcnow(),
            )

        except Exception as e:
            if isinstance(e, ServerException):
                raise
            raise ServerException(
                message="Failed to upload file",
                details=f"Error occurred while saving file: {str(e)}",
            )
        finally:
            if hasattr(file, "file") and not file.file.closed:
                await file.close()

    async def delete_file(self, file_path: str) -> MessageResponse:
        """Delete a file from local storage.

        Performs safety checks (existence and path containment) before removing
        the file and attempts to clean up empty parent directories.

        Args:
            file_path (str): Path to the file to delete.

        Returns:
            MessageResponse: Response indicating success or failure of the deletion.
        """
        try:
            path = Path(file_path)

            if not await PathHelper.file_exists_async(path):
                return MessageResponse(
                    message="File not found",
                    success=False,
                    details=f"The file '{file_path}' does not exist",
                    status_code=404,
                )

            if not await PathHelper.is_safe_path_async(path, self.base_path):
                return MessageResponse(
                    message="Access denied",
                    success=False,
                    details="File path is outside the allowed storage directory",
                    status_code=403,
                )

            await PathHelper.delete_file_async(path)

            await PathHelper.cleanup_empty_dirs_async(path.parent, self.base_path)

            return MessageResponse(
                message="File deleted successfully",
                success=True,
                details=f"File '{file_path}' has been removed from storage",
                status_code=200,
            )

        except Exception as e:
            return MessageResponse(
                message="Failed to delete file",
                success=False,
                details=f"Error occurred while deleting file: {str(e)}",
                status_code=500,
            )

    async def get_file_url_async(self, file_path: str) -> str:
        """Get the URL for accessing a stored file asynchronously.

        For local storage this returns a relative URL path. In production this
        could be extended to include a base URL or CDN prefix.

        Args:
            file_path (str): Path to the file.

        Returns:
            str: URL for accessing the file.
        """
        return f"/{file_path}"

    async def file_exists_async(self, file_path: str) -> bool:
        """Check if a file exists in storage asynchronously.

        This verifies both that the path points to an existing file and that
        it is contained within the configured base storage directory.

        Args:
            file_path (str): Path to check.

        Returns:
            bool: True if file exists and is within storage base path, False otherwise.
        """
        try:
            path = Path(file_path)

            exists = await PathHelper.file_exists_async(path)
            is_safe = await PathHelper.is_safe_path_async(path, self.base_path)

            return exists and is_safe
        except Exception:
            return False

    async def get_file_size_async(self, file_path: str) -> int:
        """Get the size of a file asynchronously.

        Args:
            file_path (str): Path to the file.

        Returns:
            int: Size of the file in bytes, or -1 if the file doesn't exist or an error occurs.
        """
        try:
            path = Path(file_path)

            if await self.file_exists_async(file_path):
                return await PathHelper.get_file_size_async(path)
            return -1
        except Exception:
            return -1
