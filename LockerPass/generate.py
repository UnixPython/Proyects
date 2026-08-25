import logging 
import string
import secrets 
from exceptions import InvalidValue

logger = logging.getLogger(__name__)

def generate_password(lenght=32):
    try:
        chars = string.ascii_letters + string.digits + string.punctuation
        while True:
            passwd = ''.join(secrets.choice(chars) for i in range(lenght))
            logger.info("Se generó contraseña.")
            if (any(c.islower() for c in passwd)
                and any(c.isupper() for c in passwd)
                and sum(c.isdigit() for c in passwd) >= 3):
                break
            return passwd

    except ValueError as exc:
        raise InvalidValue("Valor invalido") from exc
    logger.error("El valor no fue valido")
