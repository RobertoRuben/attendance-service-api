from src.app.core.monitoring.service.implementations import (
    HealthServiceImpl,
)
from src.app.core.monitoring.service.interface.health_service import IHealthService


async def get_health_service() -> IHealthService:
    """
    Get an instance of the health service.

    Returns:
        IHealthService: An instance of the health service.
    """
    return HealthServiceImpl()
