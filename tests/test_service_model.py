from datetime import datetime

import pytest
from sqlalchemy import Boolean, DateTime, Integer, String


def test_service_model_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://test_user:test_password@localhost:5432/statusradar_test",
    )

    from app.models.service import Service

    table = Service.__table__

    assert table.name == "services"
    assert set(table.columns.keys()) == {
        "id",
        "name",
        "url",
        "is_active",
        "created_at",
    }

    assert isinstance(table.c.id.type, Integer)
    assert table.c.id.primary_key is True

    assert isinstance(table.c.name.type, String)
    assert table.c.name.nullable is False

    assert isinstance(table.c.url.type, String)
    assert table.c.url.nullable is False

    assert isinstance(table.c.is_active.type, Boolean)
    assert table.c.is_active.nullable is False
    assert table.c.is_active.default.arg is True

    assert isinstance(table.c.created_at.type, DateTime)
    assert table.c.created_at.nullable is False
    assert table.c.created_at.type.timezone is True
    assert table.c.created_at.type.python_type is datetime
