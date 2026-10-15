import os

import pytest
from sqlalchemy import create_engine, inspect, text


def test_postgresql_schema_matches_initial_migration() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL is not set; skipping PostgreSQL integration test")

    engine = create_engine(database_url)

    try:
        inspector = inspect(engine)
        table_names = set(inspector.get_table_names())

        assert {"services", "health_checks", "alembic_version"} <= table_names

        foreign_keys = inspector.get_foreign_keys("health_checks")
        assert any(
            foreign_key["constrained_columns"] == ["service_id"]
            and foreign_key["referred_table"] == "services"
            and foreign_key["referred_columns"] == ["id"]
            for foreign_key in foreign_keys
        )

        with engine.connect() as connection:
            revision = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()

        assert revision == "0001"
    finally:
        engine.dispose()
