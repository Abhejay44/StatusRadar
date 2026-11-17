import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from sqlalchemy.orm import Session

from app.monitoring.scheduler import run_monitoring_cycle


def test_run_monitoring_cycle_uses_and_closes_session() -> None:
    client = AsyncMock(spec=httpx.AsyncClient)
    db = MagicMock(spec=Session)

    with (
        patch(
            "app.monitoring.scheduler.SessionLocal",
            return_value=db,
        ),
        patch(
            "app.monitoring.scheduler.monitor_active_services",
            new=AsyncMock(return_value=[]),
        ) as mock_monitor_active_services,
    ):
        asyncio.run(run_monitoring_cycle(client))

    mock_monitor_active_services.assert_awaited_once_with(
        db=db,
        client=client,
    )
    db.close.assert_called_once_with()


def test_run_monitoring_cycle_closes_session_when_monitoring_fails() -> None:
    client = AsyncMock(spec=httpx.AsyncClient)
    db = MagicMock(spec=Session)

    with (
        patch(
            "app.monitoring.scheduler.SessionLocal",
            return_value=db,
        ),
        patch(
            "app.monitoring.scheduler.monitor_active_services",
            new=AsyncMock(side_effect=RuntimeError("monitoring failed")),
        ),
    ):
        try:
            asyncio.run(run_monitoring_cycle(client))
        except RuntimeError as exc:
            assert str(exc) == "monitoring failed"
        else:
            raise AssertionError("Expected RuntimeError")

    db.close.assert_called_once_with()
