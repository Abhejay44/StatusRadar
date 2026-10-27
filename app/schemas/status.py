from datetime import datetime

from pydantic import BaseModel

from app.monitoring.status import ServiceStatus


class ServiceStatusResponse(BaseModel):
    service_id: int
    status: ServiceStatus
    response_time_ms: float | None
    checked_at: datetime | None
