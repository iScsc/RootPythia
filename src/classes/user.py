class InvalidUserData(Exception):
    pass


class User:
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

        self.idx = parsed_data["idx"]
        self.username = parsed_data["username"]
        self.score = parsed_data["score"]
        self.rank = parsed_data["rank"]
        self.nb_solves = parsed_data["nb_solves"]

        self.nb_new_solves = 0

    @staticmethod
    def keys():
        return ["idx", "username", "score", "rank", "nb_solves"]

    # TODO: move these static methods to rootme_api, it make more sense
    # or create a Parser object? we could then have a RootMeParser and a HTBParser
    # but then what's the point of the API Manager ?
    @staticmethod
    def parse_rootme_user_data(data):
        """
        A static method that returns a tuple of few user data extracted from raw RootMe API data
        """

        idx = int(data["id_auteur"])
        username = data["nom"]
        score = int(data["score"])
        _rank = data["position"]
        rank = int(_rank) if _rank != "" else 9999999
        nb_solves = len(data["validations"])

        keys = User.keys()
        return {keys[0]: idx, keys[1]: username, keys[2]: score, keys[3]: rank, keys[4]: nb_solves}

    @staticmethod
    def parse_rootme_user_solves_and_yield(data):
        validations = data["validations"]

        # This iterator yields ALL solves, not only new ones
        every_solve_iter = iter(validations)

        for solve in every_solve_iter:
            solve_id = int(solve["id_challenge"])
            yield solve_id

    def __repr__(self):
        return (
            f"User(id={self.idx}, username={self.username}, "
            f"score={self.score}, rank={self.rank}, solves={self.nb_solves})"
        )

    def __str__(self):
        return f"{self.username} #{self.idx}"

    def update_new_solves(self, raw_user_data):
        parsed_data = User.parse_rootme_user_data(raw_user_data)
        parsed_nb_solves = parsed_data["nb_solves"]

        self.nb_new_solves = parsed_nb_solves - self.nb_solves
        if self.nb_new_solves < 0:
            self.nb_new_solves = 0
            raise InvalidUserData(
                f"user {self.idx} as a negative number of new solves: "
                f"before update={self.nb_solves}; after={parsed_nb_solves}"
            )

    def yield_new_solves(self, raw_user_data):
        # FIXME: currently if it must yield several solves it yields the latest first so not in
        # chronological solve order that shouldn't be a problem with regular checking (rarely
        # someone flags twice in less than 1 minute)
        # but if the new solves checking is less frequent (few minutes) it can happen
        solves_id_iterator = User.parse_rootme_user_solves_and_yield(raw_user_data)

        # restrict to the first elements => latest solves => new solves
        for _ in range(self.nb_new_solves):
            try:
                yield next(solves_id_iterator)
            except StopIteration as exc:
                # TODO: this could be cool to log.error here but User class has no logger
                raise InvalidUserData("raw_user_data has less solves than nb_new_solves") from exc

        self.nb_solves += self.nb_new_solves
        self.nb_new_solves = 0

    def has_new_solves(self):
        return self.nb_new_solves != 0
