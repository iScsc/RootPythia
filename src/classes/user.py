# pylint: disable=too-few-public-methods
class User() :
    """Class for the User object"""
    def __init__(self, data: dict):
        """
            idx: int,
            username: str,
            score :int,
            rank: int,
            solves: int,
        """
        parsed_data = User.parse_rootme_user_data(data)

        # see keys and parse_rootme_user_data for attribute list and values
        for key, value in parsed_data.items():
            setattr(self, key, value)

        self.nb_new_solves = 0

    @staticmethod
    def keys():
        return ["idx", "username", "score", "rank", "nb_solves"]

    @staticmethod
    def parse_rootme_user_data(data):
        """A static method that returns a tuple of few user data extracted from raw RootMe API data"""

        idx = int(data["id_auteur"])
        username = data["nom"]
        score = int(data["score"])
        rank = int(data["position"])
        nb_solves = len(data["validations"])

        keys = User.keys()
        return {keys[0]: idx, keys[1]: username, keys[2]: score, keys[3]: rank, keys[4]: nb_solves}

    def __repr__(self):
        return f"User: id={self.idx}, username={self.username}, score={self.score}, rank={self.rank}, solves={self.nb_solves}"

    def update_new_solves(self, raw_user_data):
        parsed_data = User.parse_rootme_user_data(raw_user_data)

        self.nb_new_solves = parsed_data["nb_solves"] - self.nb_solves

    def has_new_solves(self):
        return self.nb_new_solves != 0
