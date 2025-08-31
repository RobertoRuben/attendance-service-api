import functools
from typing import Callable, TypeVar, Any, Optional
from src.app.core.exception.model import BaseHTTPException
from src.app.core.exception import ServerException
from src.app.core.exception.constants import ErrorTypes, ErrorTitles

T = TypeVar("T")


def service_handle_exceptions(
    func: Optional[Callable[..., T]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator factory that normalizes exception handling for service layer callables.

    Behavior:
    - If the wrapped function raises a BaseHTTPException, it is re-raised unchanged.
    - AttributeError is considered an implementation error and is converted to ServerException
      with type ErrorTypes.IMPLEMENTATION_ERROR.
    - Any other Exception is converted to ServerException with type ErrorTypes.SERVER_ERROR.

    The decorator can be used either with or without parentheses:

    Usage examples:
        @service_handle_exceptions
        async def my_service(...): ...

        @service_handle_exceptions()
        async def my_service(...): ...

    The wrapper will attempt to extract a Request-like object from the decorated function's
    args/kwargs (an object that has 'url' and 'method') and use its path as the Problem
    Details 'instance'. If not found, a synthetic instance URN is generated using the
    function name.
    """

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            request = None
            for arg in list(args) + list(kwargs.values()):
                if hasattr(arg, "url") and hasattr(arg, "method"):
                    request = arg
                    break

            instance = (
                request.url.path
                if request is not None
                else f"urn:problem-instance:{fn.__name__}"
            )

            try:
                return await fn(*args, **kwargs)

            except BaseHTTPException:
                raise

            except AttributeError as e:
                raise ServerException(
                    details=f"Implementation error: {e}",
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

    if func:
        return decorator(func)

    return decorator
