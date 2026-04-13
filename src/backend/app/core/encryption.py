"""Encryption mapping and utility for sensitive data."""

from cryptography.fernet import Fernet
from app.config import settings

# Initialize cipher suite with application setting encryption key
# The key must be 32 url-safe base64-encoded bytes.
_cipher_suite = Fernet(settings.encryption_key.encode("utf-8") if isinstance(settings.encryption_key, str) else settings.encryption_key)

def encrypt_password(plain_text: str) -> bytes:
    """
    Symmetrically encrypt a plaintext password into bytes.
    
    Args:
        plain_text: The plaintext string to encrypt.
        
    Returns:
        Encrypted byte string.
    """
    # ensure it's a string, then encode it to bytes, then encrypt
    return _cipher_suite.encrypt(plain_text.encode("utf-8"))

def decrypt_password(encrypted_bytes: bytes) -> str:
    """
    Symmetrically decrypt encrypted password bytes back to plaintext.
    
    Args:
        encrypted_bytes: The encrypted byte string.
        
    Returns:
        The decrypted plaintext string.
    """
    # decrypt returns bytes, which we decode back to string
    return _cipher_suite.decrypt(encrypted_bytes).decode("utf-8")
