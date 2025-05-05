from typing import Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import os


def derive_pbkdf2(
    password: bytes,
    salt: Optional[bytes] = None,
    iterations: int = 100_000,
    length: int = 32,
    algorithm=hashes.SHA256(),
) -> tuple[bytes, bytes]:
    """
    Производит PBKDF2-HMAC на основе SHA-256.

    :param password: пароль в байтах
    :param salt: 16-байтный соль. Если None, генерируется случайно.
    :param iterations: число итераций (рекомендуется >=100_000)
    :param length: длина выводимого ключа в байтах
    :param algorithm: алгоритм хеша (по умолчанию SHA256)
    :return: кортеж (derived_key, salt)
    """
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=algorithm,
        length=length,
        salt=salt,
        iterations=iterations,
    )
    key = kdf.derive(password)
    return key, salt


def derive_scrypt(
    password: bytes,
    salt: Optional[bytes] = None,
    length: int = 32,
    n: int = 2**14,
    r: int = 8,
    p: int = 1,
) -> tuple[bytes, bytes]:
    """
    Производит scrypt KDF.

    :param password: пароль в байтах
    :param salt: 16-байтный соль. Если None, генерируется случайно.
    :param length: длина выводимого ключа в байтах
    :param n: CPU/memory cost
    :param r: block size
    :param p: parallelization
    :return: кортеж (derived_key, salt)
    """
    if salt is None:
        salt = os.urandom(16)
    kdf = Scrypt(
        salt=salt,
        length=length,
        n=n,
        r=r,
        p=p,
    )
    key = kdf.derive(password)
    return key, salt
