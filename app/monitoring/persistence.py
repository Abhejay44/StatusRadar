from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.health_check import HealthCheck
from app.monitoring.checker import CheckResult


def save_check_result(
    db: Session,
    service_id: int,
    result: CheckResult,
) -> HealthCheck:
    health_check = HealthCheck(
        service_id=service_id,
        status_code=result.status_code,
        response_time_ms=result.response_time_ms,
        success=result.success,
        error_message=result.error_message,
    )

    db.add(health_check)

    try:
        db.commit()
        db.refresh(health_check)
    except SQLAlchemyError:
        db.rollback()
        raise

    return health_check
