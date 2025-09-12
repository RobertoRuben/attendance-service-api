import time
from datetime import datetime, timezone
from src.app.core.monitoring.service.interface import IHealthService
from src.app.core.monitoring.model import HealthCheck


class HealthServiceImpl(IHealthService):
    def __init__(self):
        self.startup_time = time.time()

    async def basic_health_check(self) -> HealthCheck:
        return HealthCheck(
            status="healthy",
            timestamp=datetime.now(timezone.utc),
            service="Attendance Service API",
        )
