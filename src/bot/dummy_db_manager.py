import logging

from classes.user import User
from classes.challenge import Challenge

class DummyDBManager:
    def __init__(self, api_manager):
        self.users = []
        self.api_manager = api_manager

        self.logger = logging.getLogger(__name__)

    async def add_user(self, idx):
        """Call the API Manager to get a user by his id then create a User object and store it"""

        # Check wether the user is already added
        if self.has_user(idx):
            return None

        raw_user_data = await self.api_manager.get_user_by_id(idx)

        user = User(raw_user_data)
        self.users.append(user)
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
            # TODO: add a specialized Exception
            raise Exception(f"User '{idx}' not in database")

        raw_user_data = await self.api_manager.get_user_by_id(idx)
        user.update_new_solves(raw_user_data)
        if not user.has_new_solves():
            self.logger.debug("'%s' hasn't any new solves", user)
            return

        self.logger.debug("'%s' has new solves: %s", user, user.nb_new_solves)
        for challenge_id in user.yield_new_solves(raw_user_data):
            challenge_data = await self.api_manager.get_challenge_by_id(challenge_id)
            challenge = Challenge(challenge_id, challenge_data)
            self.logger.info("%s solved: %s", user, challenge)
            yield repr(challenge)
