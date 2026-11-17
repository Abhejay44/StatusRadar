import pytest

from app.core.config import (
    get_database_url,
    get_monitor_interval_seconds,
)


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


def test_monitor_interval_defaults_to_60_seconds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MONITOR_INTERVAL_SECONDS", raising=False)

    assert get_monitor_interval_seconds() == 60.0


def test_monitor_interval_reads_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MONITOR_INTERVAL_SECONDS", "15")

    assert get_monitor_interval_seconds() == 15.0


@pytest.mark.parametrize("value", ["0", "-1", "not-a-number"])
def test_monitor_interval_rejects_invalid_values(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    monkeypatch.setenv("MONITOR_INTERVAL_SECONDS", value)

    with pytest.raises(RuntimeError, match="MONITOR_INTERVAL_SECONDS"):
        get_monitor_interval_seconds()
