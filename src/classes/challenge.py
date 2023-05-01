class Challenge():
    """Class for challenge object"""
    def __init__(self,
                 idx: int,
                 title: str,
                 category:str,
                 description: str,
                 pts: int,
                 difficulty: str):
        self.idx = idx
        self.title = title
        self.category = category
        self.description = description
        self.pts = pts
        self.difficulty = difficulty
