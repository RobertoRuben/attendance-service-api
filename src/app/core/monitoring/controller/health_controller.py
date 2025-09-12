from typing import Annotated
from fastapi import APIRouter, Depends, Request, status

from src.app.core.monitoring.model import HealthCheck
from src.app.core.exception import (
    BadRequestException,
    ServerException,
)
from src.app.core.exception.decorator import controller_handle_exceptions
from src.app.core.monitoring.service.dependencies import get_health_service
from src.app.core.monitoring.service.interface.health_service import IHealthService

router = APIRouter(prefix="/health", tags=["Health"])

health_tags_metadata = {
    "name": "Health",
    "description": "Health check endpoints",
}


@router.get(
    "",
    response_model=HealthCheck,
    summary="Health check endpoint",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": HealthCheck,
            "description": "Health check successful",
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
    description="",
)
@controller_handle_exceptions
async def health_check(
    request: Request,
    health_service: Annotated[IHealthService, Depends(get_health_service)],
) -> HealthCheck:
    return await health_service.basic_health_check()
