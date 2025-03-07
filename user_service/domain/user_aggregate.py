from .user import User
from .events import UserCreatedEvent
from infrastructure.encryption_service import EncryptionService

class UserAggregate:
    def __init__(self, username, password, role):
        encryption_service = EncryptionService()
        encrypted_password = encryption_service.encrypt(password)  # Encriptar la contraseña
        self.user = User(username=username, password=encrypted_password, role=role)

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

