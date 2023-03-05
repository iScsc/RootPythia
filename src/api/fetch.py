from os import getenv

import requests
import time
import json

class ApiRootMe() :
    """Class that takes care of sending the requests to the Root-me.org API"""

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
            raise Exception("GET /challenges/{id}".format(resp.status_code))
        # take response as json
        data = resp.json()
        
        return(data)


