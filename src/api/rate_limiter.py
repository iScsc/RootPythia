import asyncio
import requests
import uuid

from datetime import datetime
from os import getenv


class RequestEntry(object) :
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
        print(f"Starting rate_limiter task...")
        
        #local variable
        last_time_request = datetime.now()
        retry = False
        retry_count = 0
        
        while True :
            #take a new request from the queue
            if retry :
                #request stays the same
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Retrying {retry_count} item in queue : {request.key} -> {request.url} + {request.cookies} ")
                retry = False
            else :
                request = await self.queue.get()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Treating item in queue : {request.key} -> {request.url} + {request.cookies} ")
                retry_count = 0

            # wait 50ms for rate limitation purpose ;)
            if (0.050 - (datetime.now() - last_time_request).total_seconds()) > 0.01 :
                await asyncio.sleep(0.050 - (datetime.now() - last_time_request).total_seconds())

            if request.method == "GET" :
                # keep track of the last time a request was made
                last_time_request = datetime.now()
                # actually send the GET request
                resp = requests.get(request.url, cookies=request.cookies)
                if resp.status_code != 200 :
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Request : GET {request.url} + {request.cookies} failed with response code {resp.status_code}")
                    if retry_count < self._max_retry :
                        retry = True
                        retry_count += 1
                    else :
                        raise Exception("Looks like a ban to me :'(")
                else :     
                    data = resp.json()
            else : 
                raise Exception("Only GET method implemented for now.")

            # we send back the response and trigger the event of this request
            self.requests[request.key]['result'] = data
            self.requests[request.key]['event'].set()
            # finally we inform the queue of the end of the process
            self.queue.task_done()

    async def make_request(self,url,cookies,method) :
        key = uuid.uuid4().hex

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Request for {url} added to queue -> {key}")

        event = asyncio.Event()
        self.requests[key] = {}
        self.requests[key]['event'] = event
        request = RequestEntry(url, cookies, key, 'GET')
        await self.queue.put(request)
        await event.wait()
        
        result = self.requests[key]['result']
        
        del self.requests[key]

        return result

