from datetime import datetime, timezone
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from app.models.health_check import HealthCheck
from app.models.service import Service
from app.monitoring.history import get_latest_health_check


def test_get_latest_health_check_returns_check() -> None:
    db = MagicMock(spec=Session)
    service = Service(
        id=7,
        name="GitHub",
        url="https://github.com/",
        is_active=True,
    )
    latest_check = HealthCheck(
        id=15,
        service_id=7,
        status_code=200,
        response_time_ms=90.0,
        success=True,
        error_message=None,
        checked_at=datetime.now(timezone.utc),
    )

    db.get.return_value = service
    db.scalars.return_value.first.return_value = latest_check

    result = get_latest_health_check(db=db, service_id=7)

    assert result is latest_check
    db.get.assert_called_once_with(Service, 7)
    db.scalars.assert_called_once()


def test_get_latest_health_check_raises_for_missing_service() -> None:
    db = MagicMock(spec=Session)
    db.get.return_value = None

    try:
        get_latest_health_check(db=db, service_id=999)
    except ValueError as exc:
        assert str(exc) == "Service with id 999 was not found"
    else:
        raise AssertionError("Expected ValueError")

    db.scalars.assert_not_called()


def test_get_latest_health_check_raises_when_no_checks_exist() -> None:
    db = MagicMock(spec=Session)
    db.get.return_value = Service(
        id=7,
        name="GitHub",
        url="https://github.com/",
        is_active=True,
    )
    db.scalars.return_value.first.return_value = None

    try:
        get_latest_health_check(db=db, service_id=7)
    except LookupError as exc:
        assert str(exc) == "Service with id 7 has no health checks"
    else:
        raise AssertionError("Expected LookupError")
