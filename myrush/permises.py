import os
import time
import logging


class ErrCode(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("Error.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def permises():
    try:
        time.sleep(8)
        print("Se verificará root y el ID del sistema.")
        os.system("id")
        os.system("whoami")
    except Exception as e:
        logger.error(e)
        raise ErrCode(f"Hubo un fallo durante la ejecución. {e}")


def commands():
    try:
        time.sleep(5)
        print("Se analizarán los binarios.")
        os.system("find / -perm -4000 2>/dev/null")
        print("Binarios analizados.")
        os.system("getcap -r / 2>/dev/null")
    except FileNotFoundError as e:
        logger.error(e)
        raise ErrCode(f"Error durante la ejecución. {e}")
