# ──────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────
import os  
import ctypes
import ctypes.util 
import logging
import mmap 
from contextlib import contextmanager 

#
MCL_CURRENT = 1
MCL_FUTURE = 2

# ──────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(
            filename="app.log",
            encoding="utf-8"
        )
    ]
)

logger = logging.getLogger(__name__)
# ──────────────────────────────────────────
# EXCEPCIONES
# ──────────────────────────────────────────
class BaseBufferError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


class LockMemory(Exception): 
    """Excepcion de bloqueo de memoria."""
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code 

class UnlockMemory(Exception):
    """Bloque de excepcion de manejo de error de desbloqueo Ram"""
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code 
# ──────────────────────────────────────────
# FUNCIONES
# ──────────────────────────────────────────

@contextmanager
def buffer(size: int):
    buf = None
    try:
        buf = mmap.mmap(
            -1,
            size,
            flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS,
            prot=mmap.PROT_READ | mmap.PROT_WRITE
        )
        if buf:
            print("mmap activado.")
        yield buf
    except OSError as e:
        raise BaseBufferError(f"Fallo en la asignación de memoria/hilos: {e}")
    finally:
        if buf is not None:
            buf.close()

#bloque de bloqueo ram
libc = ctypes.CDLL("libc.so.6", use_errno=True)
libc.mlockall.argtypes = [ctypes.c_int]
libc.mlockall.restype  = ctypes.c_int

def mlockall(flags: int = MCL_CURRENT | MCL_FUTURE) -> None:
    try:
        block = libc.mlockall(flags)
        if block != 0:
            error_c = ctypes.get_errno()   
            error_w = os.strerror(error_c) 
            logger.exception("Fallo en mlockall.")
            raise LockMemory(error_c, f"Falló el bloqueo de memoria. {os.strerror(error_c)}")
    except OSError:
        logger.exception("Fallo en mlockall.")
  
#bloque de desbloqueo de ram
libc.munlockall.restype  = ctypes.c_int 
libc.munlockall.argtypes = []

def munlockall() -> None:
    try:
        unblock = libc.munlockall()
        if unblock != 0:
            error_c = ctypes.get_errno()
            error_q = os.strerror(error_c)
            logger.exception("Fallo en munlockall")
            raise UnlockMemory(error_c, f"Error al desbloquear RAM: {os.strerror(error_c)}")
    except OSError as e:
        print(f"Error: {e}")

