import pytest

from api.rate_limiter import DEFAULT_MAX_RETRY, RateLimiter


@pytest.mark.asyncio
async def test_default_max_retry(monkeypatch):
    monkeypatch.delenv("MAX_API_RETRY", raising=False)
    rate_limiter = RateLimiter()

    # pylint: disable-next=protected-access
    assert rate_limiter._max_retry == DEFAULT_MAX_RETRY

    rate_limiter.task.cancel()


@pytest.mark.asyncio
async def test_env_max_retry(monkeypatch):
    monkeypatch.setenv("MAX_API_RETRY", "42")
    rate_limiter = RateLimiter()

    # pylint: disable-next=protected-access
    assert rate_limiter._max_retry == 42

    rate_limiter.task.cancel()
