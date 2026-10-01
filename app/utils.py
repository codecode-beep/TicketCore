from pwdlib import PasswordHash

#Argon2 password-hashing algorithm
password_hash = PasswordHash.recommended()

def hash(password: str):
    """Hash a password for storing."""
    return password_hash.hash(password)

def verify(plain_password, hashed_password):
    """Verify a  plain_password provided by user against hashed from database"""
    return password_hash.verify(plain_password, hashed_password)