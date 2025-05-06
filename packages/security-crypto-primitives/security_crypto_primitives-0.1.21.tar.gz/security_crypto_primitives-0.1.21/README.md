# crypto\_utils


### Описание

`crypto_utils` — это простая и удобная Python-библиотека с обёртками над криптографическими алгоритмами на базе `cryptography`.

**Основные возможности:**

* **encrypt.py**: AES-GCM и ChaCha20-Poly1305 шифрование/дешифрование
* **sign.py**: RSA-PSS и ECDSA подпись и верификация
* **hash.py**: функции хеширования SHA-256, SHA-512, SHA3-256, SHA3-512
* **kdf.py**: PBKDF2-HMAC и scrypt для безопасного вывода ключей

### Установка

```bash
pip install crypto_utils
```

### Быстрый старт

#### Шифрование/дешифрование (AES-GCM)

```python
from crypto_utils.encrypt import encrypt_aes_gcm, decrypt_aes_gcm

key = b"\x00" * 32
nonce, ct = encrypt_aes_gcm(key, b"секретные данные", b"aad")
plaintext = decrypt_aes_gcm(key, nonce, ct, b"aad")
print(plaintext)  # b"секретные данные"
```

#### Подпись/верификация (RSA)

```python
from crypto_utils.sign import (
    generate_rsa_private_key, rsa_public_key_to_pem,
    sign_rsa, verify_rsa
)

priv = generate_rsa_private_key()
pub = priv.public_key()
sig = sign_rsa(priv, b"сообщение")
print(verify_rsa(pub, b"сообщение", sig))  # True
```

#### Хеширование (SHA3-256)

```python
from crypto_utils.hash import hash_sha3_256

digest = hash_sha3_256(b"данные для хеша")
print(digest.hex())
```

#### Производные функции ключей (PBKDF2)

```python
from crypto_utils.kdf import derive_pbkdf2

key, salt = derive_pbkdf2(b"пароль", iterations=200_000, length=64)
print(key.hex(), salt.hex())
```

### Тесты

```bash
pytest --maxfail=1 --disable-warnings -q
```


### Лицензия

MIT License

---


### Description

`crypto_utils` is a lightweight Python library wrapping cryptographic primitives (built on `cryptography`).

**Features:**

* **encrypt.py**: AES-GCM and ChaCha20-Poly1305 encryption/decryption
* **sign.py**: RSA-PSS and ECDSA signing & verification
* **hash.py**: SHA-256, SHA-512, SHA3-256, SHA3-512 hashing functions
* **kdf.py**: PBKDF2-HMAC and scrypt key derivation functions

### Installation

```bash
pip install crypto_utils
```

### Quick Start

#### Encryption/Decryption (AES-GCM)

```python
from crypto_utils.encrypt import encrypt_aes_gcm, decrypt_aes_gcm

key = b"\x00" * 32
nonce, ct = encrypt_aes_gcm(key, b"secret data", b"aad")
plaintext = decrypt_aes_gcm(key, nonce, ct, b"aad")
print(plaintext)  # b"secret data"
```

#### Signing/Verification (RSA)

```python
from crypto_utils.sign import (
    generate_rsa_private_key, rsa_public_key_to_pem,
    sign_rsa, verify_rsa
)

priv = generate_rsa_private_key()
pub = priv.public_key()
sig = sign_rsa(priv, b"message")
print(verify_rsa(pub, b"message", sig))  # True
```

#### Hashing (SHA3-256)

```python
from crypto_utils.hash import hash_sha3_256

digest = hash_sha3_256(b"data to hash")
print(digest.hex())
```

#### Key Derivation (PBKDF2)

```python
from crypto_utils.kdf import derive_pbkdf2

key, salt = derive_pbkdf2(b"password", iterations=200_000, length=64)
print(key.hex(), salt.hex())
```

### Running tests

```bash
pytest --maxfail=1 --disable-warnings -q
```



### License

MIT License
