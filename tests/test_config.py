import pytest

from app.core.config import get_database_url


def test_get_database_url_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    expected_url = (
        "postgresql+psycopg://test_user:test_password@localhost:5432/statusradar_test"
    )
    monkeypatch.setenv("DATABASE_URL", expected_url)

    assert get_database_url() == expected_url


def test_get_database_url_requires_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        get_database_url()
