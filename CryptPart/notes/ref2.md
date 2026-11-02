# EncryptPart — Referencia completa por archivo

Todo lo verificado en este chat (documentación oficial, código fuente real,
o probado con ejecución). Nada de esto es el archivo final: es la base para
que adaptes con tu lógica de errores, logging y estructura de clases.

Leyenda: **[DOC]** = de la documentación oficial · **[FUENTE]** = de código
fuente real (GitHub) · **[PROBADO]** = lo corrimos en este chat y funcionó ·
**[DISEÑO]** = decisión de diseño, no viene de ningún manual.

---

## 1. `exceptions.py`

Excepciones propias, una clase por tipo de fallo. Patrón simple: solo
`class` + docstring, sin lógica.

```python
class EncryptPartError(Exception):
    """Base de todos los errores del proyecto."""

# --- disco / header ---
class InvalidPassword(EncryptPartError):
    """La contraseña no coincide con el volumen (unwrap falló)."""

class HeaderInvalid(EncryptPartError):
    """El header está corrupto, incompleto o con magic/versión inválidos."""

class NotRoot(EncryptPartError):
    """La operación requiere privilegios de root."""

class DeviceBusy(EncryptPartError):
    """El dispositivo ya está bloqueado por otro proceso (flock)."""

class DeviceMounted(EncryptPartError):
    """El dispositivo está montado; debe desmontarse antes de operar."""

# --- memoria segura (memzo.py) ---
class BufferSizeError(EncryptPartError):
    """Los datos exceden el tamaño reservado del buffer."""

class LockError(EncryptPartError):
    """Error al bloquear o desbloquear memoria (mlock/munlock)."""

class MemCeroErr(EncryptPartError):
    """Error al poner en cero una región de memoria."""

class AllocationError(EncryptPartError):
    """Error al reservar memoria (sodium_malloc devolvió NULL o tamaño inválido)."""

class UseAfterFreeError(EncryptPartError):
    """Se intentó usar un buffer ya liberado."""

class MemmoveError(EncryptPartError):
    """Error al copiar datos a memoria protegida con ctypes.memmove."""
```

**Excepciones de terceros que vas a re-lanzar o capturar, no las escribas tú:**
- `cryptography.exceptions.AlreadyFinalized` — instancia de `Argon2id` reutilizada. **[PROBADO]**
- `cryptography.hazmat.primitives.keywrap.InvalidUnwrap` — contraseña incorrecta al abrir volumen.
- `argon2.exceptions.VerifyMismatchError` / `VerificationError` / `InvalidHashError` — de `session.py`. **[DOC]**

---

## 2. `crypt.py`

Funciones puras: reciben bytes, devuelven bytes. Sin contraseñas, sin
archivos, sin sesión.

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SECTOR = 4096
KEY_SIZE = 64          # AES-256-XTS: la key de XTS es de doble longitud [DOC]

def _tweak(n: int) -> bytes:
    # Convención LUKS "plain64": número de sector, little-endian, 16 bytes [DISEÑO]
    return n.to_bytes(16, "little")

def cifrar_sector(key: bytes, n: int, datos: bytes) -> bytes:
    if len(key) != KEY_SIZE:
        raise ValueError(f"la key debe medir {KEY_SIZE} bytes")
    if len(datos) != SECTOR:
        raise ValueError(f"el sector debe medir {SECTOR} bytes")
    enc = Cipher(algorithms.AES(bytes(key)), modes.XTS(_tweak(n))).encryptor()
    return enc.update(datos) + enc.finalize()          # XTS no usa padding [DOC]

def descifrar_sector(key: bytes, n: int, datos: bytes) -> bytes:
    if len(key) != KEY_SIZE:
        raise ValueError(f"la key debe medir {KEY_SIZE} bytes")
    if len(datos) != SECTOR:
        raise ValueError(f"el sector debe medir {SECTOR} bytes")
    dec = Cipher(algorithms.AES(bytes(key)), modes.XTS(_tweak(n))).decryptor()
    return dec.update(datos) + dec.finalize()
```

**[PROBADO]** roundtrip, sectores distintos dan ciphertext distinto, key de
32 bytes rechazada.

**Nota importante de XTS [PROBADO]:** las dos mitades de la key no pueden
ser iguales — `cryptography` lanza `ValueError: In XTS mode duplicated keys
are not allowed`. Con `secrets.token_bytes(64)` esto no pasa nunca (la
probabilidad es despreciable), solo afecta si armas una key a mano para test.

**Fingerprint** (para identificar datos, NO para derivar keys):
```python
import hashlib
fingerprint = hashlib.sha256(datos).hexdigest()
```

---

## 3. `header.py`

Crear/abrir el volumen: master key, salt, Argon2id, wrap/unwrap, struct.

```python
import os
import secrets
import struct
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.keywrap import (
    aes_key_wrap, aes_key_unwrap, InvalidUnwrap,
)
from exceptions import InvalidPassword, HeaderInvalid

