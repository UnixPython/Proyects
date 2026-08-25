import logging
import inspect
import linecache

# Base

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("errnos.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class BaseErrno(Exception):
    """Excepción base que captura automáticamente dónde y por qué se originó el error."""

    def __init__(self, message: str, info: bool = False, code=None):
        super().__init__(message)
        self.info = info
        self.code = code
        self.line = "<unavailable source>"
        self.file_name = "<unknown file>"
        self.func_name = "<unknown func>"
        self.source_line = self.line
        self._capturar_contexto()

    def _capturar_contexto(self) -> None:
        """Sube por el stack hasta salir de este archivo, para no capturar
        los __init__ intermedios de las subclases."""
        frame = inspect.currentframe()
        if frame is None:
            return

        try:
            this_file = __file__
            while frame is not None and frame.f_code.co_filename == this_file:
                frame = frame.f_back

            if frame is not None:
                code_obj = frame.f_code
                self.line = frame.f_lineno
                self.file_name = code_obj.co_filename
                self.func_name = code_obj.co_name
                source = linecache.getline(self.file_name, self.line).strip()
                self.source_line = source if source else "<unavailable source>"
        finally:
            del frame


class SecureMemoryError(BaseErrno):
    """Excepción base para errores de memoria segura. Reutiliza la captura
    de contexto de CryptoBaseError."""


# -------------------------------------------

# Criptografia

class InvalidCrypt(BaseErrno):
    """Manejo de error de invalidación de criptografía."""
    def __init__(self, message, code=None):
        super().__init__(message, code=code)


class DecryptErr(BaseErrno):
    """Excepción de autenticación."""


class PassError(BaseErrno):
    """Error de pass de criptografía."""
    def __init__(self, msg: str, info: bool = False):
        super().__init__(msg, info=info)


class EncryptErrno(BaseErrno):
    """Error de encriptado."""
    def __init__(self, msg: str, info: bool = False):
        super().__init__(msg, info=info)

class InvalidValue(BaseErrno):
    """Error de invalidacion."""
    def __init__(self, msg: str, info: bool = False):
        super().__init__(msg, info=info)

# ------------------------------------

# Memoria

class AllocationError(BaseErrno):
    """sodium_malloc devolvió NULL: no hay memoria asignada en absoluto."""

class LockError(BaseErrno):
    """sodium_mlock o sodium_munlock devolvieron un código de error."""

class MemCeroErr(BaseErrno):
    """Fallo de memoria a zero."""

class UseAfterFreeError(BaseErrno):
    """Se intentó operar sobre un buffer ya liberado con close()."""

class BufferSizeError(BaseErrno):
    """Un tamaño solicitado o escrito no es válido para el buffer."""

class memmoveErr(BaseErrno):
    """Error de memmove si falla o falta un puntero de memoria."""

#-------------------------------------

class InvalidDecode(BaseErrno):
    def __init__(self, message, code=None):
        super().__init__(message, code=code)


class Writer0x80090019(BaseErrno):
    """Error de escritura de encriptado."""
    def __init__(self, msg: str, info: bool = False):
        super().__init__(msg, info=info)

class InvalidKiller(BaseErrno):
    """Error de cancelacion de proceso."""
    def __init__(self, msg: str, info: bool = False):
        super().__init__(msg, info=info)

