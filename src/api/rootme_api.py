from os import getenv

from api.rate_limiter import RateLimiter
import requests
import time

class RootMeApi() :
    """
    Class that provides information fetched from the Root-me.org API
     -> needs a rate_limiter object to send all the requests at a maximum rate of 25 req/sec
    """

    def __init__(self,rate_limiter : RateLimiter) :
        if getenv("API_KEY_ROOTME") is not None :
            self.API_KEY = getenv("API_KEY_ROOTME")
        else :
            raise Exception("API_KEY_ROOTME is not set.")
        self.url = "https://api.www.root-me.org/"
        self.rate_limiter = rate_limiter
    
    async def GetChallengeById(self,id) :
        """
        Get a challenge from the API
        -> returns the raw json for now
        """
        #use the api_key in the cookies
        cookies = {"api_key": self.API_KEY.strip('"') }
        # ask the rate limiter for the request
        data = await self.rate_limiter.make_request(f"https://api.www.root-me.org/challenges/{id}",cookies,"GET")
        return(data)
    
    async def GetUserById(self,id) :
        """
        Get a user from the API
        -> returns the raw json for now
        """
        #use the api_key in the cookies
        cookies = {"api_key": self.API_KEY.strip('"') }
        # ask the rate limiter for the request
        data = await self.rate_limiter.make_request(f"https://api.www.root-me.org/auteurs/{id}",cookies,"GET")
        return(data)