MAGIC = b"CRYPTPRT"          # 8 bytes exactos
VERSION = 1
KEY_SIZE = 64                 # debe coincidir con crypt.py
SECTORR_HDD = 512
# "!" = network byte order = big-endian, igual que LUKS2 [FUENTE: spec LUKS2]
HEADER_FMT = "!8s I 16s I I I 72s"   # magic ver salt t m p wrapped(64+8)
HEADER_SIZE = struct.calcsize(HEADER_FMT)
HEADER_AREA = 4096
assert len(MAGIC) == 8
assert HEADER_SIZE <= HEADER_AREA and HEADER_AREA % SECTORR_HDD == 0

ARGON_T = 3
ARGON_M_KIB = 64 * 1024
ARGON_P = min(4, os.cpu_count() or 1)


def _derivar_kek(password: bytes, salt: bytes, t: int, m: int, p: int) -> bytes:
    """Deriva una KEK de 32 bytes. Instancia nueva cada llamada (no reutilizar)."""
    return Argon2id(
        salt=salt, length=32, iterations=t, lanes=p, memory_cost=m,
    ).derive(password)


def pack_header(salt, t, m, p, wrapped) -> bytes:
    raw = struct.pack(HEADER_FMT, MAGIC, VERSION, salt, t, m, p, wrapped)
    return raw.ljust(HEADER_AREA, b"\x00")


def unpack_header(raw: bytes):
    if len(raw) < HEADER_SIZE:
        raise HeaderInvalid("Header incompleto.")
    magic, ver, salt, t, m, p, wrapped = struct.unpack(HEADER_FMT, raw[:HEADER_SIZE])
    if magic != MAGIC:
        raise HeaderInvalid("Magic inválido.")
    if ver != VERSION:
        raise HeaderInvalid(f"Versión no soportada: {ver}")
    return salt, t, m, p, wrapped


def crear_volumen(password: bytes, t=ARGON_T, m=ARGON_M_KIB, p=ARGON_P):
    """Devuelve (master_key, header_raw)."""
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
        raise InvalidPassword("Contraseña incorrecta o header corrupto") from None
```

**[PROBADO]** completo: crear → abrir con contraseña correcta (coincide) →
contraseña incorrecta (`InvalidPassword`) → header con magic alterado
(`HeaderInvalid`).

**Bug real que salió y se corrigió [PROBADO]:** si `KEY_SIZE` (32) no
coincide con el tamaño reservado en `HEADER_FMT` (`72s`, calculado para
64+8), `struct` rellena con ceros al empaquetar y esos ceros se filtran al
`aes_key_unwrap`, rompiendo el volumen incluso con la contraseña correcta.
**`KEY_SIZE` debe ser el mismo en `header.py` y `crypt.py`.**

**Excepciones de `Argon2id` a manejar [PROBADO]:**
```python
from cryptography.exceptions import AlreadyFinalized
# ValueError: "salt must be at least 8 bytes" (tu salt de 16 nunca lo dispara)
# AlreadyFinalized: si reutilizas la misma instancia de Argon2id — no lo hagas
```

**Diseño checksum de header (LUKS2), por si lo agregas [FUENTE: spec LUKS2 +
código fuente cryptsetup]:** el campo de checksum se calcula con el propio
campo de checksum puesto en ceros antes de hashear; el campo de algoritmo
mide 32 bytes y el de checksum 64 (con relleno si el hash es más corto, ej.
SHA-256 de 32 bytes en un campo de 64).

---

## 4. `memzo.py`

Memoria segura: bloquear, poner en cero, limpiar ante señales.

### Con libsodium vía `pysodium` (recomendado — tu propio diseño anterior)

**[PROBADO]** — funciona con `libsodium23` instalada en el sistema.

```python
import ctypes
import pysodium
from exceptions import AllocationError, UseAfterFreeError, BufferSizeError

sodium = pysodium.sodium          # pysodium ya hace CDLL por dentro — no hace
                                   # falta ctypes.util.find_library aparte

sodium.sodium_init.restype = ctypes.c_int
sodium.sodium_init.argtypes = []
sodium.sodium_init()

