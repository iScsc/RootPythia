from os import getenv

import requests
import time

class ApiRootMe() :
    """
    Class that takes care of sending the requests to the Root-me.org API
    These functions should not be launched into separate threads in order to avoid being banned by the API (As long as a proper rate limiting design hasn't been implemented) 
    """

    def __init__(self) :
        self.url = "https://api.www.root-me.org/"
        self.API_KEY = getenv("API_KEY_ROOTME")
