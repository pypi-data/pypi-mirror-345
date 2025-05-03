
from neutrino.secret import SecretManager

secret_manager = SecretManager()
encrypted_input = secret_manager.encrypt("my secret")
decrypted_input = secret_manager.decrypt(encrypted_input)
print(f"Encrypted input: {encrypted_input}")
print(f"Decrypted input: {decrypted_input}")