# tests/test_encrypt.py
import pytest
from crypto_utils.encrypt import (
    encrypt_aes_gcm,
    decrypt_aes_gcm,
    encrypt_chacha20,
    decrypt_chacha20,
)


def test_aes_gcm_roundtrip():
    key = b"\x00" * 32
    nonce, ct = encrypt_aes_gcm(key, b"hello", b"hdr")
    assert decrypt_aes_gcm(key, nonce, ct, b"hdr") == b"hello"


def test_chacha20_roundtrip():
    key = b"\x01" * 32
    nonce, ct = encrypt_chacha20(key, b"world", b"meta")
    assert decrypt_chacha20(key, nonce, ct, b"meta") == b"world"


# Опционально: проверим, что при подмене tag или AAD пойдёт исключение
@pytest.mark.parametrize("bad_aad", [b"x", b"", None])
def test_chacha20_bad_aad(bad_aad):
    key = b"\x02" * 32
    nonce, ct = encrypt_chacha20(key, b"data", b"auth")
    with pytest.raises(Exception):
        # Передаём неверный AAD
        decrypt_chacha20(key, nonce, ct, bad_aad or b"")
