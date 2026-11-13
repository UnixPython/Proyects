"""Logs y decoradores."""

import logging
import time
import traceback
from functools import wraps

logger = logging.getLogger(__name__)

# variables de categoria de evento
infos = logging.FileHandler("infos.log")
warms = logging.FileHandler("warms.log")
errors = logging.FileHandler("errors.log")
crit = logging.FileHandler("criticsl.log")
verbose = logging.FileHandler("debug.log")

infos.setLevel(logging.INFO)
warms.setLevel(logging.WARNING)
errors.setLevel(logging.ERROR)
crit.setLevel(logging.CRITICAL)
verbose.setLevel(logging.DEBUG)

logger.addHandler(infos)
logger.addHandler(warms)
logger.addHandler(errors)
logger.addHandler(crit)
logger.addHandler(verbose)

class CheckerBug(Exception):
    """Deteccion de bug."""

def timer(funcion):
    """Mide tiempo."""
    def funcion_medida(*args, **kwargs):
        inicio = time.time()
        c = funcion(*args, **kwargs)
        print(time.time() - inicio)
        return c
    return funcion_medida

def base(func):
    """Busca bugs."""
    @wraps(func)
    def test(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            print("Se iniciará la busqueda de bugs.")
            logger.info("Se inició el decorator.")
            print(f"line: {func.__name__}")
            print("Variables: ", locals())
            logger.info("Se inicio con exito: %s", func.__name__)
            return result
        except Exception as exc:
            text_error = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            tb = exc.__traceback__
            last_frame = traceback.extract_tb(tb)[-1]
            print(f"line: {last_frame.name} - {last_frame.lineno}")
            raise CheckerBug(f"Fallo detectado en {text_error}") from exc
    return test
