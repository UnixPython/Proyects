import ctypes
import logging
import pysodium
import signal
import time
from exceptions import BufferSizeError,  AllocationError, UseAfterFreeError
logger = logging.getLogger(__name__)
sodium = pysodium.sodium

sodium.sodium_init.restype = ctypes.c_int
sodium.sodium_init.argtypes = []
sodium.sodium_init()

sodium.sodium_malloc.restype = ctypes.c_void_p
sodium.sodium_malloc.argtypes = [ctypes.c_size_t]

sodium.sodium_mlock.restype = ctypes.c_int
sodium.sodium_mlock.argtypes = [ctypes.c_void_p, ctypes.c_size_t]

sodium.sodium_munlock.restype = ctypes.c_int
sodium.sodium_munlock.argtypes = [ctypes.c_void_p, ctypes.c_size_t]

sodium.sodium_free.restype = None
sodium.sodium_free.argtypes = [ctypes.c_void_p]


class memory:
    def __init__(self, size):
        if not isinstance(size, int) or size <= 0:
            raise AllocationError("Tamaño inválido: no se puede reservar 0 bytes.")
        ptr = sodium.sodium_malloc(size)
        if ptr is None:
            logger.critical("[!] sodium_malloc devolvió NULL, sin memoria disponible.")
            raise AllocationError("Malloc devolvió NULL: no hay memoria asignada.")
        self.size = size
        self.ptr = ptr
        self._freed = False
        self._locked = False

    def lock(self):
        if self._freed:
            raise UseAfterFreeError("No se puede bloquear un buffer ya liberado")
        ret = sodium.sodium_mlock(self.ptr, self.size)
        if ret != 0:
            logger.warning(
                "No se pudo bloquear memoria (mlock). El sistema puede no soportarlo "
                "(contenedor sin CAP_IPC_LOCK, límite de RLIMIT_MEMLOCK, etc.). "
                "Continuando sin bloqueo — la clave podría paginarse a swap."
            )
            self._locked = False
            return
        self._locked = True
        logger.info("Se bloqueó el buffer")

    def write(self, data):
        if self._freed:
            raise UseAfterFreeError("No se puede escribir en un buffer ya liberado")
        if len(data) > self.size:
            raise BufferSizeError("Los datos exceden el tamaño reservado del buffer")
        buf = (ctypes.c_char * len(data)).from_buffer_copy(bytes(data))
        ctypes.memmove(self.ptr, buf, len(data))

    def read(self):
        if self._freed:
            raise UseAfterFreeError("Buffer ya liberado: use-after-free")
        mem = ctypes.string_at(self.ptr, self.size)
        if len(mem) != self.size:
            logger.error("Tamaño no es válido para el buffer")
            raise BufferSizeError("Buffer generado no es válido")
        return mem

    def close(self):
        if self._freed:
            raise UseAfterFreeError("El buffer ya fue liberado (double free)")
        if getattr(self, "_locked", False):
            sodium.sodium_munlock(self.ptr, self.size)
        sodium.sodium_free(self.ptr)
        self._freed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True

if __name__ == '__main__':
    killer = GracefulKiller()
    while not killer.kill_now:
        time.sleep(1)
        print("Proceso cancelado y limpiado.")
