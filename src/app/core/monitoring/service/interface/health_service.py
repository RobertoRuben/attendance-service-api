from abc import ABC, abstractmethod

from src.app.core.monitoring.model import HealthCheck

class IHealthService(ABC):

    @abstractmethod
    async def basic_health_check(self) -> HealthCheck:
        pass
