import functools
from fastapi import Request
from typing import Callable, TypeVar, Any
from src.app.core.exception.model import BaseHTTPException
from src.app.core.exception import ServerException
from src.app.core.exception.constants import ErrorTypes, ErrorTitles

T = TypeVar("T")


def controller_handle_exceptions(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator that normalizes exception handling for FastAPI controller callables.

    Behavior:
    - If the wrapped function raises a BaseHTTPException, it is re-raised unchanged,
      but this decorator ensures the Problem Details 'instance' field is populated
      (using request.url.path or a synthetic URN) when available.
    - AttributeError is treated as an implementation error and converted to ServerException
      with type ErrorTypes.IMPLEMENTATION_ERROR.
    - Any other Exception is converted to ServerException with type ErrorTypes.SERVER_ERROR.

    Usage:
        @controller_handle_exceptions
        async def my_endpoint(request: Request, ...):
            ...

    Implementation notes:
    - The decorator looks for a fastapi.Request instance first in kwargs under 'request',
      then scans positional args to find it. If not found, a synthetic instance URN
      of the form "urn:problem-instance:{function_name}" is used.
    - When re-raising BaseHTTPException, if the exception has a detail dict and no
      'instance' key, the decorator injects the computed instance value.
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        request: Request | None = kwargs.get("request", None)
        if request is None:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

        instance = (
            request.url.path if request else f"urn:problem-instance:{func.__name__}"
        )

        try:
            return await func(*args, **kwargs)
        except BaseHTTPException as e:
            if hasattr(e, "detail") and isinstance(e.detail, dict):
                if e.detail.get("instance") is None:
                    e.detail["instance"] = instance
            raise
        except AttributeError as e:
            raise ServerException(
                details=f"Implementation error: {str(e)}",
                instance=instance,
                type_=ErrorTypes.IMPLEMENTATION_ERROR,
                title=ErrorTitles.IMPLEMENTATION_ERROR,
            )
        except Exception as e:
            raise ServerException(
                details=str(e),
                instance=instance,
                type_=ErrorTypes.SERVER_ERROR,
                title=ErrorTitles.INTERNAL_SERVER_ERROR,
            )

    return wrapper
