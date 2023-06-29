import asyncio
import logging
import uuid
from datetime import datetime
from os import getenv
import requests

DEFAULT_MAX_ATTEMPT = 3
DEFAULT_MAX_TIMEOUT = 20


class RateLimiterError(Exception):
    def __init__(self, request, log=None, message="", msg_args=()):
        if message:
            message = message % msg_args
            super().__init__(message)

        self.request = request
        if log:
            message = f"Request %s: %s + %s {message}"
            log(message, request.method, request.url, request.cookie)


class RLErrorWithPause(RateLimiterError):
    def __init__(self, request, timeToWait, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.timeToWait = timeToWait


# pylint: disable=too-few-public-methods
class RequestEntry:
    """
    Class for request object to put in the queue for the rate limiter
    """

    def __init__(self, url, cookies, key, method) -> None:
        self.url = url
        self.cookies = cookies
        self.key = key
        self.method = method
        self.attempt = 0


class RateLimiter:
    """
    Class that takes care of sending the requests at a maximum rate (25/sec)
        and giving back the result to the calling functions when it is received (async probably)
    """

    def __init__(self):
        self.requests = {}
        self.queue = asyncio.Queue()
        # set a max_retry cap
        if getenv("MAX_API_ATTEMPT") is not None:
            self._max_attempt = int(getenv("MAX_API_ATTEMPT"))
        else:
            self._max_attempt = DEFAULT_MAX_ATTEMPT

        self.task = asyncio.create_task(self.handle_requests())

        self.logger = logging.getLogger(__name__)

    def handle_get_request(self, request):
        try:
            resp = requests.get(request.url, cookies=request.cookies, timeout=DEFAULT_MAX_TIMEOUT)
        except requests.exceptions.Timeout as exc:
            raise RateLimiterError(request, self.logger.error, "Timeout") from exc

        if resp.status_code == 200:
            return resp.json()

        elif resp.status_code == 429:
            try:
                timeToWait = int(resp.headers["Retry-After"])
            except (KeyError, ValueError) as exc:
                raise RateLimiterError(
                    request, self.logger.error, "Too many requests (429) and cannot parse headers"
                ) from exc

            raise RLErrorWithPause(
                request, timeToWait, self.logger.warning, "Too many requests (429)"
            )

        else:
            raise RateLimiterError(request, self.logger.error, "Unknown error")

    async def handle_requests(self):
        self.logger.info("Starting rate_limiter task...")

        # local variable
        last_time_request = datetime.now()

        while True:
            # wait 50ms for rate limitation purpose ;)
            loop_duration = (datetime.now() - last_time_request).total_seconds()
            if (0.050 - loop_duration) > 0.01:
                await asyncio.sleep(0.050 - loop_duration)

            # take a new request from the queue
            request = await self.queue.get()

            if request.attempts == 0:
                self.logger.debug(
                    "Treating item in queue : %s -> %s + %s ",
                    request.key,
                    request.url,
                    request.cookies,
                )
            else:
                # request stays the same
                self.logger.info(
                    "Retrying %s/%s item in queue : %s -> %s + %s",
                    request.attempt,
                    self._max_attempt,
                    request.key,
                    request.url,
                    request.cookies,
                )

            if request.method == "GET":
                # keep track of the last time a request was made
                last_time_request = datetime.now()

                try:
                    self.requests[request.key]["result"] = self.handle_get_request(request)
                except RateLimiterError as exc:
                    if request.attempt < self._max_attempt:
                        request.attempt += 1
                        self.queue.put(request)
                        continue

                    # set the exception
                    self.requests[request.key]["exception"] = (
                        RateLimiterError(request, self.logger.error, "Too many attempts"),
                        exc,
                    )

            else:
                self.requests[request.key]["exception"] = (
                    NotImplementedError("Only GET method implemented for now."),
                    None,
                )

            self.requests[request.key]["event"].set()
            self.queue.task_done()

    async def make_request(self, url, cookies, method = "GET"):
        key = uuid.uuid4().hex

        self.logger.debug("Request for %s added to queue -> %s", url, key)

        event = asyncio.Event()
        self.requests[key] = {}
        self.requests[key]["event"] = event
        self.requests[key]["exception"] = None
        request = RequestEntry(url, cookies, key, method)
        await self.queue.put(request)
        await event.wait()

        # if an error occured, raise exception
        if self.requests[key]["exception"] is not None:
            exc, prev_exc = self.requests[key]["exception"]
            if prev_exc is not None:
                raise exc from prev_exc
            raise exc

        result = self.requests[key]["result"]
        del self.requests[key]
        return result
