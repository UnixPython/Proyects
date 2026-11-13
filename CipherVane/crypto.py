"""Módulo para la generación y exportación segura de claves criptográficas."""
import logging
from cryptography.hazmat.primitives import serialization
from logger import base, timer
from exceptions import keyGenerateError

logger = logging.getLogger(__name__)

@timer
@base
def private(ec_key, passphrase: bytes) -> bytes:
    """Exporta la clave privada PEM cifrada con la passphrase indicada."""
    try:
        return ec_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(passphrase),
        )
    except (ValueError, TypeError) as e:
        logger.critical("No se pudo generar la clave privada: %s", e)
        raise keyGenerateError("Fallo al serializar la clave privada") from e


def public(ec_key) -> bytes:
    """Exporta la clave pública PEM."""
    try:
        return ec_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    except ValueError as e:
        logger.critical("No se pudo generar la clave pública: %s", e)
        raise keyGenerateError("Fallo al serializar la clave pública") from e
