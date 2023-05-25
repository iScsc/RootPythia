from classes.user import User

class DummyDBManager:
    def __init__(self, api_manager):
        self.users = []
        self.api_manager = api_manager
    
    async def add_user(self, id):
        """Call the API Manager to get a user by his id then create a User object and store it"""

        raw_user_data = await self.api_manager.get_user_by_id(id)

        user = User(raw_user_data)
        self.users.append(user)
        return user

    def get_user(self, id):
        """Retrieve the user object whose id matches 'id', None if not found"""
        return next(filter(lambda user: user.id == id, self.users), None)
    
    def get_users(self):
        return self.users
