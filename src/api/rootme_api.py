import logging

from os import getenv
from api.rate_limiter import RLRequestFailed, RateLimiter

class RootMeAPIError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class RootMeAPIManager:
    """
    Class that provides information fetched from the Root-me.org API
     -> needs a rate_limiter object to send all the requests at a maximum rate of 25 req/sec
    """

    def __init__(self, rate_limiter: RateLimiter):
        if getenv("API_KEY_ROOTME") is not None:
            self.API_KEY = getenv("API_KEY_ROOTME")
        else:
            raise RuntimeError("API_KEY_ROOTME is not set.")
        if getenv("API_URL") is not None:
            self.API_URL = getenv("API_URL")
        else:
            raise RuntimeError("API_URL is not set.")
        self.rate_limiter = rate_limiter
        self.logger = logging.getLogger(__name__)

    def get_rate_limiter(self):
        return self.rate_limiter

    async def get_challenge_by_id(self, _id):
        """
        Get a challenge from the API
        -> returns the raw json for now
        """
        # use the api_key in the cookies
        request_url = f"{self.API_URL}/challenges/{_id}"
        cookies = {"api_key": self.API_KEY.strip('"')}
        request_method = "GET"
        # ask the rate limiter for the request
        try:
            data = await self.rate_limiter.make_request(
                request_url, cookies, request_method
            )
        except RLRequestFailed as exc:
            self.logger.error("%s Request to get challenge %s failed.", request_method, request_url)
            raise RootMeAPIError() # Handle the fact the request is wrong
        return data

    async def get_user_by_id(self, _id):
        """
        Get a user from the API
        -> returns the raw json for now
        """
        # use the api_key in the cookies
        request_url = f"{self.API_URL}/auteurs/{_id}"
        cookies = {"api_key": self.API_KEY.strip('"')}
        request_method = "GET"
        # ask the rate limiter for the request
        try:
            data = await self.rate_limiter.make_request(
                request_url, cookies, request_method
            )
        except RLRequestFailed as exc:
            self.logger.error("%s Request to get user %s failed.", request_method, request_url)
            raise RootMeAPIError()
        return data
