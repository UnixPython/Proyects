"""
EncryptPart - snippets GENERICOS de lo que los manuales NO cubren.

Los manuales explican piezas sueltas (XTS, Argon2id, keywrap, struct, os...).
Aqui esta el "pegamento" entre ellas. No es la solucion final: adaptalo a
tu diseno real (nombres, formato del header, tamanos).

Probado con: cryptography 46.x, Python 3 en Linux.
Ejecutar los tests:  python snippets_faltantes.py
"""
import atexit
import ctypes                                                                                                                        import ctypes.util
import fcntl
import logging
import os
import resource                                                                                                                      import secrets
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import unittest

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.keywrap import (
    InvalidUnwrap, aes_key_unwrap, aes_key_wrap,
)

# ======================================================================
# A. EXCEPCIONES + LOGGING  (exceptions.py)
# ======================================================================
class EncryptPartError(Exception):
    """Base de todos los errores del proyecto."""

class InvalidPasswordError(EncryptPartError): ...
class CorruptHeaderError(EncryptPartError): ...
class NotRootError(EncryptPartError): ...
class DeviceMountedError(EncryptPartError): ...
class DeviceBusyError(EncryptPartError): ...


def config_logging(ruta="encryptpart.log", nivel=logging.INFO):
    # Regla: NUNCA loguear contrasenas, keys, KEK ni plaintext.
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(ruta), logging.StreamHandler()],
    )


# ======================================================================
# B. CIFRADO DE SECTORES  (crypt.py) - funciones puras
# ======================================================================
SECTOR = 4096          # una sola constante para todo el proyecto
KEY_SIZE = 64          # AES-256-XTS = key de doble longitud


def _tweak(n: int) -> bytes:
    # Convencion LUKS "plain64": sector en little-endian, 16 bytes.
    return n.to_bytes(16, "little")


def cifrar_sector(key: bytes, n: int, datos: bytes) -> bytes:
    if len(key) != KEY_SIZE:
        raise ValueError(f"la key debe medir {KEY_SIZE} bytes")
    if len(datos) != SECTOR:
        raise ValueError(f"el sector debe medir {SECTOR} bytes")
    enc = Cipher(algorithms.AES(bytes(key)), modes.XTS(_tweak(n))).encryptor()
    return enc.update(datos) + enc.finalize()


def descifrar_sector(key: bytes, n: int, datos: bytes) -> bytes:
    if len(key) != KEY_SIZE:
        raise ValueError(f"la key debe medir {KEY_SIZE} bytes")
    if len(datos) != SECTOR:
        raise ValueError(f"el sector debe medir {SECTOR} bytes")
    dec = Cipher(algorithms.AES(bytes(key)), modes.XTS(_tweak(n))).decryptor()
    return dec.update(datos) + dec.finalize()


# ======================================================================
# C. HEADER + WRAP  (header.py)
# ======================================================================
MAGIC = b"ENCPART\x00"
VERSION = 1
WRAPPED_SIZE = KEY_SIZE + 8          # aes_key_wrap agrega 8 bytes
# ">" = big-endian, sin alineacion nativa.
#  magic(8) version(H) salt(16) t(I) m(I) p(I) wrapped(72)
HEADER_FMT = ">8sH16sIII72s"
HEADER_SIZE = struct.calcsize(HEADER_FMT)
HEADER_AREA = 4096                   # espacio reservado antes de los datos
assert HEADER_SIZE <= HEADER_AREA and HEADER_AREA % SECTOR == 0

# Parametros Argon2 por defecto: MIDE en tu maquina y ajusta.
ARGON_T, ARGON_M_KIB, ARGON_P = 3, 64 * 1024, 4


def _derivar_kek(password: bytes, salt: bytes, t: int, m: int, p: int) -> bytes:
    return Argon2id(
        salt=salt, length=32, iterations=t, lanes=p, memory_cost=m,
    ).derive(password)


def pack_header(salt, t, m, p, wrapped) -> bytes:
    raw = struct.pack(HEADER_FMT, MAGIC, VERSION, salt, t, m, p, wrapped)
    return raw.ljust(HEADER_AREA, b"\x00")     # relleno hasta el area


def unpack_header(raw: bytes):
    if len(raw) < HEADER_SIZE:
        raise CorruptHeaderError("header incompleto")
    magic, ver, salt, t, m, p, wrapped = struct.unpack(
        HEADER_FMT, raw[:HEADER_SIZE])
    if magic != MAGIC:
        raise CorruptHeaderError("magic invalido")
    if ver != VERSION:
        raise CorruptHeaderError(f"version no soportada: {ver}")
    return salt, t, m, p, wrapped


