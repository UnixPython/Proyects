import logging 
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from exceptions import base 

logger = logging.getLogger(__name__)

@base 
def encrypt_passwd():
    """Registra y verifica una contraseña de sesión con Argon2id (argon2-cffi)."""
    ph = PasswordHasher()
    passw = input("Contraseña:   ").strip()
    pass_gen = ph.hash(passw)
    logger.info("Contraseña hasheada correctamente.")
    try:
        ph.verify(pass_gen, passw)
        print("Contraseña verificada correctamente.")
    except VerifyMismatchError as e:
        print("Contraseña errónea.")
        logger.error("Error de verificación: %s", e)

