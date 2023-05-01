import asyncio
import logging
import uuid
from datetime import datetime
from os import getenv
import requests



class RequestEntry() :
    """
    Class for request object to put in the queue for the rate limiter
    """
    def __init__(self,url,cookies,key,method) -> None:
        self.url = url
        self.cookies = cookies
        self.key = key
        self.method = method

class RateLimiter() :
    """
    Class that takes care of sending the requests at a maximum rate (25/sec) 
        and giving back the result to the calling functions when it is received (async probably)
    """
    _max_retry = 0

    def __init__(self) :
        self.requests = {}
        self.queue = asyncio.Queue()
        #set a max_retry cap
        if getenv("MAX_API_RETRY") is not None :
            self._max_retry = int(getenv("MAX_API_RETRY"))
        else :
            self._max_retry = 3

        asyncio.create_task(self.handle_requests())


    async def handle_requests(self) :
        logging.info("Starting rate_limiter task...")

        #local variable
        last_time_request = datetime.now()
        retry = False
        retry_count = 0

        while True :
            #take a new request from the queue
            if not retry :
                request = await self.queue.get()
                logging.debug(
                    "Treating item in queue : %s -> %s + %s ",
                    request.key,request.url,request.cookies
                    )
                retry_count = 0
            else :
                #request stays the same
                logging.debug(
                    "Retrying %s item in queue : %s -> %s + %s ",
                    retry_count,request.key,request.url,request.cookies
                    )
                retry = False

            # wait 50ms for rate limitation purpose ;)
            if (0.050 - (datetime.now() - last_time_request).total_seconds()) > 0.01 :
                await asyncio.sleep(0.050 - (datetime.now() - last_time_request).total_seconds())

            if request.method == "GET" :
                # keep track of the last time a request was made
                last_time_request = datetime.now()
                # actually send the GET request
                resp = requests.get(request.url, cookies=request.cookies)
                if resp.status_code != 200 :
                    logging.warning(
                        "Request : GET %s + %s failed with response code %s",
                        request.url,request.cookies,resp.status_code
                        )
                    if retry_count < self._max_retry :
                        retry = True
                        retry_count += 1
                    else :
                        logging.error(
                            "Failed to get request after %s attempt. We could be banned :(",
                            self._max_retry
                            )
                        raise RuntimeError("Looks like a ban to me :'(")
                else :
                    data = resp.json()
            else :
                raise NotImplementedError("Only GET method implemented for now.")

            # we send back the response and trigger the event of this request
            self.requests[request.key]['result'] = data
            self.requests[request.key]['event'].set()
            # finally we inform the queue of the end of the process
            self.queue.task_done()

    async def make_request(self,url,cookies,method) :
        key = uuid.uuid4().hex

        logging.debug("Request for %s added to queue -> %s",url,key)

        event = asyncio.Event()
        self.requests[key] = {}
        self.requests[key]['event'] = event
        request = RequestEntry(url, cookies, key, 'GET')
        await self.queue.put(request)
        await event.wait()

        result = self.requests[key]['result']

        del self.requests[key]

        return result
