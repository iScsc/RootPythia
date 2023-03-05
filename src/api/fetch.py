from os import getenv

import requests
import time
import json

class ApiRootMe() :
    """Class that takes care of sending the requests to the Root-me.org API"""

    def __init__(self) -> None:
        self.url = "https://api.www.root-me.org/"