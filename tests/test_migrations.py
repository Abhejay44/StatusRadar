from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_initial_revision_is_discoverable() -> None:
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)

    assert script.get_current_head() == "0001"

    revision = script.get_revision("0001")
    assert revision is not None
    assert revision.down_revision is None
