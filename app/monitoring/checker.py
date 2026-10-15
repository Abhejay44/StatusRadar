from dataclasses import dataclass
from time import perf_counter

import httpx


@dataclass(frozen=True)
class CheckResult:
    status_code: int | None
    response_time_ms: float | None
    success: bool
    error_message: str | None = None


async def check_service(
    url: str,
    client: httpx.AsyncClient | None = None,
) -> CheckResult:
    owns_client = client is None
    http_client = client or httpx.AsyncClient(timeout=10.0)

    try:
        started_at = perf_counter()
        response = await http_client.get(url, follow_redirects=True)
        response_time_ms = (perf_counter() - started_at) * 1000

        return CheckResult(
            status_code=response.status_code,
            response_time_ms=response_time_ms,
            success=200 <= response.status_code < 400,
        )
    except httpx.RequestError as exc:
        return CheckResult(
            status_code=None,
            response_time_ms=None,
            success=False,
            error_message=str(exc),
        )
    finally:
        if owns_client:
            await http_client.aclose()
