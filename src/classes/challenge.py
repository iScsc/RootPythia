# pylint: disable=too-few-public-methods
class Challenge():
    """Class for the Challenge object"""
    def __init__(self, challenge_id: int, data: dict):
        """
            idx: int,
            author_id: int,
            title: str,
            category:str,
            description: str,
            pts: int,
            difficulty: str
        """
        self.idx = challenge_id

        parsed_data = parse_rootme_challenge_data(data)
        (self.author_id, self.title, self.category, self.description, self.pts, self.difficulty) = parsed_data

    @classmethod
    def parse_rootme_challenge_data(data):
        """A static method that returns a tuple of few challenge data extracted from raw RootMe API data"""

        # multitline extraction so that in case of error (API change for exemple) the error clearly show the wrong line
        data = data[0]
        authors = data["auteurs"]
        main_author = authors["0"]
        author_id = int(main_author["id_auteur"])

        title = data["titre"]
        category = data["rubrique"]
        description = data["soustitre"]
        pts = int(data["score"])
        difficulty = data["difficulte"]

        return (author_id, title, category, description, pts, difficulty)
