import ctypes
import logging 
import signal
#-----------------------------
#logging

logger = logging.getLogger(__name__)
#-----------------------------

#------------------------------
#Class

class MemClearError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code

class SIGINTError(Exception):
    pass
#------------------------------
#Funtions
#------------------------------

def clean_memory():
    try:
        import os
        buf = bytearray(os.urandom(32))
        buf[:] = b"\x00" * len(buf)
        var = ctypes.c_ubyte(0x00)
        ctypes.memset(ctypes.byref(var), 0x55, 1)
        if buf != bytearray(len(buf)):
            raise MemClearError("Falló la limpieza de memoria.")
        return var
    except OSError as e:
        print(f"Falló por kernel o sistema {e}")
        logger.warning("Falló por configuraciones incorrectas.")
        return None


#--------------------------------
def signal_handler(sig, _):
    try:
        import time 
        import sys
        if sig == signal.SIGINT:
            time.sleep(3)
            print("Interrupción recibida (SIGINT/Ctrl+c) Limpiando y saliendo...")
            clean_memory() 
        elif sig == signal.SIGTERM:
            time.sleep(2)
            print("\n¡Terminación solicitada (SIGTERM)! Limpiando y saliendo...")
            clean_memory()
        sys.exit(0)
    except SIGINTError as e:
        print("Error en: ", e)
    finally: 
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
#----------------------------------------
carpet = "/tmp"

def verifytmp():
    import os
    if os.path.exists(carpet) and os.access(carpet, os.W_OK | os.X_OK):
        pass
    else:
        print("El directorio NO tiene permisos de escritura.")
verifytmp()
#----------------------------------------

RETRYS = 0
TIME = 600
file = "/tmp/timr.tmp"

def timer():
    try:
        import os
        import time
        trs = None
        attempts = 3
        logger.info("Se realizó la creación del archivo.")
        with open(file, "a", encoding="utf-8") as f:
            if os.path.exists(file):
                print("Se creó el archivo.")
                with open(file, "r", encoding="utf-8") as f:
                    inten = float(f.read())
                    trs = time.time() - inten 
            if trs is not None and trs < TIME:
                rest = int(TIME - trs)
                print(f"Demasiado pronto. Faltan {rest} segundos.")
            else:
                attempts -= 1
                if attempts >= RETRYS:
                    with open(file, "w", encoding="utf-8") as f:
                        f.write(str(time.time()))
                        print("FALLÓ")

    except ValueError as e:
        print(f"Error de valor: {e}")

timer()


