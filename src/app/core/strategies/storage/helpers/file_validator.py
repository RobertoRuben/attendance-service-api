import re
from pathlib import Path

from src.app.core.config import settings


class FileValidator:
    """Utility class for validating and sanitizing file names and metadata.

    The class provides static helpers to:
    - Validate common image MIME types.
    - Check filenames for safety (no traversal, invalid chars, reserved names).
    - Validate file size against configurable limits.
    - Validate file extensions against an allowlist.
    - Produce a sanitized filename safe for storage.

    All methods are static so the class can be used without instantiation.
    """

    @staticmethod
    def is_valid_image(content_type: str | None) -> bool:
        """Return whether a MIME content type corresponds to a supported image.

        Args:
            content_type (str | None): MIME type of the file (e.g. "image/png").

        Returns:
            bool: True if the content type is a supported image MIME type,
                False otherwise.
        """
        if not content_type:
            return False

        valid_types = frozenset(
            {
                "image/jpeg",
                "image/png",
                "image/gif",
                "image/webp",
                "image/bmp",
                "image/svg+xml",
                "image/tiff",
                "image/ico",
            }
        )

        return content_type.lower() in valid_types

    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """Check whether a filename is safe for use on common filesystems.

        The check verifies:
        - filename is non-empty and not only whitespace
        - length does not exceed typical filesystem limits
        - no path traversal tokens or path separators
        - absence of dangerous characters and control characters
        - not a Windows reserved device name
        - does not start or end with problematic characters
        - matches a conservative whitelist pattern

        Args:
            filename (str): Candidate filename to validate.

        Returns:
            bool: True if the filename is considered safe, False otherwise.
        """
        if not filename or len(filename.strip()) == 0:
            return False

        # Remove leading/trailing whitespace
        filename = filename.strip()

        # Check length limits (most filesystems support up to 255 characters)
        if len(filename) > 255:
            return False

        # Check for path traversal attempts
        if ".." in filename:
            return False

        # Check for path separators
        if "/" in filename or "\\" in filename:
            return False

        # Check for dangerous characters
        dangerous_chars = [":", "*", "?", '"', "<", ">", "|"]
        if any(char in filename for char in dangerous_chars):
            return False

        # Check for control characters (ASCII 0-31)
        if any(ord(char) < 32 for char in filename):
            return False

        # Check for Windows reserved names
        reserved_names = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }

        # Get name without extension for reserved name check
        name_without_ext = filename.split(".")[0].upper()
        if name_without_ext in reserved_names:
            return False

        # Check for filenames starting or ending with dots or spaces
        if filename.startswith(".") and len(filename) == 1:  # Just a single dot
            return False
        if filename.endswith(" ") or filename.endswith("."):
            return False

        # Validate filename pattern (basic alphanumeric + safe chars)
        # Allow letters, numbers, dots, hyphens, underscores, spaces, parentheses
        valid_pattern = re.compile(r"^[a-zA-Z0-9._\-\s()]+$")
        if not valid_pattern.match(filename):
            return False

        return True

    @staticmethod
    def validate_file_size(size: int, max_size_mb: int = 10) -> bool:
        """Validate that a file size is within allowed limits.

        If max_size_mb is None the value from application settings
        (settings.STORAGE_MAX_FILE_SIZE_MB) is used.

        Args:
            size (int): File size in bytes.
            max_size_mb (int | None): Maximum allowed size in megabytes.
                Defaults to 10 MB if not provided.

        Returns:
            bool: True if the size is positive and less than or equal to the
                configured maximum, False otherwise.
        """
        if size <= 0:
            return False

        if max_size_mb is None:
            max_size_mb = settings.STORAGE_MAX_FILE_SIZE_MB

        max_size_bytes = max_size_mb * 1024 * 1024
        return size <= max_size_bytes

    @staticmethod
    def validate_file_extension(
        filename: str, allowed_extensions: set[str] = None
    ) -> bool:
        """Return whether a filename's extension is in the allowlist.

        The comparison is case-insensitive. If allowed_extensions is omitted
        a sensible default set for common image formats is used.

        Args:
            filename (str): Filename to check (may include path components).
            allowed_extensions (set[str] | None): Set of allowed extensions,
                including the leading dot (e.g. {'.jpg', '.png'}). If None,
                a default set of common image extensions is used.

        Returns:
            bool: True if the file has an extension and it is allowed,
                False otherwise.
        """
        if allowed_extensions is None:
            allowed_extensions = {
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".webp",
                ".bmp",
                ".svg",
                ".tiff",
                ".ico",
            }

        if not filename:
            return False

        file_path = Path(filename)
        extension = file_path.suffix.lower()

        return extension in allowed_extensions

    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 200) -> str:
        """Sanitize a filename to make it safe for storage.

        The sanitization:
        - replaces dangerous characters with underscores
        - removes control characters
        - replaces path traversal tokens
        - trims whitespace
        - avoids leading dot (hidden files)
        - preserves extension while truncating the stem to fit max_length

        Args:
            filename (str): Original filename to sanitize.
            max_length (int): Maximum allowed length for the returned name.
                Defaults to 200 characters.

        Returns:
            str: A sanitized filename suitable for use on common filesystems.
        """
        if not filename:
            return "unnamed_file"

        # Remove dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

        # Remove control characters
        filename = "".join(char for char in filename if ord(char) >= 32)

        # Remove path traversal
        filename = filename.replace("..", "_")

        # Trim whitespace
        filename = filename.strip()

        # Ensure it doesn't start with dot (hidden file)
        if filename.startswith("."):
            filename = "_" + filename[1:]

        # Truncate if too long, but preserve extension
        if len(filename) > max_length:
            path = Path(filename)
            stem = path.stem[: max_length - len(path.suffix) - 1]
            filename = f"{stem}{path.suffix}"

        # Ensure it's not empty after sanitization
        if not filename:
            filename = "sanitized_file"

        return filename