sodium.sodium_malloc.restype = ctypes.c_void_p
sodium.sodium_malloc.argtypes = [ctypes.c_size_t]

sodium.sodium_mlock.restype = ctypes.c_int
sodium.sodium_mlock.argtypes = [ctypes.c_void_p, ctypes.c_size_t]

sodium.sodium_munlock.restype = ctypes.c_int
sodium.sodium_munlock.argtypes = [ctypes.c_void_p, ctypes.c_size_t]

sodium.sodium_free.restype = None
sodium.sodium_free.argtypes = [ctypes.c_void_p]


class memory:
    def __init__(self, size):
        if not isinstance(size, int) or size <= 0:      # CORREGIDO: "not size" no rechazaba negativos
            raise AllocationError("Tamaño inválido: debe ser un entero positivo.")
        ptr = sodium.sodium_malloc(size)
        if ptr is None:
            raise AllocationError("Malloc devolvió NULL: no hay memoria asignada.")
        self.size = size
        self.ptr = ptr
        self._freed = False
        self._locked = False

    def lock(self):
        if self._freed:
            raise UseAfterFreeError("No se puede bloquear un buffer ya liberado")
        ret = sodium.sodium_mlock(self.ptr, self.size)
        if ret != 0:
            # el sistema puede no soportarlo (sin CAP_IPC_LOCK, RLIMIT_MEMLOCK) [DOC libsodium]
            self._locked = False
            return
        self._locked = True

    def write(self, data):
        if self._freed:
            raise UseAfterFreeError("No se puede escribir en un buffer ya liberado")
        if len(data) > self.size:
            raise BufferSizeError("Los datos exceden el tamaño reservado del buffer")
        # CORREGIDO: ctypes.memmove rechaza bytearray directo con ArgumentError.
        # from_buffer_copy acepta bytes y bytearray por igual. [PROBADO]
        buf = (ctypes.c_char * len(data)).from_buffer_copy(bytes(data))
        ctypes.memmove(self.ptr, buf, len(data))

    def read(self):
        if self._freed:
            raise UseAfterFreeError("Buffer ya liberado: use-after-free")
        return ctypes.string_at(self.ptr, self.size)

    def close(self):
        if self._freed:
            raise UseAfterFreeError("El buffer ya fue liberado (double free)")
        if self._locked:
            sodium.sodium_munlock(self.ptr, self.size)
        sodium.sodium_free(self.ptr)   # zera y libera, pase lo que pase con el lock [DOC libsodium]
        self._freed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
```

**Uso:**
```python
with memory(64) as buf:
    buf.lock()
    buf.write(master_key)
    # ... usar buf.read() donde haga falta la key ...
# close() se llama solo al salir del "with", incluso si hay excepción
```

**Bugs reales encontrados y corregidos [PROBADO]:**
1. `if not size` no rechazaba `size=-8` (solo funcionaba por casualidad
   porque `c_size_t` sin signo lo convertía en un número gigante y
   `sodium_malloc` fallaba). Corregido a `isinstance(size, int) and size > 0`.
2. `ctypes.memmove(self.ptr, data, len(data))` con `data` tipo `bytearray`
   lanza `ctypes.ArgumentError: argument 2: TypeError: wrong type`. Con
   `bytes` funciona. Corregido envolviendo con `from_buffer_copy`.

**Doc de libsodium citada [DOC]:**
- `sodium_memzero(pnt, len)`: pone en cero de forma efectiva, resistente a
  que el compilador optimice/elimine el borrado.
- `sodium_mlock(addr, len)`: envuelve `mlock()`/`VirtualLock()`; además
  indica al kernel (vía `madvise()`) que excluya esa memoria de los core
  dumps.
- `sodium_munlock(addr, len)`: ya deja la memoria en cero por sí sola, no
  hace falta llamar `memzero` antes.
- `sodium_free()`: rellena con ceros antes de liberar.

**Ctypes: por qué declarar `argtypes`/`restype` siempre [DOC Python]:** sin
esto, `ctypes` asume que todo es `int`, lo que puede truncar punteros de 64
bits y causar segfaults. Un ejemplo documentado: comentar la declaración de
`argtypes` de una llamada que antes funcionaba produce un segfault.

### Señales (Ctrl+C) — limpieza garantizada

```python
import atexit
import signal

_buffers_activos = []

def registrar(buf) -> None:
    _buffers_activos.append(buf)

