import pytest
from crypto_utils.sign import (
    generate_rsa_private_key,
    rsa_private_key_to_pem,
    load_rsa_private_key,
    rsa_public_key_to_pem,
    load_rsa_public_key,
    sign_rsa,
    verify_rsa,
    generate_ecdsa_private_key,
    ecdsa_private_key_to_pem,
    load_ecdsa_private_key,
    ecdsa_public_key_to_pem,
    load_ecdsa_public_key,
    sign_ecdsa,
    verify_ecdsa,
)


def test_rsa_sign_verify_roundtrip():
    priv = generate_rsa_private_key()
    priv_pem = rsa_private_key_to_pem(priv)
    pub = priv.public_key()
    pub_pem = rsa_public_key_to_pem(pub)

    loaded_priv = load_rsa_private_key(priv_pem)
    loaded_pub = load_rsa_public_key(pub_pem)

    msg = b"RSA test message"
    sig = sign_rsa(loaded_priv, msg)
    assert verify_rsa(loaded_pub, msg, sig)
    assert not verify_rsa(loaded_pub, msg + b"x", sig)


def test_ecdsa_sign_verify_roundtrip():
    priv = generate_ecdsa_private_key()
    priv_pem = ecdsa_private_key_to_pem(priv)
    pub = priv.public_key()
    pub_pem = ecdsa_public_key_to_pem(pub)

    loaded_priv = load_ecdsa_private_key(priv_pem)
    loaded_pub = load_ecdsa_public_key(pub_pem)

    msg = b"ECDSA test message"
    sig = sign_ecdsa(loaded_priv, msg)
    assert verify_ecdsa(loaded_pub, msg, sig)
    assert not verify_ecdsa(loaded_pub, msg + b"x", sig)
