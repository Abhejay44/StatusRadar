from datetime import datetime, timezone
from unittest.mock import MagicMock

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.service import Service
from app.services.service_registry import create_service, list_services


def test_create_service_persists_service() -> None:
    db = MagicMock(spec=Session)

    service = create_service(
        db=db,
        name="GitHub",
        url="https://github.com/",
    )

    assert service.name == "GitHub"
    assert service.url == "https://github.com/"
    assert service.is_active is True

    db.add.assert_called_once_with(service)
    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(service)
    db.rollback.assert_not_called()


def test_create_service_rolls_back_when_commit_fails() -> None:
    db = MagicMock(spec=Session)
    db.commit.side_effect = SQLAlchemyError("commit failed")

    try:
        create_service(
            db=db,
            name="GitHub",
            url="https://github.com/",
        )
    except SQLAlchemyError:
        pass
    else:
        raise AssertionError("Expected SQLAlchemyError")

    db.rollback.assert_called_once_with()
    db.refresh.assert_not_called()


def test_list_services_returns_services() -> None:
    db = MagicMock(spec=Session)

    services = [
        Service(
            id=1,
            name="GitHub",
            url="https://github.com/",
            is_active=True,
            created_at=datetime.now(timezone.utc),
        ),
        Service(
            id=2,
            name="Discord",
            url="https://discord.com/",
            is_active=True,
            created_at=datetime.now(timezone.utc),
        ),
    ]
    db.scalars.return_value.all.return_value = services

    result = list_services(db)

    assert result == services
    db.scalars.assert_called_once()
