import logging
import subprocess

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("audit-erros.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class InvalidProcess(subprocess.CalledProcessError):
    """Error de validacion de proceso."""
