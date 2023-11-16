import logging

from api.rootme_api import RootMeAPIError, RootMeAPIManager
from classes import User
from classes import Challenge


class InvalidUser(Exception):
    def __init__(self, idx=None, message=None):
        self.idx = idx

        if message is None:
            self.message = "Invalid User"
            if self.idx is not None:
                self.message += f": {self.idx}"
        else:
            self.message = (message % self.idx) if "%s" in message else message

        super().__init__(self.message)


class DummyDBManager:
    def __init__(self, api_manager: RootMeAPIManager):
        self.users = []
        self.api_manager = api_manager

        self.logger = logging.getLogger(__name__)

    async def add_user(self, idx):
        """Call the API Manager to get a user by his id then create a User object and store it"""

        # Check wether the user is already added
        if self.has_user(idx):
            return None

        try:
            raw_user_data = await self.api_manager.get_user_by_id(idx)
        except RootMeAPIError:
            return None

        user = User(raw_user_data)
        self.users.append(user)
        self.logger.debug("add user '%s'", repr(user))
        return user

    def has_user(self, idx):
        return self.get_user(idx) is not None

    def get_user(self, idx):
        """Retrieve the user object whose id matches 'id', None if not found"""
        return next(filter(lambda user: user.idx == idx, self.users), None)

    def get_users(self):
        return self.users

    async def fetch_user_new_solves(self, idx):
        user = self.get_user(idx)
        if user is None:
            raise InvalidUser(idx, "DummyDBManager.fetch_user_new_solves: User %s not in database")

        try:
            raw_user_data = await self.api_manager.get_user_by_id(idx)
        except RootMeAPIError:
            # If for some reason we can get the user on this iteration
            # we will get him next time maybe ...
            self.logger.error("User %s could not be fetch from the API, yet we keep running", idx)
            return
            
        user.update_new_solves(raw_user_data)
        if not user.has_new_solves():
            self.logger.debug("'%s' hasn't any new solves", user)
            return

        self.logger.info("'%s' has %s new solves", user, user.nb_new_solves)
        for challenge_id in user.yield_new_solves(raw_user_data):
            try:
                challenge_data = await self.api_manager.get_challenge_by_id(challenge_id)
            except RootMeAPIError:
                # If we can't fetch the challenge, sadly there is not much we can do
                continue
            challenge = Challenge(challenge_id, challenge_data)
            self.logger.debug("'%s' solved '%s'", repr(user), repr(challenge))
            yield challenge
