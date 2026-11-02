import logging
import secrets
import os 
import struct  
from exceptions import HeaderInvalid, InvalidPassword
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.keywrap import (
        aes_key_wrap,
        aes_key_unwrap,
        InvalidUnwrap
)

logger = logging.getLogger(__name__)

MAGIC = b"CRYPTPRT"
VERSION = 1
KEY_SIZE = 64
SECTORR_HDD = 512 #solo para discos HDD
HEADER_FMT = "!8s I 16s I I I 72s"
HEADER_SIZE = struct.calcsize(HEADER_FMT)   # bytes reales del header
HEADER_AREA = 4096                          # espacio reservado antes de los datos
assert len(MAGIC) == 8
assert HEADER_SIZE <= HEADER_AREA and HEADER_AREA % SECTORR_HDD == 0

ARGON_T = 3
ARGON_M_KIB = 64 * 1024
ARGON_P = min(4, os.cpu_count() or 1)

def _derivar_kek(password: bytes, salt: bytes, t: int, m: int, p: int) -> bytes:
    return Argon2id(
        salt=salt, length=32, iterations=t, lanes=p, memory_cost=m).derive(password)

def pack_header(salt, t, m, p, wrapped) -> bytes:
    raw = struct.pack(HEADER_FMT, MAGIC, VERSION, salt, t, m, p, wrapped)
    return raw.ljust(HEADER_AREA, b"\x00")

def unpack_header(raw: bytes):
    if len(raw) < HEADER_SIZE:
        logger.error("Header fue incompleto.")
        raise HeaderInvalid("Header incompleto.")
    
    magic, ver, salt, t, m, p, wrapped = struct.unpack(
        HEADER_FMT, raw [:HEADER_SIZE]
    )
    if magic != MAGIC:
        logger.error("Magic falló se requiere revisar.")
        raise HeaderInvalid("Magic invalido.")

    if ver != VERSION:
        raise HeaderInvalid(f"Version no soportada: {ver}")
    return salt, t, m, p, wrapped


def crear_volumen(password: bytes, t=ARGON_T, m=ARGON_M_KIB, p=ARGON_P):
    """Devuelve (master_key, header_raw). Guarda header_raw al inicio del .enc."""
    master  = bytearray(secrets.token_bytes(KEY_SIZE))      
    salt    = secrets.token_bytes(16)                       
    kek     = _derivar_kek(password, salt, t, m, p)                                                
    wrapped = aes_key_wrap(kek, bytes(master))              
    return master, pack_header(salt, t, m, p, wrapped)      

def abrir_volumen(password: bytes, header_raw: bytes) -> bytearray:
    """Devuelve la master_key si la contraseña es correcta."""
    salt, t, m, p, wrapped = unpack_header(header_raw)
    kek = _derivar_kek(password, salt, t, m, p)

    try:
        return bytearray(aes_key_unwrap(kek, wrapped))  # 3. desenvolver
    except InvalidUnwrap as e:
        print("Contraseña incorrecta o header corrupto")
        raise InvalidPassword("Contraseña invalida") from e

