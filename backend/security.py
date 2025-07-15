import os
from cryptography.fernet import Fernet
from passlib.context import CryptContext

# Encryption
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
fernet = Fernet(ENCRYPTION_KEY)

def encrypt(data: str) -> str:
    """Encrypts a string."""
    return fernet.encrypt(data.encode()).decode()

def decrypt(encrypted_data: str) -> str:
    """Decrypts an encrypted string."""
    return fernet.decrypt(encrypted_data.encode()).decode()


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)
