import logging
import os
import string
import secrets 
from argon2.low_level import hash_secret_raw, Type
from argon2.exceptions import HashingError
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.exceptions import UnsupportedAlgorithm, InvalidTag
from cryptography.exceptions import AlreadyFinalized

from exceptions import PassError, EncryptErrno, DecryptErr

logger = logging.getLogger(__name__)

"""Módulo para la generación segura de contraseñas criptográficas."""

def gen():
    """Genera una contraseña aleatoria y segura de 64 caracteres."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for _ in range(64))

def derive_key(master_password: str, salt: bytes) -> bytes:
    try:
        return hash_secret_raw(
            secret=master_password.encode("utf-8"),
            salt=salt,
            time_cost=3,
            memory_cost=98304,
            parallelism=2,
            hash_len=32,
            type=Type.ID,
        )
    except HashingError as e:
        logger.warning("Derivación fallida. Revisar parámetros de Argon2.")
        raise PassError("Fallo en la derivación de la clave") from e
    except AlreadyFinalized as e:
        logger.warning("Derivación fallida, objeto ya finalizado.")
        raise PassError("Fallo en la derivación de la clave") from e 

def encrypt_passwd(key: bytes, data: bytes, aad: bytes = b"") -> tuple[bytes, bytes]:
    try:
        nonce = os.urandom(12)
        chacha = ChaCha20Poly1305(key)
        ct = chacha.encrypt(nonce, data, aad)
        return nonce, ct
    except UnsupportedAlgorithm as e:
        logger.error("Versión de OpenSSL obsoleta.")
        raise EncryptErrno("ChaCha20Poly1305 no soportado por OpenSSL.") from e

def decrypt(key: bytes, nonce: bytes, ct: bytes, aad: bytes = b"") -> str:
    try:
        chacha = ChaCha20Poly1305(key)
        pt = chacha.decrypt(nonce, ct, aad)
        return pt.decode("utf-8")
    except InvalidTag as e:
        logger.error("Falló la autenticación: datos alterados o clave/nonce incorrectos.")
        raise DecryptErr("Fallo de autenticación.") from e
