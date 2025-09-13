import functools
from typing import Callable, TypeVar, Any
from fastapi import Request
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from src.app.core.exception.model import BaseHTTPException
from src.app.core.exception import BadRequestException
from src.app.core.exception.constants import ErrorTypes, ErrorTitles
from .controller_handle_exception import controller_handle_exceptions

T = TypeVar("T")


def validation_handle_exceptions(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator that handles Pydantic validation errors with custom messages.

    This decorator specifically catches ValidationError and RequestValidationError
    to provide more user-friendly error messages from custom field validators.

    Usage:
        @validation_handle_exceptions
        async def create_student(request: Request, student_data: StudentRequestDTO):
            ...
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
        except (ValidationError, RequestValidationError) as e:
            # Extract custom validation messages
            validation_errors = []

            if isinstance(e, RequestValidationError):
                errors = e.errors()
            else:
                errors = e.errors()

            for error in errors:
                field_path = " -> ".join(str(loc) for loc in error.get("loc", []))
                error_msg = error.get("msg", "Validation error")

                # Check if it's a custom ValueError from our validators
                if error.get("type") == "value_error" and "ValueError" in str(
                    error.get("ctx", {})
                ):
                    # Extract the custom message from ValueError
                    ctx = error.get("ctx", {})
                    if "error" in ctx:
                        error_msg = str(ctx["error"])

                validation_errors.append(
                    {
                        "field": field_path,
                        "message": error_msg,
                        "input": error.get("input"),
                    }
                )

            raise BadRequestException(
                message="Los datos enviados contienen errores de validación",
                details={
                    "validation_errors": validation_errors,
                    "total_errors": len(validation_errors),
                },
                instance=instance,
                type_=ErrorTypes.VALIDATION_ERROR,
                title=ErrorTitles.BAD_REQUEST,
            )
        except BaseHTTPException:
            raise
        except Exception as e:
            # Fallback to existing controller exception handling

            decorated_func = controller_handle_exceptions(func)
            return await decorated_func(*args, **kwargs)

    return wrapper
