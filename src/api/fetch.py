from os import getenv

import requests
import time

class ApiRootMe() :
    """
    Class that takes care of sending the requests to the Root-me.org API
    These functions should not be launched into separate threads in order to avoid being banned by the API (As long as a proper rate limiting design hasn't been implemented) 
    """

    def __init__(self) -> None:
        self.url = "https://api.www.root-me.org/"
        self.API_KEY = getenv("API_KEY_ROOTME")

    def GetChallengeById(self,id) :
        """
        Get a challenge from the API
        -> returns the raw json for now
        """
        cookies = {"api_key": self.API_KEY.strip('"') }
        resp = requests.get(f"https://api.www.root-me.org/challenges/{id}", cookies=cookies)
        #raise exception if the request does not work
        if resp.status_code != 200:
            raise Exception(f"GET /challenges/{id} -> {resp.status_code}")
        # take response as json
        data = resp.json()
        time.sleep(0.050)
        
        return(data)
    
    def GetUserById(self,id) :
        """
        Get a user from the API
        -> returns the raw json for now
        """
        cookies = {"api_key": self.API_KEY.strip('"') }
        resp = requests.get(f"https://api.www.root-me.org/auteurs/{id}", cookies=cookies)
        #raise exception if the request does not work
        if resp.status_code != 200:
            raise Exception(f"GET /auteurs/{id} -> {resp.status_code}")
        # take response as json
        data = resp.json()
        time.sleep(0.050)
        
        return(data)