def crear_volumen(password: bytes, t=ARGON_T, m=ARGON_M_KIB, p=ARGON_P):
    """Devuelve (master_key, header_raw). Guarda header_raw al inicio del .enc."""
    master = bytearray(secrets.token_bytes(KEY_SIZE))
    salt = secrets.token_bytes(16)
    kek = _derivar_kek(password, salt, t, m, p)
    wrapped = aes_key_wrap(kek, bytes(master))
    return master, pack_header(salt, t, m, p, wrapped)


def abrir_volumen(password: bytes, header_raw: bytes) -> bytearray:
    salt, t, m, p, wrapped = unpack_header(header_raw)
    kek = _derivar_kek(password, salt, t, m, p)
    try:
        return bytearray(aes_key_unwrap(kek, wrapped))
    except InvalidUnwrap:
        # Contrasena incorrecta (o header alterado).
        raise InvalidPasswordError("contrasena incorrecta") from None


# ======================================================================
# D. E/S DE SECTORES CON OFFSET  (disks.py)
# ======================================================================
def _pos(n: int) -> int:
    return HEADER_AREA + n * SECTOR      # los datos empiezan tras el header


def escribir_sector(fd: int, master: bytes, n: int, datos: bytes) -> None:
    ct = cifrar_sector(master, n, datos)
    if os.pwrite(fd, ct, _pos(n)) != SECTOR:
        raise OSError("escritura incompleta")
    os.fsync(fd)


def leer_sector(fd: int, master: bytes, n: int) -> bytes:
    ct = os.pread(fd, SECTOR, _pos(n))
    if len(ct) != SECTOR:
        raise OSError("lectura incompleta (sector fuera del contenedor)")
    return descifrar_sector(master, n, ct)


# ======================================================================
# E. MEMORIA: CEROS + mlock  (memzo.py)
# ======================================================================
def borrar(buf: bytearray) -> None:
    """Pone a cero un bytearray. Solo sirve con bytearray (bytes es inmutable).
    Es mejor esfuerzo: la libreria/Python pueden haber dejado copias."""
    if len(buf):
        ctypes.memset((ctypes.c_char * len(buf)).from_buffer(buf), 0, len(buf))


def _libc():
    return ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)


def bloquear(buf: bytearray) -> bool:
    """mlock: evita que estas paginas vayan a swap. Puede fallar sin root o
    por RLIMIT_MEMLOCK; en ese caso devuelve False (no es fatal)."""
    addr = ctypes.addressof((ctypes.c_char * len(buf)).from_buffer(buf))
    return _libc().mlock(ctypes.c_void_p(addr), ctypes.c_size_t(len(buf))) == 0


def desbloquear(buf: bytearray) -> None:
    addr = ctypes.addressof((ctypes.c_char * len(buf)).from_buffer(buf))
    _libc().munlock(ctypes.c_void_p(addr), ctypes.c_size_t(len(buf)))


def desactivar_core_dumps() -> None:
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


# ======================================================================
# F. SENALES: limpiar al cancelar  (memzo.py)
# ======================================================================
_secretos: list = []
_fds: list = []


def registrar_secreto(buf: bytearray) -> None:
    _secretos.append(buf)


def registrar_fd(fd: int) -> None:
    _fds.append(fd)


def limpiar_todo() -> None:
    for b in _secretos:
        try:
            desbloquear(b)
        except Exception:
            pass
        borrar(b)
    _secretos.clear()
    for fd in _fds:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
        except OSError:
            pass
    _fds.clear()


def _handler(signum, frame):
    logging.getLogger("memzo").warning("senal %s: limpiando y saliendo", signum)
    limpiar_todo()
    sys.exit(128 + signum)


def instalar_handlers() -> None:
    # SIGKILL no se puede capturar.
    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)
    atexit.register(limpiar_todo)


# ======================================================================
# G. DISCOS: root, montaje, bloqueo, tamano  (disks.py)
# ======================================================================
def exigir_root() -> None:
    if os.geteuid() != 0:
        raise NotRootError("se necesita root para dispositivos de bloque")


def esta_montada(ruta: str) -> bool:
    if shutil.which("findmnt") is None:
        raise EncryptPartError("falta 'findmnt' (paquete util-linux)")
    r = subprocess.run(["findmnt", ruta], capture_output=True, text=True)
    return r.returncode == 0


def abrir_bloqueado(ruta: str) -> int:
    fd = os.open(ruta, os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)   # advisory
    except BlockingIOError:
        os.close(fd)
        raise DeviceBusyError(f"{ruta} esta en uso por otro proceso") from None
    return fd


