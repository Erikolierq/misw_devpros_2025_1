from .user import User
from .events import UserCreatedEvent

class UserAggregate:
    def __init__(self, username, password, role):
        self.user = User(username=username, password=password, role=role)

    @staticmethod
    def create(username, password, role):
        return UserAggregate(username, password, role)

    def to_dict(self):
        return {
            "id": self.user.id, 
            "username": self.user.username,
            "password": self.user.password,
            "role": self.user.role
        }

