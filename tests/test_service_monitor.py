import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.models.health_check import HealthCheck
from app.models.service import Service
from app.monitoring.checker import CheckResult
from app.monitoring.service_monitor import monitor_service


def test_monitor_service_checks_and_persists_result() -> None:
    db = MagicMock(spec=Session)

    service = Service(
        id=7,
        name="GitHub",
        url="https://github.com",
        is_active=True,
    )
    db.get.return_value = service

    result = CheckResult(
        status_code=200,
        response_time_ms=125.5,
        success=True,
    )
    saved_health_check = HealthCheck(
        id=12,
        service_id=7,
        status_code=200,
        response_time_ms=125.5,
        success=True,
    )

    with (
        patch(
            "app.monitoring.service_monitor.check_service",
            new=AsyncMock(return_value=result),
        ) as mock_check_service,
        patch(
            "app.monitoring.service_monitor.save_check_result",
            return_value=saved_health_check,
        ) as mock_save_check_result,
    ):
        returned_health_check = asyncio.run(
            monitor_service(db=db, service_id=7)
        )

    db.get.assert_called_once_with(Service, 7)
    mock_check_service.assert_awaited_once_with(
        "https://github.com",
        client=None,
    )
    mock_save_check_result.assert_called_once_with(
        db=db,
        service_id=7,
        result=result,
    )
    assert returned_health_check is saved_health_check


def test_monitor_service_raises_when_service_is_missing() -> None:
    db = MagicMock(spec=Session)
    db.get.return_value = None

    with patch(
        "app.monitoring.service_monitor.check_service",
        new=AsyncMock(),
    ) as mock_check_service:
        with pytest.raises(
            ValueError,
            match="Service with id 999 was not found",
        ):
            asyncio.run(
                monitor_service(db=db, service_id=999)
            )

    db.get.assert_called_once_with(Service, 999)
    mock_check_service.assert_not_awaited()
