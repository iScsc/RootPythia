import pytest

from api.rate_limiter import (
    DEFAULT_MAX_ATTEMPT,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_TIMEOUT_DELAY,
    RateLimiter,
)


@pytest.mark.asyncio
async def test_default_values(monkeypatch):
    monkeypatch.delenv("MAX_API_ATTEMPT", raising=False)
    rate_limiter = RateLimiter()

    # pylint: disable-next=protected-access
    assert rate_limiter._max_attempt == DEFAULT_MAX_ATTEMPT
    assert rate_limiter._request_timeout == DEFAULT_REQUEST_TIMEOUT
    assert rate_limiter._timeout_delay == DEFAULT_TIMEOUT_DELAY

    rate_limiter.task.cancel()


@pytest.mark.asyncio
async def test_env_max_attempt(monkeypatch):
    monkeypatch.setenv("MAX_API_ATTEMPT", "42")
    rate_limiter = RateLimiter()

    # pylint: disable-next=protected-access
    assert rate_limiter._max_attempt == 42

    rate_limiter.task.cancel()


@pytest.mark.asyncio
async def test_request_passes(monkeypatch, mocker):
    mocked_get = mocker.MagicMock()
    resp = mocker.MagicMock()

    data = {"some data": "when request returns"}
    resp.status_code = 200
    resp.json.return_value = data
    mocked_get.return_value = resp

    monkeypatch.setattr("requests.get", mocked_get)

    # Trigger test
    url = "url"
    cookies = {"cookie": "dummy"}
    request_timeout = -1
    rate_limiter = RateLimiter(request_timeout=request_timeout)

    result = await rate_limiter.make_request(url, cookies, "GET")

    mocked_get.assert_called_once_with(url, cookies=cookies, timeout=request_timeout)
    assert result is data

    # Clean task properly
    rate_limiter.task.cancel()
