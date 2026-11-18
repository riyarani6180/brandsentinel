
from pwdlib import PasswordHash


# Configure Argon2 password hashing
password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a secure hash.
    """

    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verify a password against its stored hash.
    """

    return password_hasher.verify(
        plain_password,
        hashed_password
    )
