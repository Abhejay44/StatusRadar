from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.monitoring.status import ServiceStatus, get_current_service_status
from app.services.service_registry import list_services


@dataclass(frozen=True)
class ServiceSummary:
    id: int
    name: str
    url: str
    is_active: bool
    status: ServiceStatus
    response_time_ms: float | None
    checked_at: datetime | None


def list_service_summaries(
    db: Session,
) -> list[ServiceSummary]:
    services = list_services(db)

    summaries: list[ServiceSummary] = []

    for service in services:
        current_status = get_current_service_status(
            db=db,
            service_id=service.id,
        )

        summaries.append(
            ServiceSummary(
                id=service.id,
                name=service.name,
                url=service.url,
                is_active=service.is_active,
                status=current_status.status,
                response_time_ms=current_status.response_time_ms,
                checked_at=current_status.checked_at,
            )
        )

    return summaries
