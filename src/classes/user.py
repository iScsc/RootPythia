# pylint: disable=too-few-public-methods
class User() :
    """Class for user object"""
    def __init__(self,idx: int,username: str,score :int,rank: int) -> None:
        self.idx = idx
        self.username = username
        self.score = score
        self.rank = rank
