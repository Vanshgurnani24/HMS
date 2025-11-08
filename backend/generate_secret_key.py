#!/usr/bin/env python3
"""
Generate a secure secret key for JWT token generation.
Run this script and copy the output to your .env file.
"""

import secrets

def generate_secret_key():
    """Generate a cryptographically secure secret key."""
    return secrets.token_hex(32)

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print("=" * 70)
    print("SECURE SECRET KEY GENERATED")
    print("=" * 70)
    print(f"\nYour secret key:\n{secret_key}\n")
    print("Copy this to your .env file:")
    print(f"SECRET_KEY={secret_key}")
    print("\n" + "=" * 70)
    print("IMPORTANT: Keep this key secret and never commit it to version control!")
    print("=" * 70)