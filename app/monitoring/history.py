from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.health_check import HealthCheck
from app.models.service import Service


def get_latest_health_check(
    db: Session,
    service_id: int,
) -> HealthCheck:
    service = db.get(Service, service_id)

    if service is None:
        raise ValueError(f"Service with id {service_id} was not found")

    statement = (
        select(HealthCheck)
        .where(HealthCheck.service_id == service_id)
        .order_by(
            HealthCheck.checked_at.desc(),
            HealthCheck.id.desc(),
        )
        .limit(1)
    )

    health_check = db.scalars(statement).first()

    if health_check is None:
        raise LookupError(
            f"Service with id {service_id} has no health checks"
        )

    return health_check
