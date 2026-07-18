#Librarys
import secrets
import time
import hmac
import hashlib
import base64
import logging
#-----------------------------------
#Logger 
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(
            filename="asfm03fm.log",
            encoding="utf-8"
        )
    ]
)

logger = logging.getLogger(__name__)
#-------------------------------------
#Exceptions Class

class ErrorGen(Exception):
    """Excepcion de generacion de token"""
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code 

class ErrrValid(Exception):
    """Excepcion de validacion de token"""
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code 

class F000x92900001(Exception):
    """Excepcion de token revocado"""
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = None 

class F0000000x10FFFF(Exception):
    """Excepcion de expiracion de token"""
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = None 
#--------------------------------------
SECRET_KEY = secrets.token_bytes(64)
TOKEN_EXPIRATION = 300

# Solo en RAM
_revoked = set()

def generate_token():
    """Genera un token firmado."""
    try:
        logging.info("Se creo el token.")
        rand = secrets.token_bytes(64)
        t_create = time.time_ns()
        t_exp = t_create + TOKEN_EXPIRATION
        payload = rand + t_create.to_bytes(8, 'big') + t_exp.to_bytes(8, 'big')
        logging.warning("Se creó el payload")
        firma = hmac.new(SECRET_KEY, payload, digestmod=hashlib.sha3_512).digest()
        data = payload + firma
        logging.info("Se cargó el valor de data.")
        return base64.urlsafe_b64encode(data).decode()
    except OSError:
        logging.critical("Falló la generación de token. Se requiere revisión en el codigo.")
        raise ErrorGen("Nose pudo generar entropía segura para el token.")
    except OverflowError as e:
        logging.warning("Timestamp falló")
        raise F0000000x10FFFF(
            f"El timestamp de expiración ({t_exp}) excede los 8 bytes. "
            f"Revisa EXPIRATION actual: {TOKEN_EXPIRATION}.") from e

def validate_token(token):
    """Verifica integridad y expiración."""
    try:
        if token in _revoked:
            return False
        raw = base64.urlsafe_b64decode(token + "==")
        payload, received = raw[:-64], raw[-64:]
        sig = hmac.new(SECRET_KEY, payload, hashlib.sha3_512).digest()
        compare = hmac.compare_digest(sig, received)
        ts = int.from_bytes(payload[-8:], "big")
        timer = time.time() > ts + TOKEN_EXPIRATION
    except Exception as e:
        raise ErrrValid("Falló la comparación de tokens.")

def revoke_token(token):
    """Revoca un token."""
    try:
        _revoked.add(token)
    except Exception:
        raise F0000000x10FFFF("Error al revokar token.")

def is_expired(token):
    """Comprueba únicamente la expiración."""
    try:
        raw = base64.urlsafe_b64decode(token + "==")
        payload = raw[:-64]
        ts = int.from_bytes(payload[-8:], "big")
        return time.time() > ts + TOKEN_EXPIRATION
    except Exception:
        raise F0000000x10FFFF("Se pasó el limite de expiración. del token.") 
