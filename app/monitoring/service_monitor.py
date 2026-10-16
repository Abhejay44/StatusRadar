import httpx
from sqlalchemy.orm import Session

from app.models.health_check import HealthCheck
from app.models.service import Service
from app.monitoring.checker import check_service
from app.monitoring.persistence import save_check_result


async def monitor_service(
    db: Session,
    service_id: int,
    client: httpx.AsyncClient | None = None,
) -> HealthCheck:
    service = db.get(Service, service_id)

    if service is None:
        raise ValueError(f"Service with id {service_id} was not found")

    result = await check_service(service.url, client=client)

    return save_check_result(
        db=db,
        service_id=service.id,
        result=result,
    )
