# core/security.py
# Handles password hashing and verification
from passlib.context import CryptContext

# bcrypt is the industry standard for password hashing
pwd_context = CryptContext (schemes=["bcrypt"],deprecated = "auto")

def hash_password (password: str) -> str:
    """
    Converts plain text password to bcrypt hash.
    One-way function - cannot be reversed.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Returns True if plain password matches the hash.
    Used during login to verify credentials.
    """
    return pwd_context.verify(plain_password, hashed_password)   