import asyncio
import os
import shutil
from pathlib import Path


class PathHelper:
    """Helper class for path operations with optimized async handling.

    This class provides asynchronous helpers for common filesystem tasks by
    delegating blocking calls to the default executor when needed.
    """

    @staticmethod
    async def is_safe_path_async(path: Path, base_path: Path) -> bool:
        """Check if a path is inside a base directory.

        This resolves both paths (to handle symlinks) and verifies that the
        resolved path starts with the resolved base path.

        Args:
            path (Path): Path to check.
            base_path (Path): Base directory path.

        Returns:
            bool: True if `path` is inside `base_path`, False otherwise.
        """
        try:
            # These operations are fast and don't need thread pool
            resolved_path = path.resolve()
            base_resolved = base_path.resolve()

            # Check if the file is within our base directory
            return str(resolved_path).startswith(str(base_resolved))
        except (OSError, ValueError):
            return False

    @staticmethod
    async def file_exists_async(path: Path) -> bool:
        """Determine whether a file exists and is a file.

        Args:
            path (Path): Path to check.

        Returns:
            bool: True if file exists and is a file, False on error or if not a file.
        """
        try:
            # Fast filesystem operations - no need for thread pool
            return path.exists() and path.is_file()
        except (OSError, PermissionError):
            return False

    @staticmethod
    async def directory_exists_async(path: Path) -> bool:
        """Determine whether a directory exists.

        Args:
            path (Path): Path to check.

        Returns:
            bool: True if directory exists and is a directory, False otherwise.
        """
        try:
            return path.exists() and path.is_dir()
        except (OSError, PermissionError):
            return False

    @staticmethod
    async def get_file_size_async(path: Path) -> int:
        """Return file size in bytes.

        Uses the event loop executor for the potentially slow stat() call.

        Args:
            path (Path): Path to the file.

        Returns:
            int: File size in bytes, or -1 if the file does not exist or an error occurs.
        """
        try:
            if not await PathHelper.file_exists_async(path):
                return -1

            # Use thread pool only for potentially slow I/O operation
            loop = asyncio.get_event_loop()
            stat_result = await loop.run_in_executor(None, path.stat)
            return stat_result.st_size
        except (OSError, PermissionError):
            return -1

    @staticmethod
    async def delete_file_async(path: Path) -> None:
        """Delete a file.

        Executes os.unlink in the default executor.

        Args:
            path (Path): Path to the file to delete.

        Raises:
            OSError: If file deletion fails.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, os.unlink, str(path))

    @staticmethod
    async def delete_directory_async(path: Path, recursive: bool = False) -> None:
        """Delete a directory.

        Args:
            path (Path): Path to the directory to delete.
            recursive (bool): If True, remove directory and all contents (shutil.rmtree).
                              If False, only remove empty directory (os.rmdir).

        Raises:
            OSError: If directory deletion fails.
        """
        loop = asyncio.get_event_loop()
        if recursive:
            await loop.run_in_executor(None, shutil.rmtree, str(path))
        else:
            await loop.run_in_executor(None, os.rmdir, str(path))

    @staticmethod
    async def create_directory_async(
        path: Path, parents: bool = True, exist_ok: bool = True
    ) -> None:
        """Create a directory.

        Delegates Path.mkdir to the executor to avoid blocking the event loop.

        Args:
            path (Path): Directory path to create.
            parents (bool): Create parent directories if they don't exist.
            exist_ok (bool): Do not raise if the directory already exists.

        Raises:
            OSError: If directory creation fails.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, path.mkdir, parents, exist_ok)

    @staticmethod
    async def cleanup_empty_dirs_async(directory: Path, base_path: Path) -> None:
        """Recursively remove empty parent directories up to base_path.

        This is a best-effort cleanup: permission and OS errors are ignored.

        Args:
            directory (Path): Directory to start cleanup from.
            base_path (Path): Base directory (this directory will not be removed).
        """
        try:
            # Safety checks
            if directory == base_path or not directory.exists():
                return

            # Resolve paths to handle symlinks properly
            directory = directory.resolve()
            base_path = base_path.resolve()

            # Additional safety check after resolving
            if directory == base_path or not str(directory).startswith(str(base_path)):
                return

            # Check if directory is empty (fast operation)
            try:
                is_empty = not any(directory.iterdir())
            except (OSError, PermissionError):
                return

            if is_empty:
                # Only the actual deletion needs thread pool
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, directory.rmdir)

                # Recursively clean parent directories
                await PathHelper.cleanup_empty_dirs_async(directory.parent, base_path)

        except (OSError, PermissionError):
            # Ignore errors during cleanup - this is best effort
            pass

    @staticmethod
    async def move_file_async(src_path: Path, dest_path: Path) -> None:
        """Move a file from src_path to dest_path.

        Args:
            src_path (Path): Source file path.
            dest_path (Path): Destination file path.

        Raises:
            OSError: If file move fails.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, shutil.move, str(src_path), str(dest_path))

    @staticmethod
    async def copy_file_async(src_path: Path, dest_path: Path) -> None:
        """Copy a file from src_path to dest_path preserving metadata.

        Args:
            src_path (Path): Source file path.
            dest_path (Path): Destination file path.

        Raises:
            OSError: If file copy fails.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, shutil.copy2, str(src_path), str(dest_path))

    @staticmethod
    async def get_file_modified_time_async(path: Path) -> float | None:
        """Return the file's last modification time as a timestamp.

        Args:
            path (Path): Path to the file.

        Returns:
            float | None: Modification time as timestamp, or None if file doesn't exist or an error occurs.
        """
        try:
            if not await PathHelper.file_exists_async(path):
                return None

            loop = asyncio.get_event_loop()
            stat_result = await loop.run_in_executor(None, path.stat)
            return stat_result.st_mtime
        except (OSError, PermissionError):
            return None

    @staticmethod
    async def list_files_async(
        directory: Path, pattern: str = "*", recursive: bool = False
    ) -> list[Path]:
        """List files in a directory matching a pattern.

        Args:
            directory (Path): Directory to search in.
            pattern (str): Glob pattern to match (e.g., "*.jpg").
            recursive (bool): If True, search recursively in subdirectories.

        Returns:
            list[Path]: List of matching file paths. Returns empty list on error.
        """
        try:
            if not await PathHelper.directory_exists_async(directory):
                return []

            loop = asyncio.get_event_loop()

            def _list_files():
                if recursive:
                    return [p for p in directory.rglob(pattern) if p.is_file()]
                else:
                    return [p for p in directory.glob(pattern) if p.is_file()]

            files = await loop.run_in_executor(None, _list_files)
            return files
        except (OSError, PermissionError):
            return []

    @staticmethod
    async def get_directory_size_async(directory: Path) -> int:
        """Calculate total size of a directory and its contents.

        Args:
            directory (Path): Directory path.

        Returns:
            int: Total size in bytes, or -1 if the directory doesn't exist or an error occurs.
        """
        try:
            if not await PathHelper.directory_exists_async(directory):
                return -1

            loop = asyncio.get_event_loop()

            def _calculate_size():
                total_size = 0
                for path in directory.rglob("*"):
                    if path.is_file():
                        try:
                            total_size += path.stat().st_size
                        except (OSError, PermissionError):
                            continue
                return total_size

            return await loop.run_in_executor(None, _calculate_size)
        except (OSError, PermissionError):
            return -1
