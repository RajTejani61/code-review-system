from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash(password: str) -> str:
    return password_hash.hash(password)

def verify(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)