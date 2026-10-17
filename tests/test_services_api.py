from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.main import app
from app.models.health_check import HealthCheck


def override_get_db():
    yield MagicMock(spec=Session)


client = TestClient(app)
app.dependency_overrides[get_db] = override_get_db


def test_check_service_endpoint_returns_saved_health_check() -> None:
    checked_at = datetime.now(timezone.utc)
    saved_health_check = HealthCheck(
        id=12,
        service_id=7,
        status_code=200,
        response_time_ms=125.5,
        success=True,
        error_message=None,
        checked_at=checked_at,
    )

    with patch(
        "app.api.services.monitor_service",
        new=AsyncMock(return_value=saved_health_check),
    ) as mock_monitor_service:
        response = client.post("/api/services/7/check")

    assert response.status_code == 200
    assert response.json() == {
        "id": 12,
        "service_id": 7,
        "status_code": 200,
        "response_time_ms": 125.5,
        "success": True,
        "error_message": None,
        "checked_at": checked_at.isoformat().replace("+00:00", "Z"),
    }
    assert mock_monitor_service.await_count == 1
    assert mock_monitor_service.await_args.kwargs["service_id"] == 7


def test_check_service_endpoint_returns_404_for_missing_service() -> None:
    with patch(
        "app.api.services.monitor_service",
        new=AsyncMock(
            side_effect=ValueError("Service with id 999 was not found")
        ),
    ):
        response = client.post("/api/services/999/check")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Service with id 999 was not found"
    }
