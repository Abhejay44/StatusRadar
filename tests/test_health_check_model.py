from datetime import datetime

import pytest
from sqlalchemy import Boolean, DateTime, Float, Integer, String


def test_health_check_model_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://test_user:test_password@localhost:5432/statusradar_test",
    )

    from app.models.service import Service  # noqa: F401
    from app.models.health_check import HealthCheck

    table = HealthCheck.__table__

    assert table.name == "health_checks"
    assert set(table.columns.keys()) == {
        "id",
        "service_id",
        "status_code",
        "response_time_ms",
        "success",
        "error_message",
        "checked_at",
    }

    assert isinstance(table.c.id.type, Integer)
    assert table.c.id.primary_key is True

    assert isinstance(table.c.service_id.type, Integer)
    assert table.c.service_id.nullable is False
    foreign_key = next(iter(table.c.service_id.foreign_keys))
    assert foreign_key.target_fullname == "services.id"

    assert isinstance(table.c.status_code.type, Integer)
    assert table.c.status_code.nullable is True

    assert isinstance(table.c.response_time_ms.type, Float)
    assert table.c.response_time_ms.nullable is True

    assert isinstance(table.c.success.type, Boolean)
    assert table.c.success.nullable is False

    assert isinstance(table.c.error_message.type, String)
    assert table.c.error_message.nullable is True

    assert isinstance(table.c.checked_at.type, DateTime)
    assert table.c.checked_at.nullable is False
    assert table.c.checked_at.type.timezone is True
    assert table.c.checked_at.type.python_type is datetime
