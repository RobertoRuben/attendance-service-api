import os
from fastapi import APIRouter, Request, status

from src.app.core.exception.decorator import controller_handle_exceptions
from src.app.core.exception import BadRequestException, ServerException
from src.app.domain.root.dto.response import RootResponseDTO


api_base = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
api_prefix = os.getenv("API_PREFIX", "/api/v1").rstrip("/")
app_version = os.getenv("APP_VERSION", "1.0.0")

router = APIRouter(prefix="", tags=["Root"])

root_tags_metadata = {
    "name": "Root",
    "description": "Root endpoint",
}


@router.get(
    "/",
    response_model=RootResponseDTO,
    summary="Service root information",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": RootResponseDTO,
            "description": "Service root information retrieved successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestException,
            "description": "Invalid request data or validation errors",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ServerException,
            "description": "Internal server error occurred",
        },
    },
    description="""
    Returns basic service metadata and links to API documentation.
    """,
)
@controller_handle_exceptions
async def root(request: Request) -> RootResponseDTO:
    """
    Get root information.

    Args:
        request (Request): The request object.

    Returns:
        RootResponseDTO: The root response data transfer object.
    """
    return RootResponseDTO(
        message="Attendance Service API",
        version=app_version,
        docs=f"{api_base}{api_prefix}/docs",
        redoc=f"{api_base}{api_prefix}/redoc",
        scalar=f"{api_base}{api_prefix}/scalar",
    )
