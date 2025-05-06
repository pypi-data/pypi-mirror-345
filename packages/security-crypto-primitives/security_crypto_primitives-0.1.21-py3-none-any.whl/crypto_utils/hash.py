from cryptography.hazmat.primitives import hashes


def hash_sha256(data: bytes) -> bytes:
    """
    Возвращает SHA-256 хеш данных.
    :param data: байты для хеширования
    :return: байтовый результат (32 байта)
    """
    digest = hashes.Hash(hashes.SHA256())
    digest.update(data)
    return digest.finalize()


def hash_sha512(data: bytes) -> bytes:
    """
    Возвращает SHA-512 хеш данных.
    :param data: байты для хеширования
    :return: байтовый результат (64 байта)
    """
    digest = hashes.Hash(hashes.SHA512())
    digest.update(data)
    return digest.finalize()


def hash_sha3_256(data: bytes) -> bytes:
    """
    Возвращает SHA3-256 хеш данных.
    :param data: байты для хеширования
    :return: байтовый результат (32 байта)
    """
    digest = hashes.Hash(hashes.SHA3_256())
    digest.update(data)
    return digest.finalize()


def hash_sha3_512(data: bytes) -> bytes:
    """
    Возвращает SHA3-512 хеш данных.
    :param data: байты для хеширования
    :return: байтовый результат (64 байта)
    """
    digest = hashes.Hash(hashes.SHA3_512())
    digest.update(data)
    return digest.finalize()
