import requests

import pytest

from api.rate_limiter import (
    DEFAULT_MAX_ATTEMPT,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_TIMEOUT_DELAY,
    DEFAULT_IDLE_STATE_SLEEP,
    RateLimiter,
    RequestEntry,
    RateLimiterError,
    RLErrorWithPause,
)


@pytest.mark.asyncio
async def test_default_values(monkeypatch):
    monkeypatch.delenv("MAX_API_ATTEMPT", raising=False)
    rate_limiter = RateLimiter()

    # pylint: disable-next=protected-access
    assert rate_limiter._max_attempt == DEFAULT_MAX_ATTEMPT
    assert rate_limiter._request_timeout == DEFAULT_REQUEST_TIMEOUT
    assert rate_limiter._timeout_delay == DEFAULT_TIMEOUT_DELAY
    assert rate_limiter._idle_state_sleep == DEFAULT_IDLE_STATE_SLEEP

    rate_limiter.task.cancel()


@pytest.mark.asyncio
async def test_env_max_attempt(monkeypatch):
    monkeypatch.setenv("MAX_API_ATTEMPT", "42")
    rate_limiter = RateLimiter()

    # pylint: disable-next=protected-access
    assert rate_limiter._max_attempt == 42

    rate_limiter.task.cancel()


@pytest.mark.parametrize(
    "testing_kwargs",
    [
        ({}),
        ({"message": "some message"}),
        ({"message": "some message %s; %s", "msg_args": ("arg1", "arg2")}),
        pytest.param(
            {"message": "too few args %s; %s", "msg_args": ("only one arg")},
            marks=pytest.mark.xfail,
        ),
        ({"log": None}),
        ({"log": None, "message": "some message"}),
    ],
)
def test_RateLimiterError(mocker, testing_kwargs):
    if "log" in testing_kwargs:
        def mock_log(message, *args):
            _ = message % args
        testing_kwargs["log"] = mocker.MagicMock(side_effect=mock_log)

    requ = RequestEntry("url", "cookies", 1, "GET")
    _ = RateLimiterError(requ, **testing_kwargs)

    if "log" in testing_kwargs:
        testing_kwargs["log"].assert_called_once()


def test_RLErrorWithPause(monkeypatch, mocker):
    super_init = mocker.MagicMock()
    monkeypatch.setattr("api.rate_limiter.RateLimiterError.__init__", super_init)

    requ = RequestEntry("url", "cookies", 1, "GET")
    time2wait = 10
    args = "some arg"
    kwargs = {"key": "some kwarg"}
    exc = RLErrorWithPause(requ, time2wait, *args, **kwargs)

    assert exc.time_to_wait == time2wait
    super_init.assert_called_once_with(requ, *args, **kwargs)


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


@pytest.mark.asyncio
async def test_too_many_request(monkeypatch, mocker):
    mocked_get = mocker.MagicMock()
    resp = mocker.MagicMock()

    resp.status_code = 429
    retry_after = -1
    resp.headers = {"Retry-After": retry_after}
    mocked_get.return_value = resp

    monkeypatch.setattr("requests.get", mocked_get)

    monkeypatch.setenv("MAX_API_ATTEMPT", "1")
    # Trigger test
    url = "url"
    cookies = {"cookie": "dummy"}
    rate_limiter = RateLimiter()

    with pytest.raises(RateLimiterError) as exc_info:
        await rate_limiter.make_request(url, cookies, "GET")
    assert exc_info.type is RateLimiterError
    assert isinstance(exc_info.value.__cause__, RLErrorWithPause)
    assert exc_info.value.__cause__.time_to_wait == retry_after
    assert rate_limiter.is_idle()

    mocked_get.assert_called_once_with(url, cookies=cookies, timeout=DEFAULT_REQUEST_TIMEOUT)

    # Clean task properly
    rate_limiter.task.cancel()


@pytest.mark.asyncio
async def test_request_times_out(monkeypatch, mocker):
    mocked_get = mocker.Mock(side_effect=requests.exceptions.Timeout)
    monkeypatch.setattr("requests.get", mocked_get)

    monkeypatch.setenv("MAX_API_ATTEMPT", "1")

    # Trigger test
    url = "url"
    cookies = {"cookie": "dummy"}
    timeout_delay = -1
    rate_limiter = RateLimiter(timeout_delay=-1)

    # Assertions
    with pytest.raises(RateLimiterError) as exc_info:
        await rate_limiter.make_request(url, cookies, "GET")
    assert exc_info.type is RateLimiterError
    assert isinstance(exc_info.value.__cause__, RLErrorWithPause)
    assert exc_info.value.__cause__.time_to_wait == timeout_delay
    assert rate_limiter.is_idle()

    mocked_get.assert_called_once_with(url, cookies=cookies, timeout=DEFAULT_REQUEST_TIMEOUT)

    # Clean task properly
    rate_limiter.task.cancel()
