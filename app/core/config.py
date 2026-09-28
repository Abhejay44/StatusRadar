import os


def get_database_url() -> str:
    """Return the PostgreSQL database URL configured for the application."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    return database_url
