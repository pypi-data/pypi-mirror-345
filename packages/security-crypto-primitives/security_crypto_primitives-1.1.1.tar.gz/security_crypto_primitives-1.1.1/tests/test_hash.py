# tests/test_hash.py
import pytest
from crypto_utils.hash import hash_sha256, hash_sha512, hash_sha3_256, hash_sha3_512


def test_sha256_empty():
    assert hash_sha256(b"").hex() == (
        "e3b0c44298fc1c149afbf4c8996fb924" "27ae41e4649b934ca495991b7852b855"
    )


def test_sha512_empty():
    assert hash_sha512(b"").hex() == (
        "cf83e1357eefb8bdf1542850d66d8007"
        "d620e4050b5715dc83f4a921d36ce9ce"
        "47d0d13c5d85f2b0ff8318d2877eec2f"
        "63b931bd47417a81a538327af927da3e"
    )


def test_sha3_256_empty():
    assert hash_sha3_256(b"").hex() == (
        "a7ffc6f8bf1ed76651c14756a061d662" "f580ff4de43b49fa82d80a4b80f8434a"
    )


def test_sha3_512_empty():
    assert hash_sha3_512(b"").hex() == (
        "a69f73cca23a9ac5c8b567dc185a756e"
        "97c982164fe25859e0d1dcc1475c80a6"
        "15b2123af1f5f94c11e3e9402c3ac558"
        "f500199d95b6d3e301758586281dcd26"
    )
