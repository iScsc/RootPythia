import asyncio
import logging
import uuid
from datetime import datetime
from os import getenv
import requests

DEFAULT_MAX_RETRY = 3


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


class RateLimiter:
    """
    Class that takes care of sending the requests at a maximum rate (25/sec)
        and giving back the result to the calling functions when it is received (async probably)
    """

    def __init__(self):
        self.requests = {}
        self.queue = asyncio.Queue()
        # set a max_retry cap
        if getenv("MAX_API_RETRY") is not None:
            self._max_retry = int(getenv("MAX_API_RETRY"))
        else:
            self._max_retry = DEFAULT_MAX_RETRY

        self.task = asyncio.create_task(self.handle_requests())

        self.logger = logging.getLogger(__name__)

    async def handle_requests(self):
        self.logger.info("Starting rate_limiter task...")

        # local variable
        last_time_request = datetime.now()
        retry = False
        retry_count = 0

        while True:
            # take a new request from the queue
            if not retry:
                request = await self.queue.get()
                self.logger.debug(
                    "Treating item in queue : %s -> %s + %s ",
                    request.key,
                    request.url,
                    request.cookies,
                )
                retry_count = 0
            else:
                # request stays the same
                self.logger.debug(
                    "Retrying %s item in queue : %s -> %s + %s ",
                    retry_count,
                    request.key,
                    request.url,
                    request.cookies,
                )
                retry = False

            # wait 50ms for rate limitation purpose ;)
            loop_duration = (datetime.now() - last_time_request).total_seconds()
            if (0.050 - loop_duration) > 0.01:
                await asyncio.sleep(0.050 - loop_duration)

            if request.method == "GET":
                # keep track of the last time a request was made
                last_time_request = datetime.now()
                # actually send the GET request
                resp = requests.get(request.url, cookies=request.cookies)
                if resp.status_code != 200:
                    self.logger.warning(
                        "Request : GET %s + %s failed with response code %s",
                        request.url,
                        request.cookies,
                        resp.status_code,
                    )
                    if retry_count >= self._max_retry:
                        self.logger.error(
                            "Failed to get request after %s attempt. We could be banned :(",
                            self._max_retry,
                        )
                        raise RuntimeError("Looks like a ban to me :'(")

                    # Retry the request
                    retry = True
                    retry_count += 1
                    continue

            else:
                raise NotImplementedError("Only GET method implemented for now.")

            # The request did pass all the tests successfully
            # we send back the response and trigger the event of this request
            self.requests[request.key]["result"] = resp.json()
            self.requests[request.key]["event"].set()
            # finally we inform the queue of the end of the process
            self.queue.task_done()

    async def make_request(self, url, cookies, method):
        key = uuid.uuid4().hex

        self.logger.debug("Request for %s added to queue -> %s", url, key)

        event = asyncio.Event()
        self.requests[key] = {}
        self.requests[key]["event"] = event
        request = RequestEntry(url, cookies, key, "GET")
        await self.queue.put(request)
        await event.wait()

        result = self.requests[key]["result"]

        del self.requests[key]

        return result
