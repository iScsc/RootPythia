# pylint: disable=too-few-public-methods
class User() :
    """Class for the User object"""
    def __init__(self, data: dict):
        """
            idx: int,
            username: str,
            score :int,
            rank: int
        """
        parsed_data = User.parse_rootme_user_data(data)
        (self.idx, self.username, self.score, self.rank) = parsed_data

    @staticmethod
    def parse_rootme_user_data(data):
        """A static method that returns a tuple of few user data extracted from raw RootMe API data"""

        idx = int(data["id_auteur"])
        username = data["nom"]
        score = int(data["score"])
        rank = int(data["position"])

        return (idx, username, score, rank)

    def __repr__(self):
        return f"User: id={self.idx}, username={self.username}, score={self.score}, rank={self.rank}"
