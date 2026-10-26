from datetime import datetime, timezone
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from app.models.health_check import HealthCheck
from app.models.service import Service
from app.monitoring.history import list_health_checks


def test_list_health_checks_returns_recent_checks() -> None:
    db = MagicMock(spec=Session)
    db.get.return_value = Service(
        id=7,
        name="GitHub",
        url="https://github.com/",
        is_active=True,
    )

    checks = [
        HealthCheck(
            id=3,
            service_id=7,
            status_code=200,
            response_time_ms=80.0,
            success=True,
            error_message=None,
            checked_at=datetime.now(timezone.utc),
        ),
        HealthCheck(
            id=2,
            service_id=7,
            status_code=503,
            response_time_ms=140.0,
            success=False,
            error_message=None,
            checked_at=datetime.now(timezone.utc),
        ),
    ]
    db.scalars.return_value.all.return_value = checks

    result = list_health_checks(
        db=db,
        service_id=7,
        limit=10,
    )

    assert result == checks
    db.get.assert_called_once_with(Service, 7)
    db.scalars.assert_called_once()


def test_list_health_checks_returns_empty_list_when_no_checks_exist() -> None:
    db = MagicMock(spec=Session)
    db.get.return_value = Service(
        id=7,
        name="GitHub",
        url="https://github.com/",
        is_active=True,
    )
    db.scalars.return_value.all.return_value = []

    result = list_health_checks(db=db, service_id=7)

    assert result == []


def test_list_health_checks_raises_for_missing_service() -> None:
    db = MagicMock(spec=Session)
    db.get.return_value = None

    try:
        list_health_checks(db=db, service_id=999)
    except ValueError as exc:
        assert str(exc) == "Service with id 999 was not found"
    else:
        raise AssertionError("Expected ValueError")

    db.scalars.assert_not_called()
