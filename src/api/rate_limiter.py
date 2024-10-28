import asyncio
import logging
import uuid
from datetime import datetime
from os import getenv
import requests

DEFAULT_MAX_ATTEMPT = 3
DEFAULT_REQUEST_TIMEOUT = 5
DEFAULT_TIMEOUT_DELAY = 10 * 60
DEFAULT_IDLE_STATE_SLEEP = 10


class RateLimiterError(Exception):
    def __init__(self, request, log=None, message="", msg_args=()):
        if message:
            message = message % msg_args
            super().__init__(message)

        self.request = request
        if log:
            message = f"Request %s: %s + %s {message}"
            log(message, request.method, request.url, request.cookies)


class RLErrorWithPause(RateLimiterError):
    def __init__(self, request, time_to_wait, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.time_to_wait = time_to_wait


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

    def __init__(self, request_timeout=None, timeout_delay=None, idle_state_sleep=None):
        self.requests = {}
        self.queue = asyncio.Queue()
        # set a max_retry cap
        if getenv("MAX_API_ATTEMPT") is not None:
            self._max_attempt = int(getenv("MAX_API_ATTEMPT"))
        else:
            self._max_attempt = DEFAULT_MAX_ATTEMPT

        self._waiting = False
        self._idle = False
        self._request_timeout = request_timeout or DEFAULT_REQUEST_TIMEOUT
        self._timeout_delay = timeout_delay or DEFAULT_TIMEOUT_DELAY
        self._idle_state_sleep = idle_state_sleep or DEFAULT_IDLE_STATE_SLEEP
        self.task = asyncio.create_task(self.handle_requests())
        self.logger = logging.getLogger(__name__)

    def go_idle(self, manually = False):
        self._idle = True
        if manually:
            self.logger.error("Entering idle state due to manual command")
        else:
            self.logger.error("Entering idle state due to previous errors")

    def is_idle(self):
        return self._idle

    def exit_idle(self):
        self.logger.info("Resuming from idle state")
        self._idle = False

    def is_waiting(self):
        return self._waiting

    async def wait(self, delay):
        self._waiting = True
        await asyncio.sleep(delay)
        self._waiting = False

    def handle_get_request(self, request):
        try:
            # TODO: we should really use a session object to persist cookies and TCP connection
            # https://requests.readthedocs.io/en/latest/user/advanced/#session-objects
            resp = requests.get(request.url, cookies=request.cookies, timeout=self._request_timeout)
        except requests.exceptions.Timeout as exc:
            raise RLErrorWithPause(
                request, self._timeout_delay, self.logger.error, "Timeout"
            ) from exc

        match resp.status_code:
            case 200:
                return resp.json()
            case 429:
                try:
                    time_to_wait = int(resp.headers["Retry-After"])
                except (KeyError, ValueError) as exc:
                    raise RateLimiterError(
                        request,
                        self.logger.error,
                        "Too many requests (429) and cannot parse headers",
                    ) from exc

                raise RLErrorWithPause(
                    request, time_to_wait, self.logger.warning, "Too many requests (429)"
                )
            case code:
                raise RateLimiterError(
                    request, self.logger.error, f"Unhandled response status: {code}"
                )

    async def handle_requests(self):
        self.logger.info("Starting rate_limiter task...")

        # local variable
        last_time_request = datetime.now()

        while True:
            if self._idle:
                await asyncio.sleep(self._idle_state_sleep)
                continue

            # wait 50ms for rate limitation purpose ;)
            loop_duration = (datetime.now() - last_time_request).total_seconds()
            if (0.050 - loop_duration) > 0.01:
                await asyncio.sleep(0.050 - loop_duration)

            # take a new request from the queue
            request = await self.queue.get()
            request.attempt += 1

            if request.attempt == 1:
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
                    if isinstance(exc, RLErrorWithPause):
                        await self.wait(exc.time_to_wait)

                    if request.attempt < self._max_attempt:
                        await self.queue.put(request)
                        continue

                    # set the exception
                    self.requests[request.key]["exception"] = (
                        RateLimiterError(request, self.logger.error, "Too many attempts"),
                        exc,
                    )
                except Exception as exc:
                    self.requests[request.key]["exception"] = (
                        RateLimiterError(
                            request, self.logger.error, "Unhandled error. Entering idle state."
                        ),
                        exc,
                    )

            else:
                self.requests[request.key]["exception"] = (
                    NotImplementedError("Only GET method implemented for now."),
                    None,
                )

            self.requests[request.key]["event"].set()
            self.queue.task_done()

    async def make_request(self, url, cookies, method="GET"):
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
            self.go_idle()
            exc, prev_exc = self.requests[key]["exception"]
            if prev_exc is not None:
                raise exc from prev_exc
            raise exc

        result = self.requests[key]["result"]
        del self.requests[key]
        return result
