from cryptography.fernet import Fernet
import base64
import os

class EncryptionService:
    def __init__(self):
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            raise ValueError("Falta la clave de encriptación en las variables de entorno")
        self.cipher = Fernet(key.encode())


    def encrypt(self, data):
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data.encode()).decode()
