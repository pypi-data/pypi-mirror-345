# crypto_utils/encrypt.py
from typing import Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
import os


def encrypt_aes_gcm(
    key: bytes, plaintext: bytes, associated_data: bytes = b""
) -> Tuple[bytes, bytes]:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext, associated_data)
    return nonce, ct


def decrypt_aes_gcm(
    key: bytes, nonce: bytes, ct: bytes, associated_data: bytes = b""
) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, associated_data)


def encrypt_chacha20(
    key: bytes, plaintext: bytes, associated_data: bytes = b""
) -> Tuple[bytes, bytes]:
    """
    Шифрует plaintext алгоритмом ChaCha20-Poly1305.
    :param key: 32-байтный ключ.
    :param plaintext: данные для шифрования.
    :param associated_data: AAD.
    :return: (nonce, ciphertext_with_tag)
    """
    chacha = ChaCha20Poly1305(key)
    nonce = os.urandom(12)
    ct = chacha.encrypt(nonce, plaintext, associated_data)
    return nonce, ct


def decrypt_chacha20(
    key: bytes, nonce: bytes, ct: bytes, associated_data: bytes = b""
) -> bytes:
    """
    Расшифровывает ciphertext алгоритмом ChaCha20-Poly1305.
    """
    chacha = ChaCha20Poly1305(key)
    return chacha.decrypt(nonce, ct, associated_data)
