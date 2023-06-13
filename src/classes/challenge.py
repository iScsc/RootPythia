class Challenge:
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

        parsed_data = Challenge.parse_rootme_challenge_data(data)
        (
            self.author_id,
            self.title,
            self.category,
            self.description,
            self.pts,
            self.difficulty,
        ) = parsed_data

    @staticmethod
    def parse_rootme_challenge_data(data):
        """A static method that returns a tuple of few challenge data extracted from raw RootMe API data"""

        # multitline extraction so that in case of error (API change for exemple) the error clearly show the wrong line
        data = data[0]
        authors = data["auteurs"]
        main_author = authors["0"]
        author_id = int(main_author["id_auteur"])

        title = data["titre"]
        # parse the challenge category to ASCII character and better usability
        category = (
            data["rubrique"].lower().replace(" ", "").replace("\u00E9", "e").replace("\u00E8", "e")
        )
        description = data["soustitre"]
        pts = int(data["score"])
        difficulty = data["difficulte"]

        return (author_id, title, category, description, pts, difficulty)

    def __repr__(self):
        return f"Challenge(id={self.idx}, author ID={self.author_id}, title={self.title}, category={self.category}, description={self.description}, points={self.pts}, difficulty={self.difficulty})"

    def __str__(self):
        return f"{self.title} - {self.category} - {self.pts}"
