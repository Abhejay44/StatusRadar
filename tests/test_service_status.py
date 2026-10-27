from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from app.models.health_check import HealthCheck
from app.monitoring.status import (
    ServiceStatus,
    calculate_service_status,
    get_current_service_status,
)


def make_check(check_id: int, success: bool) -> HealthCheck:
    return HealthCheck(
        id=check_id,
        service_id=7,
        status_code=200 if success else 503,
        response_time_ms=80.0,
        success=success,
        error_message=None,
        checked_at=datetime.now(timezone.utc),
    )


def test_calculate_service_status_returns_unknown_without_checks() -> None:
    assert calculate_service_status([]) == ServiceStatus.UNKNOWN


def test_calculate_service_status_returns_up_when_all_checks_succeed() -> None:
    checks = [
        make_check(3, True),
        make_check(2, True),
        make_check(1, True),
    ]

    assert calculate_service_status(checks) == ServiceStatus.UP


def test_calculate_service_status_returns_down_when_all_checks_fail() -> None:
    checks = [
        make_check(3, False),
        make_check(2, False),
        make_check(1, False),
    ]

    assert calculate_service_status(checks) == ServiceStatus.DOWN


def test_calculate_service_status_returns_degraded_for_mixed_checks() -> None:
    checks = [
        make_check(3, True),
        make_check(2, False),
        make_check(1, True),
    ]

    assert calculate_service_status(checks) == ServiceStatus.DEGRADED


def test_get_current_service_status_uses_three_most_recent_checks() -> None:
    db = MagicMock(spec=Session)
    latest_check = make_check(3, True)
    checks = [
        latest_check,
        make_check(2, True),
        make_check(1, True),
    ]

    with patch(
        "app.monitoring.status.list_health_checks",
        return_value=checks,
    ) as mock_list_health_checks:
        result = get_current_service_status(
            db=db,
            service_id=7,
        )

    assert result.service_id == 7
    assert result.status == ServiceStatus.UP
    assert result.response_time_ms == latest_check.response_time_ms
    assert result.checked_at == latest_check.checked_at
    mock_list_health_checks.assert_called_once_with(
        db=db,
        service_id=7,
        limit=3,
    )
