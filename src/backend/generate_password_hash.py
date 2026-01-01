#!/usr/bin/env python3
"""Generate password hash for seed data."""
from app.core.security import get_password_hash

if __name__ == "__main__":
    password = "password123"
    hashed = get_password_hash(password)
    print(f"\nPassword: {password}")
    print(f"Hash: {hashed}")
    print("\nCopy this hash to init_db.py")
