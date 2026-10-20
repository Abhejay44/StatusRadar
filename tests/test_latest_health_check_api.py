from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.main import app
from app.models.health_check import HealthCheck


def override_get_db():
    yield MagicMock(spec=Session)


client = TestClient(app)
app.dependency_overrides[get_db] = override_get_db


def test_latest_health_check_endpoint_returns_latest_check() -> None:
    checked_at = datetime.now(timezone.utc)
    health_check = HealthCheck(
        id=15,
        service_id=7,
        status_code=200,
        response_time_ms=90.0,
        success=True,
        error_message=None,
        checked_at=checked_at,
    )

    with patch(
        "app.api.services.get_latest_health_check",
        return_value=health_check,
    ):
        response = client.get("/api/services/7/checks/latest")

    assert response.status_code == 200
    assert response.json() == {
        "id": 15,
        "service_id": 7,
        "status_code": 200,
        "response_time_ms": 90.0,
        "success": True,
        "error_message": None,
        "checked_at": checked_at.isoformat().replace("+00:00", "Z"),
    }


def test_latest_health_check_endpoint_returns_404_when_service_missing() -> None:
    with patch(
        "app.api.services.get_latest_health_check",
        side_effect=ValueError("Service with id 999 was not found"),
    ):
        response = client.get("/api/services/999/checks/latest")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Service with id 999 was not found"
    }


def test_latest_health_check_endpoint_returns_404_when_no_checks_exist() -> None:
    with patch(
        "app.api.services.get_latest_health_check",
        side_effect=LookupError(
            "Service with id 7 has no health checks"
        ),
    ):
        response = client.get("/api/services/7/checks/latest")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Service with id 7 has no health checks"
    }
