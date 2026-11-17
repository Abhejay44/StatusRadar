from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.main import app
from app.monitoring.status import ServiceStatus
from app.services.service_summary import ServiceSummary


def override_get_db():
    yield MagicMock(spec=Session)


client = TestClient(app)
app.dependency_overrides[get_db] = override_get_db


def test_service_summary_endpoint_returns_dashboard_data() -> None:
    checked_at = datetime.now(timezone.utc)
    summaries = [
        ServiceSummary(
            id=1,
            name="GitHub",
            url="https://github.com/",
            is_active=True,
            status=ServiceStatus.UP,
            response_time_ms=82.0,
            checked_at=checked_at,
        ),
        ServiceSummary(
            id=2,
            name="Discord",
            url="https://discord.com/",
            is_active=True,
            status=ServiceStatus.DEGRADED,
            response_time_ms=150.0,
            checked_at=checked_at,
        ),
    ]

    with patch(
        "app.api.services.list_service_summaries",
        return_value=summaries,
    ):
        response = client.get("/api/services/summary")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "GitHub",
            "url": "https://github.com/",
            "is_active": True,
            "status": "up",
            "response_time_ms": 82.0,
            "checked_at": checked_at.isoformat().replace("+00:00", "Z"),
        },
        {
            "id": 2,
            "name": "Discord",
            "url": "https://discord.com/",
            "is_active": True,
            "status": "degraded",
            "response_time_ms": 150.0,
            "checked_at": checked_at.isoformat().replace("+00:00", "Z"),
        },
    ]


def test_service_summary_endpoint_returns_empty_list() -> None:
    with patch(
        "app.api.services.list_service_summaries",
        return_value=[],
    ):
        response = client.get("/api/services/summary")

    assert response.status_code == 200
    assert response.json() == []