def _limpiar_todo(signum=None, frame=None):
    for buf in list(_buffers_activos):
        try:
            buf.close()
        except Exception:
            pass
    _buffers_activos.clear()
    if signum is not None:
        raise SystemExit(128 + signum)

signal.signal(signal.SIGINT, _limpiar_todo)
signal.signal(signal.SIGTERM, _limpiar_todo)   # SIGKILL no se puede capturar
atexit.register(_limpiar_todo)
```

**[PROBADO]**: al mandar `SIGINT` a un proceso con esto instalado, limpió y
salió con código 130, sin dejar el buffer sin cerrar.

### Alternativa sin libsodium — solo libc (fallback, ya probado antes)

```python
import ctypes, ctypes.util

def borrar(buf: bytearray) -> None:
    if len(buf):
        ctypes.memset((ctypes.c_char * len(buf)).from_buffer(buf), 0, len(buf))

def _libc():
    return ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)

def bloquear(buf: bytearray) -> bool:
    addr = ctypes.addressof((ctypes.c_char * len(buf)).from_buffer(buf))
    return _libc().mlock(ctypes.c_void_p(addr), ctypes.c_size_t(len(buf))) == 0
```

Usa esto solo si por algún motivo `libsodium` no está disponible en el
sistema destino; tu clase `memory` con `sodium_malloc` es más completa
(guard pages, sin exponer un `bytearray` de Python normal).

---

## 5. `session.py`

Registro/verificación de contraseña de sesión. Argon2id vía `argon2-cffi`,
**no** el de `cryptography`. Sin relación con el disco.

```python
import logging
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

logger = logging.getLogger(__name__)


def registrar(password: str) -> str:
    """Devuelve el hash a guardar. El salt ya va incluido adentro. [DOC]"""
    ph = PasswordHasher()
    return ph.hash(password)


def login(hash_guardado: str, password: str) -> bool:
    ph = PasswordHasher()
    try:
        ph.verify(hash_guardado, password)
        logger.info("Login correcto.")
        return True
    except VerifyMismatchError:
        logger.warning("Intento de login con contraseña incorrecta.")
        return False
```

**Con el perfil RFC 9106 de bajo consumo de memoria [PROBADO]:**
```python
from argon2.profiles import RFC_9106_LOW_MEMORY
ph = PasswordHasher.from_parameters(RFC_9106_LOW_MEMORY)
# Parameters(type=Type.ID, version=19, salt_len=16, hash_len=32,
#            time_cost=3, memory_cost=65536, parallelism=4)  -- 65536 KiB = 64 MiB
```

**El salt es automático [FUENTE: código real de argon2-cffi,
`_password_hasher.py`]:**
```python
salt=salt or os.urandom(self.salt_len)
```
Nunca lo generas ni lo guardas tú; queda embebido en el string del hash
(`$argon2id$v=19$m=...$<salt b64>$<hash b64>`). La propia doc advierte no
pasar un `salt=` manual "a menos que sepas realmente lo que haces".

**Re-hash si cambiaste los parámetros de costo [DOC]:**
```python
if ph.check_needs_rehash(hash_guardado):
    hash_guardado = ph.hash(password)   # ya tienes el password en claro acá
```

**Error real que salió al mezclar módulos:** `_derivar_kek` (de
`cryptography`, para `header.py`) **no va en `session.py`**. Son dos
Argon2id de dos librerías distintas: uno es un KDF de bajo nivel donde tú
generas el salt (disco), el otro es un hasher de contraseñas que lo genera
solo (sesión). Mezclarlos produce `NameError` por variables (`salt`, `t`,
`m`, `p`) que no existen en ese archivo.

**Diferencia clave — Argon2 no es cifrado:**
| | Disco (`crypt.py`) | Sesión (`session.py`) |
|---|---|---|
| Reversible | Sí, con la key (`descifrar_sector`) | **No, nunca** |
| Operación inversa | `descifrar_sector()` | No existe — solo `verify()` compara hashes |

**Excepciones [DOC]:**
| Excepción | Cuándo |
|---|---|
| `VerifyMismatchError` | la contraseña no coincide |
| `VerificationError` | falla la verificación por otra razón (superclase) |
| `InvalidHashError` | el hash está mal formado |

---

## 6. `disks.py`

E/S de bajo nivel, root, montaje, bloqueo. **[VERIFICAR]** salvo lo marcado.

```python
import os
import fcntl
import shutil
import subprocess
from exceptions import NotRoot, DeviceBusy, DeviceMounted

def exigir_root() -> None:
    if os.geteuid() != 0:
        raise NotRoot("se necesita root para dispositivos de bloque")

