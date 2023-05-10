class DummyUser:
    def __init__(self, id):
        self.id = id
        self.points = 0
        self.name = "dummy_user_"+str(id)
        self.solves = ["super dur challenge", "challenge moyen", "HTML - boutons désactivés"]

class DummyAPIManager:
    def __init__(self):
        pass
    def get_rootme_user(self, id):
        return DummyUser(id)

class DummyDBManager:
    def __init__(self, api_manager):
        self.users = []
        self.api_manager = api_manager
    
    def add_user(self, id):
        user = self.api_manager.get_rootme_user(id)
        self.users.append(user)
        return user

    def get_user(self, id):
        """Retrieve the user object whose id matches 'id', None if not found"""
        return next(filter(lambda user: user.id == id, self.users), None)
    
    def get_users(self):
        return self.users
