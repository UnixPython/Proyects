import argparse
import logging
import os 
import disks
import header
import session
from exceptions import InvalidArgument, base, RuteNotFound

logger = logging.getLogger(__name__)


@base
def runs():
    """Ejecuta la rama del script y procesa comandos"""
    supers = disks.root()
    if supers is None:
        logger.warning("[!] Error de root")
        raise RuteNotFound("Falla la deteccion de root.")

    parser = argparse.ArgumentParser(
        description="Encriptar y desencriptar particiones. Se requiere analizar la particion."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Registrar
    subparsers.add_parser("registrar", help="Registrar nuevo usuario")

    # Encriptar
    encrypt_parser = subparsers.add_parser("encriptar", help="Encriptar particion")
    encrypt_parser.add_argument("particion", help="Particion a encriptar.")
    encrypt_parser.add_argument(
        "--clave", required=True, help="Clave de encriptacion de la particion"
    )

    # Desencriptar
    decrypt_parser = subparsers.add_parser("desencriptar", help="Desencriptar particion")
    decrypt_parser.add_argument("particion", help="Particion a desencriptar")
    decrypt_parser.add_argument(
        "--clave", required=True, help="Clave de descifrado"
    )

    try:
        args = parser.parse_args()

        if args.command == "encriptar":
            logger.info("Encriptado activado.")
            print("Encriptado se ha activado.")
            fd = disks.block(args.particion)
            master, header_raw = header.crear_volumen(args.clave.encode())
            os.pwrite(fd, header_raw, 0)

        elif args.command == "desencriptar":
            logger.info("Se ha quitado el encriptado.")
            print("Desencriptado de disco activado.")
            fd = disks.block(args.particion)
            header_raw = os.pread(fd, header.HEADER_AREA, 0)
            master = header.abrir_volumen(args.clave.encode(), header_raw)
            return master

        elif args.command == "registrar":
            logger.info("Registro de usuario activado.")
            session.encrypt_passwd()

    except InvalidArgument:
        print("Comando no existe")

