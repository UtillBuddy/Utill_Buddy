import os
from cryptography.fernet import Fernet

# Load the encryption key from the environment variables
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
fernet = Fernet(ENCRYPTION_KEY)

def encrypt(data: str) -> str:
    """Encrypts a string."""
    return fernet.encrypt(data.encode()).decode()

def decrypt(encrypted_data: str) -> str:
    """Decrypts an encrypted string."""
    return fernet.decrypt(encrypted_data.encode()).decode()
