from os import getenv

import requests
import time

class RootMeApi() :
    """
    Class that provides information fetched from the Root-me.org API
     -> needs a rate_limiter object to send all the requests at a maximum rate of 25 req/sec
    """

    def __init__(self) :
        self.url = "https://api.www.root-me.org/"
        self.API_KEY = getenv("API_KEY_ROOTME")
