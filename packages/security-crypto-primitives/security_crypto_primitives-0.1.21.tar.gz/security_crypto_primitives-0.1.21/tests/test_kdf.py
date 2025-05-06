# tests/test_kdf.py
import pytest
from crypto_utils.kdf import derive_pbkdf2, derive_scrypt


def test_pbkdf2_consistency():
    pwd = b"password"
    key1, salt = derive_pbkdf2(pwd, salt=None)
    key2, _ = derive_pbkdf2(pwd, salt=salt)
    assert key1 == key2


def test_pbkdf2_length_and_salt():
    pwd = b"pass"
    key, salt = derive_pbkdf2(pwd, iterations=200_000, length=64)
    assert isinstance(key, bytes) and len(key) == 64
    assert isinstance(salt, bytes) and len(salt) == 16


def test_scrypt_consistency():
    pwd = b"secret"
    key1, salt = derive_scrypt(pwd)
    key2, _ = derive_scrypt(pwd, salt=salt)
    assert key1 == key2


def test_scrypt_params_and_length():
    pwd = b"abc"
    key, salt = derive_scrypt(pwd, n=2**12, r=8, p=2, length=24)
    assert isinstance(key, bytes) and len(key) == 24
    assert isinstance(salt, bytes) and len(salt) == 16
