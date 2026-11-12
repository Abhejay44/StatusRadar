import httpx
from sqlalchemy.orm import Session

from app.models.health_check import HealthCheck
from app.monitoring.service_monitor import monitor_service
from app.services.service_registry import list_active_services


async def monitor_active_services(
    db: Session,
    client: httpx.AsyncClient | None = None,
) -> list[HealthCheck]:
    services = list_active_services(db)

    owns_client = client is None
    http_client = client or httpx.AsyncClient(timeout=10.0)

    health_checks: list[HealthCheck] = []

    try:
        for service in services:
            health_check = await monitor_service(
                db=db,
                service_id=service.id,
                client=http_client,
            )
            health_checks.append(health_check)
    finally:
        if owns_client:
            await http_client.aclose()

    return health_checks
