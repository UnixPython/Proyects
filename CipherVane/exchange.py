import logging
import getpass
import os
from cryptography.exceptions import InvalidKey
from cryptography.hazmat.bindings._rust.openssl import kdf
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

logger = logging.getLogger(__name__)

def encrypt(info: str, salt: bytes) -> bytes:
    try:
        salt = os.urandom(16)
        info = getpass.getpass("Input key:   ")
        utfs = info.encode("utf-8")
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=31,
            salt=salt,
            info=info.encode("utf-8")
        )
        derv = hkdf.derive(b"Input key:  ")
        return derv 
    except InvalidKey:
        print("""
        comprueba que la clave calculada no coincide con la
        clave esperada.""")


"""
def derive_hkdf(master_hkdf: str, salt: bytes) -> bytes:
    try:
        passd = getpass.getpass("input key")
        utf = passd.encode("utf-8")
        hkdf = HKDF (
            algorithm=hashes.SHA256(),
            lenght=32,
            salt=salt,
            info=info,
        )
        vert = hkdf.verify(b"key to verify:  ", key)
"""
