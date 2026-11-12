from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from app.models.service import Service
from app.services.service_registry import list_active_services


def test_list_active_services_returns_active_services() -> None:
    db = MagicMock(spec=Session)

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

    db.scalars.return_value.all.return_value = services

    result = list_active_services(db)

    assert result == services
    db.scalars.assert_called_once()
