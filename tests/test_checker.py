import asyncio

import httpx

from app.monitoring.checker import CheckResult, check_service


def test_check_service_success() -> None:
    async def run_test() -> CheckResult:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, request=request)

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler)
        ) as client:
            return await check_service("https://example.test", client=client)

    result = asyncio.run(run_test())

    assert result.status_code == 200
    assert result.success is True
    assert result.response_time_ms is not None
    assert result.response_time_ms >= 0
    assert result.error_message is None


def test_check_service_503_is_unsuccessful() -> None:
    async def run_test() -> CheckResult:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(503, request=request)

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler)
        ) as client:
            return await check_service("https://example.test", client=client)

    result = asyncio.run(run_test())

    assert result.status_code == 503
    assert result.success is False
    assert result.response_time_ms is not None
    assert result.error_message is None


def test_check_service_timeout_is_handled() -> None:
    async def run_test() -> CheckResult:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("Request timed out", request=request)

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler)
        ) as client:
            return await check_service("https://example.test", client=client)

    result = asyncio.run(run_test())

    assert result.status_code is None
    assert result.response_time_ms is None
    assert result.success is False
    assert result.error_message is not None
    assert "timed out" in result.error_message.lower()
