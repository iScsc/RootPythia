from os import getenv
from api.rate_limiter import RateLimiter

class RootMeApi() :
    """
    Class that provides information fetched from the Root-me.org API
     -> needs a rate_limiter object to send all the requests at a maximum rate of 25 req/sec
    """

    def __init__(self,rate_limiter : RateLimiter) :
        if getenv("API_KEY_ROOTME") is not None :
            self.API_KEY = getenv("API_KEY_ROOTME")
        else :
            raise RuntimeError("API_KEY_ROOTME is not set.")
        if getenv("API_URL") is not None :
            self.API_URL = getenv("API_URL")
        else :
            raise RuntimeError("API_URL is not set.")
        self.rate_limiter = rate_limiter

    async def GetChallengeById(self,_id) :
        """
        Get a challenge from the API
        -> returns the raw json for now
        """
        #use the api_key in the cookies
        cookies = {
            "api_key": self.API_KEY.strip('"')
            }
        # ask the rate limiter for the request
        data = await self.rate_limiter.make_request(f"{self.API_URL}/challenges/{_id}",cookies,"GET")
        return data

    async def GetUserById(self,_id) :
        """
        Get a user from the API
        -> returns the raw json for now
        """
        #use the api_key in the cookies
        cookies = {"api_key": self.API_KEY.strip('"') }
        # ask the rate limiter for the request
        data = await self.rate_limiter.make_request(f"{self.API_URL}/auteurs/{_id}",cookies,"GET")
        return data
