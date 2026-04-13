"""Unit tests for encryption core utility."""

import pytest
from cryptography.fernet import InvalidToken

from app.core.encryption import encrypt_password, decrypt_password


def test_encryption_decryption_loop():
    """Test that a password can be encrypted and then decrypted to the same string."""
    original_password = "SuperSecretPassword123!"
    
    encrypted = encrypt_password(original_password)
    
    # Should not be the same as original
    assert encrypted != original_password.encode("utf-8")
    assert isinstance(encrypted, bytes)
    
    decrypted = decrypt_password(encrypted)
    
    # Should match original
    assert decrypted == original_password
    assert isinstance(decrypted, str)


def test_different_passwords_produce_different_ciphertexts():
    """Test that different passwords yield different ciphertexts."""
    pwd1 = "PasswordOne"
    pwd2 = "PasswordTwo"
    
    enc1 = encrypt_password(pwd1)
    enc2 = encrypt_password(pwd2)
    
    assert enc1 != enc2


def test_decrypting_invalid_ciphertext_raises_error():
    """Test that decrypting invalid or tampered ciphertext raises InvalidToken."""
    invalid_bytes = b"not-a-valid-fernet-token"
    
    with pytest.raises(InvalidToken):
        decrypt_password(invalid_bytes)


def test_decrypting_tampered_ciphertext_raises_error():
    """Test that modifying a byte of valid ciphertext invalidates it."""
    encrypted = bytearray(encrypt_password("MyPassword"))
    # Flip one byte in the ciphertext (excluding the Fernet header which might cause different errors)
    encrypted[-1] ^= 0x01 
    
    with pytest.raises(InvalidToken):
        decrypt_password(bytes(encrypted))
