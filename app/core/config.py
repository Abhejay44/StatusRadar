import os


def get_database_url() -> str:
    """Return the PostgreSQL database URL configured for the application."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    return database_url


def get_monitor_interval_seconds() -> float:
    """Return the delay between automatic monitoring cycles."""
    raw_value = os.getenv("MONITOR_INTERVAL_SECONDS", "60")

    try:
        interval = float(raw_value)
    except ValueError as exc:
        raise RuntimeError(
            "MONITOR_INTERVAL_SECONDS must be a number"
        ) from exc

    if interval <= 0:
        raise RuntimeError(
            "MONITOR_INTERVAL_SECONDS must be greater than 0"
        )

    return interval
