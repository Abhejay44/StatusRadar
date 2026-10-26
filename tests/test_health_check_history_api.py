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


def test_health_check_history_endpoint_returns_checks() -> None:
    checked_at = datetime.now(timezone.utc)
    checks = [
        HealthCheck(
            id=3,
            service_id=7,
            status_code=200,
            response_time_ms=80.0,
            success=True,
            error_message=None,
            checked_at=checked_at,
        ),
        HealthCheck(
            id=2,
            service_id=7,
            status_code=503,
            response_time_ms=140.0,
            success=False,
            error_message=None,
            checked_at=checked_at,
        ),
    ]

    with patch(
        "app.api.services.list_health_checks",
        return_value=checks,
    ) as mock_list_health_checks:
        response = client.get("/api/services/7/checks?limit=2")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [3, 2]
    mock_list_health_checks.assert_called_once()
    assert mock_list_health_checks.call_args.kwargs["service_id"] == 7
    assert mock_list_health_checks.call_args.kwargs["limit"] == 2


def test_health_check_history_endpoint_returns_empty_list() -> None:
    with patch(
        "app.api.services.list_health_checks",
        return_value=[],
    ):
        response = client.get("/api/services/7/checks")

    assert response.status_code == 200
    assert response.json() == []


def test_health_check_history_endpoint_returns_404_for_missing_service() -> None:
    with patch(
        "app.api.services.list_health_checks",
        side_effect=ValueError("Service with id 999 was not found"),
    ):
        response = client.get("/api/services/999/checks")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Service with id 999 was not found"
    }


def test_health_check_history_endpoint_validates_limit() -> None:
    response = client.get("/api/services/7/checks?limit=0")

    assert response.status_code == 422
