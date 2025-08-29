from fastapi import HTTPException
from datetime import datetime
from .error_detail import ErrorDetail


class BaseHTTPException(HTTPException):
    """
    Base class for all custom HTTP exceptions.
    Provides consistent error formatting using ErrorDetail.
    """

    def __init__(
        self,
        type_: str = None,
        code: int = 500,
        message: str = "An unexpected error occurred",
        details: str = None,
        instance: str = None,
        time: str = None,
        headers: dict = None,
        title: str = "Server Error",
    ):
        """
        Initialize a new BaseHTTPException.

        :param type_: URI that identifies the problem type
        :param code: HTTP status code
        :param message: Human-readable error message
        :param details: Additional details about the error
        :param instance: URI that identifies the specific occurrence of the problem
        :param time: Timestamp when the error occurred, defaults to current time
        :param headers: HTTP headers to include in the response
        :param title: A short, human-readable summary of the problem type
        """

        error = ErrorDetail(
            type=type_,
            title=title,
            status=code,
            detail=message,
            details=details,
            instance=instance,
            timestamp=time or datetime.now().isoformat(),
        )

        super().__init__(status_code=code, detail=error.model_dump(), headers=headers)