def esta_montada(ruta: str) -> bool:
    if shutil.which("findmnt") is None:
        raise RuntimeError("falta 'findmnt' (paquete util-linux)")
    r = subprocess.run(["findmnt", ruta], capture_output=True, text=True)
    return r.returncode == 0

def abrir_bloqueado(ruta: str) -> int:
    fd = os.open(ruta, os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)   # advisory, no absoluto
    except BlockingIOError:
        os.close(fd)
        raise DeviceBusy(f"{ruta} está en uso por otro proceso") from None
    return fd

def tamano(fd: int) -> int:
    return os.lseek(fd, 0, os.SEEK_END)

def confirmar_destructivo(ruta: str) -> None:
    if input(f"Operación destructiva. Escribe '{ruta}' para continuar: ") != ruta:
        raise SystemExit("Cancelado por el usuario")
```

**Offset de sectores tras el header, y E/S real [PROBADO en `.img`]:**
```python
import header as hdr   # HEADER_AREA, SECTOR de header.py/crypt.py

def _pos(n: int) -> int:
    return hdr.HEADER_AREA + n * crypt.SECTOR

def escribir_sector(fd, master, n, datos) -> None:
    ct = crypt.cifrar_sector(master, n, datos)
    if os.pwrite(fd, ct, _pos(n)) != crypt.SECTOR:
        raise OSError("escritura incompleta")
    os.fsync(fd)

def leer_sector(fd, master, n) -> bytes:
    ct = os.pread(fd, crypt.SECTOR, _pos(n))
    if len(ct) != crypt.SECTOR:
        raise OSError("lectura incompleta (sector fuera del contenedor)")
    return crypt.descifrar_sector(master, n, ct)
```

**Modo de prueba (obligatorio antes de tocar un disco real):**
```python
def crear_img(ruta: str, n_sectores: int) -> None:
    with open(ruta, "wb") as f:
        f.truncate(hdr.HEADER_AREA + n_sectores * crypt.SECTOR)
```

---

## 7. `checker.py`

```python
import ctypes.util
import shutil
from importlib.metadata import version, PackageNotFoundError

def verificar_dependencias():
    faltan = []
    for paquete, minimo in [("cryptography", "44.0.0"), ("argon2-cffi", None)]:
        try:
            v = version(paquete)
        except PackageNotFoundError:
            faltan.append(paquete)
    # libsodium es del SISTEMA, no de pip — se verifica distinto:
    if ctypes.util.find_library("sodium") is None:
        faltan.append("libsodium (paquete de sistema, ej. libsodium23 en Ubuntu)")
    for programa in ("findmnt", "lsblk", "blockdev"):
        if shutil.which(programa) is None:
            faltan.append(programa)
    return faltan
```

**No instales nada en silencio [DISEÑO]:** reporta lo que falta, pide
confirmación explícita, y usa `[sys.executable, "-m", "pip", "install", ...]`
para paquetes de pip. Para paquetes de sistema (`apt`), pide confirmación y
recuerda que necesita root.

---

## Resumen: qué NO se mezcla entre archivos

| No hagas esto | Por qué |
|---|---|
| `_derivar_kek` en `session.py` | Es de `cryptography`, para el disco. Sesión usa `argon2-cffi` |
| `KEY_SIZE` distinto en `crypt.py` y `header.py` | Rompe el `unwrap`, probado en este chat |
| Password de sesión = key de `crypt.py` | Argon2 no es cifrado, `verify()` no revierte nada |
| Contraseña como argumento de CLI | Queda en el historial de bash y en `ps`; usa `getpass` |
| `_secretos`/handlers de señal sin ser variables globales | El handler de `signal` no puede recibir tus argumentos, solo ve globales |

---

## Fuentes citadas en este chat

- XTS: `cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/`
- Argon2id (cryptography): `cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/`
- keywrap: `cryptography.io/en/latest/hazmat/primitives/keywrap.html`
- argon2-cffi: `argon2-cffi.readthedocs.io` (howto + código fuente `_password_hasher.py`)
- libsodium memory management: `doc.libsodium.org/memory_management`
- ctypes argtypes/restype: `docs.python.org/3/library/ctypes.html`
- LUKS2 spec: `fossies.org/linux/cryptsetup/docs/on-disk-format-luks2.pdf`
- LUKS1 spec: `clemens.endorphin.org/LUKS-on-disk-format.pdf`
- XTS sin autenticación (doc de Go, misma propiedad del modo): `pkg.go.dev/golang.org/x/crypto/xts`
