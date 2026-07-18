import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %I:%M:%S %p'
)

logger = logging.getLogger('mi_app')

logger.debug("Esto se ve")
logger.error("Esto también")
