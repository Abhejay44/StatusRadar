from datetime import datetime

from pydantic import BaseModel

from app.monitoring.status import ServiceStatus


class ServiceSummaryResponse(BaseModel):
    id: int
    name: str
    url: str
    is_active: bool
    status: ServiceStatus
    response_time_ms: float | None
    checked_at: datetime | None
