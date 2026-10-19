from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.main import app
from app.models.service import Service


def override_get_db():
    yield MagicMock(spec=Session)


client = TestClient(app)
app.dependency_overrides[get_db] = override_get_db


def test_create_service_endpoint_returns_created_service() -> None:
    created_at = datetime.now(timezone.utc)
    service = Service(
        id=1,
        name="GitHub",
        url="https://github.com/",
        is_active=True,
        created_at=created_at,
    )

    with patch(
        "app.api.services.create_service",
        return_value=service,
    ) as mock_create_service:
        response = client.post(
            "/api/services",
            json={
                "name": "GitHub",
                "url": "https://github.com",
            },
        )

    assert response.status_code == 201
    assert response.json()["name"] == "GitHub"
    assert response.json()["url"] == "https://github.com/"
    assert response.json()["is_active"] is True
    mock_create_service.assert_called_once()


def test_list_services_endpoint_returns_services() -> None:
    created_at = datetime.now(timezone.utc)
    services = [
        Service(
            id=1,
            name="GitHub",
            url="https://github.com/",
            is_active=True,
            created_at=created_at,
        ),
        Service(
            id=2,
            name="Discord",
            url="https://discord.com/",
            is_active=True,
            created_at=created_at,
        ),
    ]

    with patch(
        "app.api.services.list_services",
        return_value=services,
    ):
        response = client.get("/api/services")

    assert response.status_code == 200
    assert [service["name"] for service in response.json()] == [
        "GitHub",
        "Discord",
    ]


def test_create_service_endpoint_rejects_invalid_url() -> None:
    response = client.post(
        "/api/services",
        json={
            "name": "Broken",
            "url": "not-a-url",
        },
    )

    assert response.status_code == 422
