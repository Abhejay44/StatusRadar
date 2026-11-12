import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from sqlalchemy.orm import Session

from app.models.health_check import HealthCheck
from app.models.service import Service
from app.monitoring.batch import monitor_active_services


def test_monitor_active_services_checks_each_active_service() -> None:
    db = MagicMock(spec=Session)
    client = AsyncMock(spec=httpx.AsyncClient)

    services = [
        Service(
            id=1,
            name="GitHub",
            url="https://github.com/",
            is_active=True,
        ),
        Service(
            id=2,
            name="Discord",
            url="https://discord.com/",
            is_active=True,
        ),
    ]

    saved_checks = [
        HealthCheck(
            id=10,
            service_id=1,
            status_code=200,
            response_time_ms=80.0,
            success=True,
            error_message=None,
        ),
        HealthCheck(
            id=11,
            service_id=2,
            status_code=200,
            response_time_ms=90.0,
            success=True,
            error_message=None,
        ),
    ]

    with (
        patch(
            "app.monitoring.batch.list_active_services",
            return_value=services,
        ),
        patch(
            "app.monitoring.batch.monitor_service",
            new=AsyncMock(side_effect=saved_checks),
        ) as mock_monitor_service,
    ):
        result = asyncio.run(
            monitor_active_services(
                db=db,
                client=client,
            )
        )

    assert result == saved_checks
    assert mock_monitor_service.await_count == 2
    mock_monitor_service.assert_any_await(
        db=db,
        service_id=1,
        client=client,
    )
    mock_monitor_service.assert_any_await(
        db=db,
        service_id=2,
        client=client,
    )
    client.aclose.assert_not_awaited()


def test_monitor_active_services_returns_empty_list_when_none_are_active() -> None:
    db = MagicMock(spec=Session)
    client = AsyncMock(spec=httpx.AsyncClient)

    with (
        patch(
            "app.monitoring.batch.list_active_services",
            return_value=[],
        ),
        patch(
            "app.monitoring.batch.monitor_service",
            new=AsyncMock(),
        ) as mock_monitor_service,
    ):
        result = asyncio.run(
            monitor_active_services(
                db=db,
                client=client,
            )
        )

    assert result == []
    mock_monitor_service.assert_not_awaited()
    client.aclose.assert_not_awaited()


def test_monitor_active_services_closes_client_it_creates() -> None:
    db = MagicMock(spec=Session)
    service = Service(
        id=1,
        name="GitHub",
        url="https://github.com/",
        is_active=True,
    )
    saved_check = HealthCheck(
        id=10,
        service_id=1,
        status_code=200,
        response_time_ms=80.0,
        success=True,
        error_message=None,
    )
    created_client = AsyncMock(spec=httpx.AsyncClient)

    with (
        patch(
            "app.monitoring.batch.list_active_services",
            return_value=[service],
        ),
        patch(
            "app.monitoring.batch.monitor_service",
            new=AsyncMock(return_value=saved_check),
        ),
        patch(
            "app.monitoring.batch.httpx.AsyncClient",
            return_value=created_client,
        ),
    ):
        result = asyncio.run(
            monitor_active_services(db=db)
        )

    assert result == [saved_check]
    created_client.aclose.assert_awaited_once_with()
