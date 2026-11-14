import logging
import getpass
import os
from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

logger = logging.getLogger(__name__)

def verify(salt: bytes) -> bytes:
    try:
        salt = os.urandom(16)
        info = getpass.getpass("Input key:   ")
        utfs = info.encode("utf-8")
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=utfs,
        )
        derv = hkdf.derive(utfs)
        hkdf.verify(utfs, derv)
        return derv
    except InvalidKey:
        print("""
        comprueba que la clave calculada no coincide con la
        clave esperada.""")
        raise
