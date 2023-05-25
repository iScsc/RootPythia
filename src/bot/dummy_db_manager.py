from classes.user import User

class DummyDBManager:
    def __init__(self, api_manager):
        self.users = []
        self.api_manager = api_manager
    
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
