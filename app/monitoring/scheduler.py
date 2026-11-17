import asyncio
import logging

import httpx

from app.core.config import get_monitor_interval_seconds
from app.core.database import SessionLocal
from app.monitoring.batch import monitor_active_services


logger = logging.getLogger(__name__)


async def run_monitoring_cycle(
    client: httpx.AsyncClient,
) -> None:
    db = SessionLocal()

    try:
        await monitor_active_services(
            db=db,
            client=client,
        )
    finally:
        db.close()


async def run_monitoring_loop() -> None:
    interval_seconds = get_monitor_interval_seconds()

    async with httpx.AsyncClient(timeout=10.0) as client:
        while True:
            try:
                await run_monitoring_cycle(client)
            except Exception:
                logger.exception("Automatic monitoring cycle failed")

            await asyncio.sleep(interval_seconds)
