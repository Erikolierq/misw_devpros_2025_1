class User:
    def __init__(self, user_id, username, password, role):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.role = role

    def create_event(self):
        return {
            "type": "UserCreated",
            "version": 1,
            "data": {
                "user_id": self.user_id,
                "username": self.username,
                "role": self.role
            }
        }
