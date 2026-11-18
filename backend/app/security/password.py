
from pwdlib import PasswordHash

# Configure Argon2 password hashing
password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def get_password_hash(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    try:
        return password_hasher.verify(
            plain_password,
            hashed_password
        )
    except Exception:
        return False
