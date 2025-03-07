from domain.user import User
from infrastructure.encryption_service import EncryptionService

class UserRepository:
    def __init__(self, session):
        self.session = session

    def get_all_users(self):
        users = self.session.query(User).all()
        return [user.to_dict() for user in users]

    def add(self, user):
        self.session.add(user)
        self.session.commit()

