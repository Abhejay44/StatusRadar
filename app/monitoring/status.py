from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sqlalchemy.orm import Session

from app.models.health_check import HealthCheck
from app.monitoring.history import list_health_checks


class ServiceStatus(str, Enum):
    UP = "up"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ServiceStatusResult:
    service_id: int
    status: ServiceStatus
    response_time_ms: float | None
    checked_at: datetime | None


def calculate_service_status(
    health_checks: list[HealthCheck],
) -> ServiceStatus:
    if not health_checks:
        return ServiceStatus.UNKNOWN

    successful_checks = sum(
        1 for health_check in health_checks if health_check.success
    )

    if successful_checks == len(health_checks):
        return ServiceStatus.UP

    if successful_checks == 0:
        return ServiceStatus.DOWN

    return ServiceStatus.DEGRADED


def get_current_service_status(
    db: Session,
    service_id: int,
) -> ServiceStatusResult:
    health_checks = list_health_checks(
        db=db,
        service_id=service_id,
        limit=3,
    )

    status = calculate_service_status(health_checks)
    latest_check = health_checks[0] if health_checks else None

    return ServiceStatusResult(
        service_id=service_id,
        status=status,
        response_time_ms=(
            latest_check.response_time_ms if latest_check else None
        ),
        checked_at=(
            latest_check.checked_at if latest_check else None
        ),
    )
