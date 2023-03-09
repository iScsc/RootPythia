class User(object) :
    """Class for user object"""
    def __init__(self,idx,username,score,rank) -> None:
        self.idx = idx
        self.username = username
        self.score = score
        self.rank = rank