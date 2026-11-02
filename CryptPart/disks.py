"""Utilidades para manejo de contenedor cifrado por sectores."""

import fcntl
import logging
import os
import subprocess

import header as hdr
import cryptos
from exceptions import BusyFailed, base

logger = logging.getLogger(__name__)

def root():
    """Verifica si el usuario actual es root."""
    if os.getuid()!= 0:
        return "Se requiere root para continuar."
         
    else:
        print("Ya es root.")

@base
def parts():
    """Lista las particiones del sistema usando lsblk."""
    try:
        result = subprocess.run(
            ["lsblk", "-o", "NAME,SIZE,FSTYPE,MOUNTPOINT,UUID"],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        logging.info("Se enumeró información en disco.")
    except subprocess.CalledProcessError as e:
        print("""
        No se ha podido enumerar las particiones
        en disco. Se requiere analizar codigo fuente.""")
        print(f"Error: {e.stderr}")
        logger.critical("Error critico: [lsblk]")

@base
def block(rute: str) -> int:
    """Abre y bloquea exclusivamente un dispositivo/ruta."""
    fd = os.open(rute, os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        os.close(fd)
        raise BusyFailed("Erroneo o en uso") from exc
    return fd

@base
def rutas() -> str:
    """Solicita una ruta al usuario."""
    ruta = input("Escriba una ruta para continuar: ")
    if not ruta:
        raise ValueError("No se ingresó ninguna ruta")
    print("Ruta:", ruta)
    return ruta

@base
def size(fd: int) -> int:
    """Retorna el tamaño del archivo/dispositivo."""
    return os.lseek(fd, 0, os.SEEK_END)

@base
def _pos(n: int) -> int:
    """Calcula la posicion fisica del sector n."""
    return hdr.HEADER_AREA + n * cryptos.SECTOR

@base
def write_sector(fd, master, n, datos) -> None:
    """Cifra y escribe un sector."""
    ct = cryptos.encrypt(master, n, datos)
    if os.pwrite(fd, ct, _pos(n))!= cryptos.SECTOR:
        raise OSError("escritura incompleta")
    os.fsync(fd)

@base
def read_sector(fd, master, n) -> bytes:
    """Lee y descifra un sector."""
    ct = os.pread(fd, cryptos.SECTOR, _pos(n))
    if len(ct)!= cryptos.SECTOR:
        raise OSError("lectura incompleta (sector fuera del contenedor)")
    return cryptos.decrypt(master, n, ct)

