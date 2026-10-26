from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.monitoring.history import get_latest_health_check, list_health_checks
from app.monitoring.service_monitor import monitor_service
from app.schemas.health_check import HealthCheckResponse
from app.schemas.service import ServiceCreate, ServiceResponse
from app.services.service_registry import create_service, list_services


router = APIRouter(prefix="/api/services", tags=["services"])


@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_monitored_service(
    payload: ServiceCreate,
    db: Session = Depends(get_db),
) -> ServiceResponse:
    service = create_service(
        db=db,
        name=payload.name,
        url=str(payload.url),
        is_active=payload.is_active,
    )
    return ServiceResponse.model_validate(service)


@router.get(
    "",
    response_model=list[ServiceResponse],
)
def get_monitored_services(
    db: Session = Depends(get_db),
) -> list[ServiceResponse]:
    services = list_services(db)
    return [ServiceResponse.model_validate(service) for service in services]


@router.get(
    "/{service_id}/checks",
    response_model=list[HealthCheckResponse],
)
def get_service_check_history(
    service_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[HealthCheckResponse]:
    try:
        health_checks = list_health_checks(
            db=db,
            service_id=service_id,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return [
        HealthCheckResponse.model_validate(health_check)
        for health_check in health_checks
    ]


@router.get(
    "/{service_id}/checks/latest",
    response_model=HealthCheckResponse,
)
def get_latest_service_check(
    service_id: int,
    db: Session = Depends(get_db),
) -> HealthCheckResponse:
    try:
        health_check = get_latest_health_check(
            db=db,
            service_id=service_id,
        )
    except (ValueError, LookupError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return HealthCheckResponse.model_validate(health_check)


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
