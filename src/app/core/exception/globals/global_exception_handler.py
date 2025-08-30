from fastapi import Request, FastAPI, logger
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
from fastapi.responses import JSONResponse
from src.app.core.exception.model import ErrorDetail
from src.app.core.exception.constants import ErrorTypes, ErrorTitles


async def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        details = []
        for error in exc.errors():
            details.append(
                {
                    "loc": error.get("loc", ["unknown"]),
                    "msg": error.get("msg", "Unknown validation error"),
                    "type": error.get("type", "validation_error"),
                }
            )

        instance = f"request:{request.url.path}"

        error = ErrorDetail(
            type=ErrorTypes.VALIDATION_ERROR,
            title=ErrorTitles.UNPROCESSABLE_ENTITY,
            status=422,
            detail="Input data validation error",
            details=details,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        return JSONResponse(status_code=422, content=error.model_dump())

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        instance = f"request:{request.url.path}"

        if exc.status_code == 400:
            title = ErrorTitles.BAD_REQUEST
        elif exc.status_code == 401:
            title = ErrorTitles.UNAUTHORIZED
        elif exc.status_code == 403:
            title = ErrorTitles.FORBIDDEN
        elif exc.status_code == 404:
            title = ErrorTitles.NOT_FOUND
        elif exc.status_code == 409:
            title = ErrorTitles.CONFLICT
        else:
            title = ErrorTitles.INTERNAL_SERVER_ERROR

        error = ErrorDetail(
            type=ErrorTypes.HTTP_ERROR,
            title=title,
            status=exc.status_code,
            detail=(
                str(exc.detail) if isinstance(exc.detail, str) else "Request error"
            ),
            details=exc.detail if not isinstance(exc.detail, str) else None,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        return JSONResponse(status_code=exc.status_code, content=error.model_dump())

    @app.exception_handler(AttributeError)
    async def attribute_error_handler(request: Request, exc: AttributeError):
        instance = f"request:{request.url.path}"

        error = ErrorDetail(
            type=ErrorTypes.IMPLEMENTATION_ERROR,
            title=ErrorTitles.IMPLEMENTATION_ERROR,
            status=500,
            detail="Service implementation error",
            details=str(exc),
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        logger.error(f"AttributeError: {exc}", exc_info=True)

        return JSONResponse(status_code=500, content=error.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        instance = f"request:{request.url.path}"

        error = ErrorDetail(
            type=ErrorTypes.SERVER_ERROR,
            title=ErrorTitles.INTERNAL_SERVER_ERROR,
            status=500,
            detail="An internal server error occurred",
            details=str(exc) if app.debug else None,
            instance=instance,
            timestamp=datetime.now().isoformat(),
        )

        logger.error(f"Unhandled exception: {exc}", exc_info=True)

        return JSONResponse(status_code=500, content=error.model_dump())
