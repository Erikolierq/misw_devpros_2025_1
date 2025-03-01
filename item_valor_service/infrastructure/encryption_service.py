from cryptography.fernet import Fernet
import base64
import os

class EncryptionService:
    def __init__(self, key=None):
        if key is None:
            key = base64.urlsafe_b64encode(os.urandom(32))  # Genera una clave aleatoria
        self.cipher = Fernet(key)

    def encrypt(self, data):
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data.encode()).decode()
