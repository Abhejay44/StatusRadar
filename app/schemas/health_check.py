from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HealthCheckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_id: int
    status_code: int | None
    response_time_ms: float | None
    success: bool
    error_message: str | None
    checked_at: datetime
