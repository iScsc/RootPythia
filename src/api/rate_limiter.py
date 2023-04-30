import asyncio
import requests
import uuid

from datetime import datetime


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
    def __init__(self) :
        self.requests = {}
        self.queue = asyncio.Queue()
        asyncio.create_task(self.handle_requests())


    async def handle_requests(self) :
        print(f"Starting rate_limiter task...")
        last_time_request = datetime.now()
        while True :
            #take a new request from the queue
            request = await self.queue.get()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Treating item in queue : {request.key} -> {request.url} + {request.cookies} ")

            # wait 50ms for rate limitation purpose ;)
            if 0.050 - (datetime.now() - last_time_request) > 0.01 :
                await asyncio.sleep(0.050 - (datetime.now() - last_time_request))

            if request.method == "GET" :
                last_time_request = datetime.now()
                resp = requests.get(request.url, cookies=request.cookies)
                if resp.status_code != 200 :
                    raise Exception(f"GET {request.url} -> {resp.status_code}")
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

