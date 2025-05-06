from typing import Optional, Tuple
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.exceptions import InvalidSignature

# ── RSA ─────────────────────────────────────────────────────────────────────────────


def generate_rsa_private_key(key_size: int = 2048) -> rsa.RSAPrivateKey:
    """
    Генерирует RSA-ключ.
    """
    return rsa.generate_private_key(public_exponent=65537, key_size=key_size)


def rsa_private_key_to_pem(
    private_key: rsa.RSAPrivateKey, password: Optional[bytes] = None
) -> bytes:
    """
    Сериализует RSA-приватный ключ в PEM (PKCS8).
    Если задан password, шифрует ключ.
    """
    encryption = (
        serialization.BestAvailableEncryption(password)
        if password
        else serialization.NoEncryption()
    )
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    )


def load_rsa_private_key(
    pem_data: bytes, password: Optional[bytes] = None
) -> rsa.RSAPrivateKey:
    """
    Загружает RSA-приватный ключ из PEM.
    """
    return serialization.load_pem_private_key(pem_data, password=password)


def rsa_public_key_to_pem(public_key: rsa.RSAPublicKey) -> bytes:
    """
    Сериализует RSA-публичный ключ в PEM.
    """
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def load_rsa_public_key(pem_data: bytes) -> rsa.RSAPublicKey:
    """
    Загружает RSA-публичный ключ из PEM.
    """
    return serialization.load_pem_public_key(pem_data)


def sign_rsa(private_key: rsa.RSAPrivateKey, message: bytes) -> bytes:
    """
    Подписывает message RSA-PSS+SHA256.
    """
    return private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )


def verify_rsa(public_key: rsa.RSAPublicKey, message: bytes, signature: bytes) -> bool:
    """
    Проверяет подпись. Возвращает True, если корректно, иначе False.
    """
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False


# ── ECDSA ────────────────────────────────────────────────────────────────────────────


def generate_ecdsa_private_key(
    curve: ec.EllipticCurve = ec.SECP256R1(),
) -> ec.EllipticCurvePrivateKey:
    """
    Генерирует ECDSA-ключ на заданной кривой.
    """
    return ec.generate_private_key(curve)


def ecdsa_private_key_to_pem(
    private_key: ec.EllipticCurvePrivateKey, password: Optional[bytes] = None
) -> bytes:
    """
    Сериализует ECDSA-приватный ключ в PEM (PKCS8).
    """
    encryption = (
        serialization.BestAvailableEncryption(password)
        if password
        else serialization.NoEncryption()
    )
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    )


def load_ecdsa_private_key(
    pem_data: bytes, password: Optional[bytes] = None
) -> ec.EllipticCurvePrivateKey:
    """
    Загружает ECDSA-ключ из PEM.
    """
    return serialization.load_pem_private_key(pem_data, password=password)


def ecdsa_public_key_to_pem(public_key: ec.EllipticCurvePublicKey) -> bytes:
    """
    Сериализует ECDSA-публичный ключ в PEM.
    """
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def load_ecdsa_public_key(pem_data: bytes) -> ec.EllipticCurvePublicKey:
    """
    Загружает ECDSA-публичный ключ из PEM.
    """
    return serialization.load_pem_public_key(pem_data)


def sign_ecdsa(private_key: ec.EllipticCurvePrivateKey, message: bytes) -> bytes:
    """
    Подписывает message ECDSA+SHA256.
    """
    return private_key.sign(message, ec.ECDSA(hashes.SHA256()))


def verify_ecdsa(
    public_key: ec.EllipticCurvePublicKey, message: bytes, signature: bytes
) -> bool:
    """
    Проверяет ECDSA-подпись.
    """
    try:
        public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False