def tamano(fd: int) -> int:
    """Tamano en bytes (funciona con archivos y dispositivos de bloque)."""
    return os.lseek(fd, 0, os.SEEK_END)


def crear_img(ruta: str, n_sectores: int) -> None:
    """Contenedor de prueba: header + n sectores, relleno de ceros."""
    with open(ruta, "wb") as f:
        f.truncate(HEADER_AREA + n_sectores * SECTOR)


def confirmar_destructivo(ruta: str) -> None:
    if input(f"Operacion destructiva. Escribe '{ruta}' para continuar: ") != ruta:
        raise EncryptPartError("cancelado por el usuario")


# ======================================================================
# H. TESTS UNITARIOS  (checker.py los ejecutaria)
# ======================================================================
class TestEncryptPart(unittest.TestCase):
    # Argon2 liviano SOLO para que los tests sean rapidos.
    T, M, P = 1, 8 * 1024, 1

    def test_roundtrip_sector(self):
        key, datos = secrets.token_bytes(64), secrets.token_bytes(SECTOR)
        self.assertEqual(descifrar_sector(key, 7, cifrar_sector(key, 7, datos)), datos)

    def test_sectores_distintos_dan_ct_distinto(self):
        key, datos = secrets.token_bytes(64), b"\x00" * SECTOR
        self.assertNotEqual(cifrar_sector(key, 1, datos), cifrar_sector(key, 2, datos))

    def test_sector_incorrecto_da_basura(self):
        key, datos = secrets.token_bytes(64), secrets.token_bytes(SECTOR)
        ct = cifrar_sector(key, 3, datos)
        self.assertNotEqual(descifrar_sector(key, 4, ct), datos)

    def test_tamanos_invalidos(self):
        with self.assertRaises(ValueError):
            cifrar_sector(b"x" * 32, 0, b"\x00" * SECTOR)
        with self.assertRaises(ValueError):
            cifrar_sector(b"x" * 64, 0, b"\x00" * 10)

    def test_header_roundtrip_y_password(self):
        master, raw = crear_volumen(b"clave", self.T, self.M, self.P)
        self.assertEqual(len(raw), HEADER_AREA)
        self.assertEqual(abrir_volumen(b"clave", raw), master)
        with self.assertRaises(InvalidPasswordError):
            abrir_volumen(b"otra", raw)

    def test_header_corrupto(self):
        _, raw = crear_volumen(b"clave", self.T, self.M, self.P)
        with self.assertRaises(CorruptHeaderError):
            unpack_header(b"XXXXXXXX" + raw[8:])
        with self.assertRaises(CorruptHeaderError):
            unpack_header(raw[:10])

    def test_img_escribir_leer(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = os.path.join(d, "disco.img")
            crear_img(ruta, 4)
            master, raw = crear_volumen(b"clave", self.T, self.M, self.P)
            fd = abrir_bloqueado(ruta)
            try:
                self.assertEqual(tamano(fd), HEADER_AREA + 4 * SECTOR)
                os.pwrite(fd, raw, 0)
                datos = secrets.token_bytes(SECTOR)
                escribir_sector(fd, master, 2, datos)
                # lo guardado en disco NO es el plaintext
                self.assertNotEqual(os.pread(fd, SECTOR, _pos(2)), datos)
                # reabrir desde el header del archivo
                m2 = abrir_volumen(b"clave", os.pread(fd, HEADER_AREA, 0))
                self.assertEqual(leer_sector(fd, m2, 2), datos)
                with self.assertRaises(OSError):
                    leer_sector(fd, m2, 99)            # fuera del contenedor
            finally:
                os.close(fd)

    def test_flock_exclusivo(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = os.path.join(d, "disco.img")
            crear_img(ruta, 1)
            fd = abrir_bloqueado(ruta)
            try:
                with self.assertRaises(DeviceBusyError):
                    abrir_bloqueado(ruta)
            finally:
                os.close(fd)

    def test_borrar(self):
        b = bytearray(b"secreto" * 10)
        borrar(b)
        self.assertEqual(bytes(b), b"\x00" * 70)

    def test_mlock_no_revienta(self):
        b = bytearray(64)
        print("mlock ->", bloquear(b))    # True/False segun permisos
        desbloquear(b)

    def test_esta_montada_archivo_normal(self):
        with tempfile.NamedTemporaryFile() as f:
            self.assertFalse(esta_montada(f.name))


if __name__ == "__main__":
    unittest.main(verbosity=2)
