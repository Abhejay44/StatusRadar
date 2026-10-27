from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.main import app
from app.monitoring.status import ServiceStatus, ServiceStatusResult


def override_get_db():
    yield MagicMock(spec=Session)


client = TestClient(app)
app.dependency_overrides[get_db] = override_get_db


def test_service_status_endpoint_returns_current_status() -> None:
    checked_at = datetime.now(timezone.utc)
    result = ServiceStatusResult(
        service_id=7,
        status=ServiceStatus.UP,
        response_time_ms=82.5,
        checked_at=checked_at,
    )

    with patch(
        "app.api.services.get_current_service_status",
        return_value=result,
    ):
        response = client.get("/api/services/7/status")

    assert response.status_code == 200
    assert response.json() == {
        "service_id": 7,
        "status": "up",
        "response_time_ms": 82.5,
        "checked_at": checked_at.isoformat().replace("+00:00", "Z"),
    }


def test_service_status_endpoint_returns_unknown_without_checks() -> None:
    result = ServiceStatusResult(
        service_id=7,
        status=ServiceStatus.UNKNOWN,
        response_time_ms=None,
        checked_at=None,
    )

    with patch(
        "app.api.services.get_current_service_status",
        return_value=result,
    ):
        response = client.get("/api/services/7/status")

    assert response.status_code == 200
    assert response.json() == {
        "service_id": 7,
        "status": "unknown",
        "response_time_ms": None,
        "checked_at": None,
    }


def test_service_status_endpoint_returns_404_for_missing_service() -> None:
    with patch(
        "app.api.services.get_current_service_status",
        side_effect=ValueError("Service with id 999 was not found"),
    ):
        response = client.get("/api/services/999/status")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Service with id 999 was not found"
    }
