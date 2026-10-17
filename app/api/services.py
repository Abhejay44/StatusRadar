from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.monitoring.service_monitor import monitor_service
from app.schemas.health_check import HealthCheckResponse


router = APIRouter(prefix="/api/services", tags=["services"])


@router.post(
    "/{service_id}/check",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
)
async def check_service_now(
    service_id: int,
    db: Session = Depends(get_db),
) -> HealthCheckResponse:
    try:
        health_check = await monitor_service(
            db=db,
            service_id=service_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return HealthCheckResponse.model_validate(health_check)
