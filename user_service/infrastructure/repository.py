from domain.user import User
from infrastructure.encryption_service import EncryptionService

class UserRepository:
    def __init__(self, session):
        self.session = session

    def get_all_users(self):
        users = self.session.query(User).all()
        return [user.to_dict() for user in users]
    
    def get_by_username(self, username):
        return self.session.query(User).filter(User.username == username).first()

    def add(self, user):
        self.session.add(user)
        self.session.commit()
        
    def verify_password(self, username, password):
        user = self.get_by_username(username)
        if user:
            try:
                decrypted_password = self.encryption_service.decrypt(user.password)
                return decrypted_password == password
            except Exception:
                return False
        return False

