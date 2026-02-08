"""Password hashing utilities using bcrypt directly."""
import bcrypt

# Bcrypt has a 72-byte limit for passwords
BCRYPT_MAX_LENGTH = 72


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    Truncates to 72 bytes to avoid bcrypt limit error.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string
    """
    password_bytes = password.encode('utf-8')[:BCRYPT_MAX_LENGTH]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to check against

    Returns:
        True if password matches, False otherwise
    """
    password_bytes = plain_password.encode('utf-8')[:BCRYPT_MAX_LENGTH]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)
