import os
import logging
from argon2.low_level import hash_secret_raw, Type
from argon2.exceptions import HashingError
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.exceptions import UnsupportedAlgorithm, InvalidTag
from exceptions import DecryptErr, PassError, EncryptErrno

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("cryps.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def derive_key(master_password: str, salt: bytes) -> bytes:
    try:
        key = hash_secret_raw(
            secret=master_password.encode("utf-8"),
            salt=salt,
            time_cost=3,
            memory_cost=98304,
            parallelism=2,
            hash_len=32,
            type=Type.ID
        )
        return key
    except HashingError as e:
        logger.warning("Derivación fallada. Revisar argon2")
        raise PassError("Fallo en la derivación de la clave") from e


def encrypt_passwd(key: bytes, data: bytes, aad: bytes = b"") -> tuple:
    """funcion que encripta"""
    try:
        nonce = os.urandom(12)
        chacha = ChaCha20Poly1305(key)
        ct = chacha.encrypt(nonce, data, aad)
        return nonce, ct
    except UnsupportedAlgorithm as e:
        logger.warning("Version de OpenSSL obsoleto se requiere actualizar.")
        raise EncryptErrno(
            "ChaCha20Poly1305 no soportado por esta versión de OpenSSL."
        ) from e


def decrypt(key: bytes, nonce: bytes, ct: bytes, aad: bytes = b"") -> str:
    try:
        chacha = ChaCha20Poly1305(key)
        pt = chacha.decrypt(nonce, ct, aad)
        return pt.decode("utf-8")
    except InvalidTag as e:
        logger.error("Falló la autenticación por falla de usuario.")
        raise DecryptErr(
            "Fallo de autenticación: datos alterados o clave/nonce incorrectos."
        ) from e
