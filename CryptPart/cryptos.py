import logging
import hashlib
import hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from exceptions import base

logger = logging.getLogger(__name__)

SECTOR = 4096
KEY_SIZE = 64

@base 
def _tweak(n: int) -> bytes: #convierte valor int a bytes
    return n.to_bytes(16, "little")

@base
def encrypt(key: bytes, n: int, dates: bytes) -> bytes:
    """Encripta la particion"""
    logger.info("Se midieron los bytes.")
    if len(key) != KEY_SIZE:
        raise ValueError(f"La key debe medir: {KEY_SIZE} bytes")
    if len(dates) != SECTOR:
        raise ValueError(f"El sector debe medir: {SECTOR} bytes")

    if not 0 <= n < 2**128:
        raise ValueError("n fuera de rango (0 a 2^128-1)")

    enc = Cipher(algorithms.AES(bytes(key)), modes.XTS(_tweak(n))).encryptor()
    return enc.update(dates) + enc.finalize()

@base 
def decrypt(key: bytes, n: int, dates: bytes) -> bytes:
    """desencripta la particion."""
    if len(key) != KEY_SIZE:
        raise ValueError(f"La key debe medir: {KEY_SIZE} bytes")
    if len(dates) != SECTOR:
        raise ValueError(f"El sector debe medir: {SECTOR} bytes")
    if not 0 <= n < 2**128:
        raise ValueError("n fuera de rango (0 a 2^128-1)")
    dec = Cipher(algorithms.AES(bytes(key)), modes.XTS(_tweak(n))).decryptor()
    return dec.update(dates) + dec.finalize()

@base 
def hasher256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

@base 
def compares_hmac(key_hmac: bytes, data: bytes, expected_mac: bytes) -> bool:
    calculated_mac = hmac.new(key_hmac, data, hashlib.sha256).digest()
    return hmac.compare_digest(calculated_mac, expected_mac)
