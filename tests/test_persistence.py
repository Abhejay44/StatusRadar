from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.monitoring.checker import CheckResult
from app.monitoring.persistence import save_check_result


def test_save_check_result_persists_health_check() -> None:
    db = MagicMock(spec=Session)
    result = CheckResult(
        status_code=200,
        response_time_ms=125.5,
        success=True,
    )

    health_check = save_check_result(
        db=db,
        service_id=7,
        result=result,
    )

    assert health_check.service_id == 7
    assert health_check.status_code == 200
    assert health_check.response_time_ms == 125.5
    assert health_check.success is True
    assert health_check.error_message is None

    db.add.assert_called_once_with(health_check)
    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(health_check)
    db.rollback.assert_not_called()


def test_save_check_result_rolls_back_when_commit_fails() -> None:
    db = MagicMock(spec=Session)
    db.commit.side_effect = SQLAlchemyError("commit failed")

    result = CheckResult(
        status_code=None,
        response_time_ms=None,
        success=False,
        error_message="Request timed out",
    )

    with pytest.raises(SQLAlchemyError, match="commit failed"):
        save_check_result(
            db=db,
            service_id=7,
            result=result,
        )

    db.rollback.assert_called_once_with()
    db.refresh.assert_not_called()
