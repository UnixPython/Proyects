import logging
import traceback
from functools import wraps

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("warning.log")
    ]
)

logger = logging.getLogger(__name__)

class CheckerBug(Exception):
    """Deteccion de bug."""

def base(func):
    @wraps(func)
    def test(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            print("Se iniciará la busqueda de bugs.")
            logger.info("Se inició el decorator.")
            
            # Usa el nombre de la funcion original, no el del wrapper
            print(f"line: {func.__name__}")
            logger.info(f"Se inicio con exito: {func.__name__}")
            
            return result
        except Exception as exc:
            text_error = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            # Para el error, saca la linea real de donde fallo
            tb = exc.__traceback__
            last_frame = traceback.extract_tb(tb)[-1]
            print(f"line: {last_frame.name} - {last_frame.lineno}")
            raise CheckerBug(f"Fallo detectado en {text_error}") from exc
    return test

#Class Errnos header.py

class InvalidPassword(Exception):
    """Contraseña criptografica invalida."""
    def __init__(self,  code):
        super().__init__(code)
        self.code = code

class HeaderInvalid(Exception):
    """Header invalido error"""
    

#Class  Errnos memory.py

class BufferSizeError(Exception):
    """Los datos exceden el tamaño reservado del buffer."""

class LockError(Exception):
    """Error al bloquear o desbloquear memoria (mlock/munlock)."""

class BaseErrno(Exception):
    """Clase base para errores de memoria segura del proyecto."""

class MemCeroErr(Exception):
    """Error al poner en cero una región de memoria."""

class AllocationError(Exception):
    """Error al reservar memoria (sodium_malloc devolvió NULL o tamaño inválido)."""

class UseAfterFreeError(Exception):
    """Se intentó usar un buffer ya liberado."""

class MemmoveError(Exception):
    """Error al copiar datos a memoria protegida con ctypes.memmove."""

#Class Errnos disks.py

class BusyFailed(Exception):
    """Erroneo o en uso"""
    def __init__(self, msg, code=False):
        super().__init__(msg)
        self.code = code
        self.msg = msg

    def __str__(self):
        return f"{self.code} {self.msg}"

#class check.py

class FailedModule(Exception):
    """Modulo de error"""

#Class Error rute commands.py

class RuteNotFound(Exception):
    """Manejo de error de ruta. """

#class commands.py

class InvalidArgument(Exception):
    """Comando invalido o inexistente."""
    def __init__(self, msg, code=False):
        super().__init__(msg)
        self.code = code 
        self.msg = msg 


