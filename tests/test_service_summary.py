from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from app.models.service import Service
from app.monitoring.status import ServiceStatus, ServiceStatusResult
from app.services.service_summary import list_service_summaries


def test_list_service_summaries_combines_service_and_status_data() -> None:
    db = MagicMock(spec=Session)
    checked_at = datetime.now(timezone.utc)

    services = [
        Service(
            id=1,
            name="GitHub",
            url="https://github.com/",
            is_active=True,
        ),
        Service(
            id=2,
            name="Discord",
            url="https://discord.com/",
            is_active=False,
        ),
    ]

    status_results = [
        ServiceStatusResult(
            service_id=1,
            status=ServiceStatus.UP,
            response_time_ms=82.0,
            checked_at=checked_at,
        ),
        ServiceStatusResult(
            service_id=2,
            status=ServiceStatus.UNKNOWN,
            response_time_ms=None,
            checked_at=None,
        ),
    ]

    with (
        patch(
            "app.services.service_summary.list_services",
            return_value=services,
        ),
        patch(
            "app.services.service_summary.get_current_service_status",
            side_effect=status_results,
        ) as mock_get_current_service_status,
    ):
        summaries = list_service_summaries(db)

    assert len(summaries) == 2

    assert summaries[0].id == 1
    assert summaries[0].name == "GitHub"
    assert summaries[0].status == ServiceStatus.UP
    assert summaries[0].response_time_ms == 82.0
    assert summaries[0].checked_at == checked_at

    assert summaries[1].id == 2
    assert summaries[1].is_active is False
    assert summaries[1].status == ServiceStatus.UNKNOWN

    assert mock_get_current_service_status.call_count == 2
