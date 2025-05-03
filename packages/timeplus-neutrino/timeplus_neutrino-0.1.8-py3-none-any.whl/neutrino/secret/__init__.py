import os
from cryptography.fernet import Fernet

# Define paths
HOME_DIR = os.path.expanduser("~")
SECURE_DIR = os.path.join(HOME_DIR, ".timeplus")
KEY_FILE = os.path.join(SECURE_DIR, "encryption_key.key")


class SecretManager:
    def __init__(self):
        os.makedirs(SECURE_DIR, exist_ok=True)
        self.key = self._get_or_create_key()

    def _get_or_create_key(self) -> bytes:
        if not os.path.exists(KEY_FILE):
            encryption_key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as key_file:
                key_file.write(encryption_key)
            print("New encryption key generated and saved.")
        else:
            with open(KEY_FILE, "rb") as key_file:
                encryption_key = key_file.read()
        return encryption_key

    def encrypt(self, input: str) -> bytes:
        cipher = Fernet(self.key)
        encrypted_input = cipher.encrypt(input.encode())
        return encrypted_input

    def decrypt(self, input: bytes) -> str:
        cipher = Fernet(self.key)
        decrypted_input = cipher.decrypt(input).decode()
        return decrypted_input
