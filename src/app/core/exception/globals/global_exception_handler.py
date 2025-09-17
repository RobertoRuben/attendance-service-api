import json
from fastapi import Request, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
from datetime import datetime
from fastapi.responses import JSONResponse
from src.app.core.exception.model import ErrorDetail
from src.app.core.exception.constants import ErrorTypes, ErrorTitles
from src.app.core.exception import (
    NotFoundException,
    ConflictException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    DatabaseException,
    InvalidFieldException,
    ServerException,
    UnprocessableEntityException,
)
from .utils import extract_validation_errors, format_validation_response_details


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for the FastAPI application.

    This function registers exception handlers that provide consistent error formatting
    following RFC 7807 Problem Details standard. It handles different types of exceptions
    including validation errors, HTTP exceptions, and unexpected server errors.

    The handlers ensure that:
    - All error responses follow a consistent structure
    - Custom validation messages are properly extracted and displayed
    - Sensitive information is not exposed in production
    - HTTP status codes follow RFC standards (422 for validation, etc.)
    - Error details are properly serialized for JSON responses

    Args:
        app: The FastAPI application instance to register handlers on.

    Note:
        This should be called during application initialization, before registering
        routes to ensure the handlers are properly configured.
    """

    # Custom Domain Exception Handlers - Must be registered FIRST
    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(
        request: Request, exc: NotFoundException
    ) -> JSONResponse:
        """Handle NotFoundException for missing resources."""
        instance = f"request:{request.url.path}"

        error = ErrorDetail(
            type=exc.type_,
            title=exc.title,
            status=exc.code,
            detail=exc.message,
            details=exc.details,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        return JSONResponse(
            status_code=exc.code,
            content=jsonable_encoder(error.model_dump()),
            headers={"Content-Type": "application/json"},
        )

    @app.exception_handler(ConflictException)
    async def conflict_exception_handler(
        request: Request, exc: ConflictException
    ) -> JSONResponse:
        """Handle ConflictException for resource conflicts."""
        instance = f"request:{request.url.path}"

        error = ErrorDetail(
            type=exc.type_,
            title=exc.title,
            status=exc.code,
            detail=exc.message,
            details=exc.details,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        return JSONResponse(
            status_code=exc.code,
            content=jsonable_encoder(error.model_dump()),
            headers={"Content-Type": "application/json"},
        )

    @app.exception_handler(BadRequestException)
    async def bad_request_exception_handler(
        request: Request, exc: BadRequestException
    ) -> JSONResponse:
        """Handle BadRequestException for invalid client requests."""
        instance = f"request:{request.url.path}"

        error = ErrorDetail(
            type=exc.type_,
            title=exc.title,
            status=exc.code,
            detail=exc.message,
            details=exc.details,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        return JSONResponse(
            status_code=exc.code,
            content=jsonable_encoder(error.model_dump()),
            headers={"Content-Type": "application/json"},
        )

    @app.exception_handler(UnauthorizedException)
    async def unauthorized_exception_handler(
        request: Request, exc: UnauthorizedException
    ) -> JSONResponse:
        """Handle UnauthorizedException for authentication failures."""
        instance = f"request:{request.url.path}"

        error = ErrorDetail(
            type=exc.type_,
            title=exc.title,
            status=exc.code,
            detail=exc.message,
            details=exc.details,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        headers = {"Content-Type": "application/json"}
        if exc.headers:
            headers.update(exc.headers)

        return JSONResponse(
            status_code=exc.code,
            content=jsonable_encoder(error.model_dump()),
            headers=headers,
        )

    @app.exception_handler(ForbiddenException)
    async def forbidden_exception_handler(
        request: Request, exc: ForbiddenException
    ) -> JSONResponse:
        """Handle ForbiddenException for authorization failures."""
        instance = f"request:{request.url.path}"

        error = ErrorDetail(
            type=exc.type_,
            title=exc.title,
            status=exc.code,
            detail=exc.message,
            details=exc.details,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        headers = {"Content-Type": "application/json"}
        if exc.headers:
            headers.update(exc.headers)

        return JSONResponse(
            status_code=exc.code,
            content=jsonable_encoder(error.model_dump()),
            headers=headers,
        )

    @app.exception_handler(DatabaseException)
    async def database_exception_handler(
        request: Request, exc: DatabaseException
    ) -> JSONResponse:
        """Handle DatabaseException for database-related errors."""
        instance = f"request:{request.url.path}"

        error = ErrorDetail(
            type=exc.type_,
            title=exc.title,
            status=exc.code,
            detail=exc.message,
            details=exc.details if app.debug else None,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        return JSONResponse(
            status_code=exc.code,
            content=jsonable_encoder(error.model_dump()),
            headers={"Content-Type": "application/json"},
        )

    @app.exception_handler(InvalidFieldException)
    async def invalid_field_exception_handler(
        request: Request, exc: InvalidFieldException
    ) -> JSONResponse:
        """Handle InvalidFieldException for invalid field errors."""
        instance = f"request:{request.url.path}"

        error = ErrorDetail(
            type=exc.type_,
            title=exc.title,
            status=exc.code,
            detail=exc.message,
            details=exc.details,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        return JSONResponse(
            status_code=exc.code,
            content=jsonable_encoder(error.model_dump()),
            headers={"Content-Type": "application/json"},
        )

    @app.exception_handler(ServerException)
    async def server_exception_handler(
        request: Request, exc: ServerException
    ) -> JSONResponse:
        """Handle ServerException for internal server errors."""
        instance = f"request:{request.url.path}"

        error = ErrorDetail(
            type=exc.type_,
            title=exc.title,
            status=exc.code,
            detail=exc.message,
            details=exc.details if app.debug else None,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        return JSONResponse(
            status_code=exc.code,
            content=jsonable_encoder(error.model_dump()),
            headers={"Content-Type": "application/json"},
        )

    @app.exception_handler(UnprocessableEntityException)
    async def unprocessable_entity_exception_handler(
        request: Request, exc: UnprocessableEntityException
    ) -> JSONResponse:
        """Handle UnprocessableEntityException for validation errors."""
        instance = f"request:{request.url.path}"

        error = ErrorDetail(
            type=exc.type_,
            title=exc.title,
            status=exc.code,
            detail=exc.message,
            details=exc.details,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        return JSONResponse(
            status_code=exc.code,
            content=jsonable_encoder(error.model_dump()),
            headers={"Content-Type": "application/json"},
        )

    # FastAPI Built-in Exception Handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle FastAPI request validation errors using custom UnprocessableEntityException."""
        validation_errors = extract_validation_errors(exc.errors())
        details_dict = format_validation_response_details(validation_errors)

        unprocessable_exc = UnprocessableEntityException(
            message="The submitted data contains validation errors",
            details=json.dumps(details_dict),
        )

        instance = f"request:{request.url.path}"

        error = ErrorDetail(
            type=unprocessable_exc.type_,
            title=unprocessable_exc.title,
            status=unprocessable_exc.code,
            detail=unprocessable_exc.message,
            details=None,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        response_content = error.model_dump()
        response_content["details"] = details_dict

        return JSONResponse(
            status_code=unprocessable_exc.code,
            content=jsonable_encoder(response_content),
            headers={"Content-Type": "application/json"},
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Handle direct Pydantic validation errors using custom UnprocessableEntityException."""
        validation_errors = extract_validation_errors(exc.errors())
        details_dict = format_validation_response_details(validation_errors)

        instance = f"request:{request.url.path}"

        error = ErrorDetail(
            type=ErrorTypes.VALIDATION_ERROR,
            title=ErrorTitles.UNPROCESSABLE_ENTITY,
            status=422,
            detail="The submitted data contains validation errors",
            details=None,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        response_content = error.model_dump()
        response_content["details"] = details_dict

        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(response_content),
            headers={"Content-Type": "application/json"},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions following RFC status code semantics.

        This handler processes HTTP exceptions and maps them to appropriate RFC-compliant
        status codes and error messages. It ensures consistent error formatting while
        preserving the original HTTP semantics.

        Status code mapping follows RFC standards:
        - 400: Bad Request (malformed request syntax)
        - 401: Unauthorized (authentication required)
        - 403: Forbidden (authenticated but insufficient permissions)
        - 404: Not Found (resource doesn't exist)
        - 409: Conflict (request conflicts with server state)
        - 422: Unprocessable Entity (validation errors)
        - 500: Internal Server Error (unexpected server errors)

        Args:
            request: The FastAPI request object containing request metadata.
            exc: The HTTP exception with status code and detail message.

        Returns:
            JSONResponse with the original status code and structured error details.
        """

        instance = f"request:{request.url.path}"

        # Map status codes to appropriate titles following RFC standards
        title_mapping = {
            400: ErrorTitles.BAD_REQUEST,  # RFC 7231 - malformed syntax
            401: ErrorTitles.UNAUTHORIZED,  # RFC 7235 - authentication required
            403: ErrorTitles.FORBIDDEN,  # RFC 7231 - insufficient permissions
            404: ErrorTitles.NOT_FOUND,  # RFC 7231 - resource not found
            409: ErrorTitles.CONFLICT,  # RFC 7231 - request conflicts with state
            422: ErrorTitles.UNPROCESSABLE_ENTITY,  # RFC 4918 - validation errors
        }

        title = title_mapping.get(exc.status_code, ErrorTitles.INTERNAL_SERVER_ERROR)

        details_value = str(exc.detail) if exc.detail else None

        error = ErrorDetail(
            type=ErrorTypes.HTTP_ERROR,
            title=title,
            status=exc.status_code,
            detail=str(exc.detail) if isinstance(exc.detail, str) else "Request error",
            details=details_value,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(error.model_dump()),
            headers={"Content-Type": "application/json"},
        )

    @app.exception_handler(AttributeError)
    async def attribute_error_handler(
        request: Request, exc: AttributeError
    ) -> JSONResponse:
        """Handle AttributeError exceptions indicating implementation issues.

        This handler catches AttributeError exceptions which typically indicate
        missing attributes or methods in service implementations. These are
        considered implementation errors rather than client errors.

        Args:
            request: The FastAPI request object containing request metadata.
            exc: The AttributeError exception containing error details.

        Returns:
            JSONResponse with 500 status code indicating server implementation error.
        """

        instance = f"request:{request.url.path}"

        error = ErrorDetail(
            type=ErrorTypes.IMPLEMENTATION_ERROR,
            title=ErrorTitles.IMPLEMENTATION_ERROR,
            status=500,
            detail="Service implementation error",
            details=str(exc) if app.debug else None,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(error.model_dump()),
            headers={"Content-Type": "application/json"},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected exceptions with secure error reporting.

        This is the catch-all handler for any exceptions not handled by more specific
        handlers. It provides secure error reporting by exposing detailed error
        information only in debug mode to prevent information leakage in production.

        Args:
            request: The FastAPI request object containing request metadata.
            exc: The unhandled exception that occurred during request processing.

        Returns:
            JSONResponse with 500 status code. Error details are included only
            when the application is running in debug mode.
        """

        instance = f"request:{request.url.path}"

        details_content = None
        if app.debug:
            details_content = json.dumps(
                {"error_type": type(exc).__name__, "error_message": str(exc)}
            )

        error = ErrorDetail(
            type=ErrorTypes.SERVER_ERROR,
            title=ErrorTitles.INTERNAL_SERVER_ERROR,
            status=500,
            detail="An internal server error occurred",
            details=details_content,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(error.model_dump()),
            headers={"Content-Type": "application/json"},
        )
