ENCRYPTPART - ESTRUCTURA DEL PROYECTO
=====================================
Leyenda:  [DOC] = viene de documentacion oficial (ver FUENTES)
          [DISENO] = decision de diseno (LUKS / criterio propio)
          [VERIFICAR] = de conocimiento general, confirmar en man/docs

------------------------------------------------------------------
0. DECISIONES FIJAS (no cambiar sin motivo)
------------------------------------------------------------------
- Cifrado de sectores: AES-XTS, sin padding.                      [DOC]
- Key de datos (master key): 64 bytes = AES-256-XTS. Con 32 es AES-128. [DOC]
- Tweak: 16 bytes derivados del numero de sector (little-endian).
  Nunca aleatorio, nunca el mismo para sectores distintos.        [DOC]+[DISENO]
- KDF: Argon2id (cryptography >= 44.0.0), salt >= 16 bytes.       [DOC]
- Proteccion de la master key: aes_key_wrap / aes_key_unwrap.     [DOC]
- Aleatoriedad: SOLO secrets.token_bytes() en todo el proyecto.   [DISENO]
- Contrasena: nunca en archivo ni en codigo. Solo getpass.        [DISENO]
- Contrasena de sesion y de disco: independientes, salts distintos. [DISENO]
- Tamano de sector fijo (512 o 4096), una constante en un solo lugar. [DISENO]
- Nunca loguear: contrasenas, keys, KEK, plaintext. Solo fingerprints.  [DISENO]

LIMITE DE ALCANCE (importante):
- Python en userland puede leer/escribir sectores cifrados, pero NO
  monta un filesystem de forma transparente. Eso requiere dm-crypt,
  FUSE o NBD. La v1 debe ser: cifrar / descifrar el contenedor .enc
  o la particion completa, sector a sector, en modo offline.      [VERIFICAR]
- Cifrar una particion que YA tiene datos es peligroso: el header
  ocupa espacio al inicio y una interrupcion puede corromper todo.
  Empezar solo con .img o particiones vacias.                     [DISENO]

------------------------------------------------------------------
1. exceptions.py
------------------------------------------------------------------
Responsabilidad: errores propios, logging y politica ante fallos.
- Clase base EncryptPartError y derivadas:
    InvalidPasswordError   (envuelve keywrap.InvalidUnwrap)
    CorruptHeaderError     (magic/version/tamano invalido)
    InvalidKeySizeError    (key distinta de 64 bytes)
    InvalidSectorSizeError (dato distinto del tamano de sector)
    NotRootError           DeviceBusyError     DeviceMountedError
    MissingDependencyError
- Logging con el modulo logging de la stdlib: niveles, archivo + consola.
  Regla dura: ningun secreto en logs ni en mensajes de excepcion.
- Politica de errores (fail closed):
    * Ante duda, abortar; nunca continuar con datos a medias.
    * Codigos de salida distintos por tipo de error (sys.exit(n)).
    * Sin stack traces al usuario final; detalle solo en el log.
    * Si tu detector de bugs (checks.py) ya cubre esto, reutilizarlo.

------------------------------------------------------------------
2. crypt.py  (funciones puras: bytes entran, bytes salen)
------------------------------------------------------------------
Responsabilidad: cifrar/descifrar un sector y calcular fingerprints.
- cifrar_sector(key, n, datos) / descifrar_sector(key, n, datos)
    Cipher(algorithms.AES(key), modes.XTS(tweak))                 [DOC]
    Validar len(key) == 64 y len(datos) == SECTOR.
- fingerprint(datos) con hashlib.sha256. Sirve para IDENTIFICAR
  (por ejemplo el header), no como control de seguridad.
    Si quieres integridad real: hmac.new(...) y hmac.compare_digest,
    nunca comparar con ==.
- NO va aqui: contrasenas, Argon2, wrap, header, archivos, sesion.
- Stateless: no guarda nada entre llamadas.

------------------------------------------------------------------
2b. header.py  (NUEVO, recomendado: aqui va "creacion del .enc")
------------------------------------------------------------------
Responsabilidad: crear/abrir el volumen y manejar el header.
- crear_volumen(password): master = token_bytes(64), salt = token_bytes(16),
  KEK = Argon2id(...).derive(password), wrapped = aes_key_wrap(KEK, master). [DOC]
- abrir_volumen(password, header): recalcula KEK y hace aes_key_unwrap;
  InvalidUnwrap => InvalidPasswordError.                          [DOC]
- Header binario con struct, SIEMPRE con prefijo de orden ">" (big-endian,
  sin alineacion nativa). LUKS2 usa big-endian.                   [DOC LUKS2]
    campos: magic | version | salt | params Argon2 (t, m, p) | wrapped
    + copia de respaldo del header (LUKS2 guarda un secundario).  [DOC LUKS2]
- El header NO es secreto pero es visible: no meter nada que ayude a
  atacar los datos.                                               [DOC LUKS2]
- Offset de datos = tamano del header (dato n va en HEADER_SIZE + n*SECTOR).
- Parametros Argon2: medir en tu maquina (python -m argon2 de argon2-cffi
  sirve de referencia para tiempos).

------------------------------------------------------------------
3. memzo.py
------------------------------------------------------------------
Responsabilidad: proteger secretos en memoria (interpretacion de
"bloqueo en estado 0" = bloquear memoria y poner a cero al terminar).
- Guardar keys en bytearray (los bytes son inmutables y no se pueden
  borrar). Poner a cero con ctypes.memset o un bucle. Es mejor esfuerzo:
  Python y la libreria pueden dejar copias internas.              [VERIFICAR]
- Bloquear paginas en RAM con mlock via ctypes (libc). Puede exigir
  root o subir RLIMIT_MEMLOCK.                                    [VERIFICAR]
- Desactivar core dumps: resource.setrlimit(RLIMIT_CORE, (0, 0)). [VERIFICAR]
- SIGINT / SIGTERM: signal.signal(...) con un handler que pone a cero
  las keys, cierra el fd, libera el flock y sale. Tambien try/finally
  y atexit. SIGKILL no se puede capturar.                         [VERIFICAR]
- Registro de lo que se bloqueo, para limpiarlo todo al final.

------------------------------------------------------------------
4. session.py  (fase tardia, se dejo de lado a proposito)
------------------------------------------------------------------
- Registro e inicio de sesion con argon2-cffi PasswordHasher:
  hash(), verify() (lanza VerifyMismatchError si no coincide),
  check_needs_rehash().                                           [DOC argon2-cffi]
- Perfiles RFC 9106 (LOW_MEMORY es el razonable; HIGH_MEMORY pide 2 GiB).
- Logging en tiempo real de eventos de sesion (sin contrasenas).
- Independiente del disco: otra contrasena o al menos otro salt.
- Excepciones a manejar: VerifyMismatchError, VerificationError,
  InvalidHashError.

------------------------------------------------------------------
5. commands.py
------------------------------------------------------------------
- argparse con subparsers (dest="accion"): por ejemplo
  encriptar / desencriptar / info / verificar, con "objetivo" como argumento.
- Ejemplos de uso en el epilog del parser o traidos de examples.py.
- Solo parsea y despacha: la logica vive en los otros modulos.
- La contrasena NUNCA como argumento de linea de comandos (queda en el
  historial y en ps); siempre getpass.

------------------------------------------------------------------
6. disks.py
------------------------------------------------------------------
- Root: os.geteuid() == 0, si no => NotRootError.
- Abrir con os.open(ruta, os.O_RDWR); leer/escribir con os.pread /
  os.pwrite (offset explicito) y os.fsync tras escribir.          [VERIFICAR]
- Bloqueo exclusivo: fcntl.flock(fd, LOCK_EX | LOCK_NB). Es advisory:
  solo protege contra procesos que tambien lo respetan.
- Verificar que NO esta montada: subprocess.run(["findmnt", ruta]) o
  lsblk -J (JSON). Rechazar si esta montada.
- Tamano: os.lseek(fd, 0, os.SEEK_END). Tamano de sector:
  blockdev --getss.                                               [VERIFICAR]
- Modo de prueba: operar sobre un .img. Confirmacion explicita
  (escribir el nombre del dispositivo) antes de cualquier operacion
  destructiva. No tocar nunca el disco donde vive "/".

------------------------------------------------------------------
7. checker.py
------------------------------------------------------------------
- Ejecutar tests unitarios (unittest o pytest) y reportar.
- Verificar que existen los archivos del proyecto.
- Dependencias: cryptography >= 44.0.0, argon2-cffi. Comprobar version
  con importlib.metadata.
- Programas Linux: lsblk, findmnt, blockdev (shutil.which).
- Instalacion: NO instalar en silencio. Reportar lo que falta, pedir
  confirmacion, y usar [sys.executable, "-m", "pip", "install", ...].
  apt requiere root: solo con confirmacion explicita.
- Tests minimos que debe correr:
    * descifrar(cifrar(x)) == x
    * mismo texto en sectores distintos => ciphertext distinto
    * key de tamano incorrecto => error
    * contrasena incorrecta => InvalidPasswordError
    * pack/unpack del header simetrico
    * vectores de prueba conocidos de XTS (IEEE 1619)             [VERIFICAR]

------------------------------------------------------------------
8. examples.py
------------------------------------------------------------------
- Ejemplos genericos por comando; el epilog de argparse los reutiliza.
- Un ejemplo completo sobre un .img de prueba, sin dispositivos reales.

------------------------------------------------------------------
9. main.py
------------------------------------------------------------------
- Punto de entrada: configura logging, instala los handlers de senales
  (memzo), corre el checker si corresponde, parsea comandos y despacha.
- Pide la contrasena con getpass solo cuando hace falta.

------------------------------------------------------------------
ORDEN DE CONSTRUCCION SUGERIDO
------------------------------------------------------------------
1) exceptions.py + crypt.py + tests sobre un .img con key fija.
2) header.py (crear/abrir volumen, contrasena incorrecta).
3) disks.py primero con .img, despues con dispositivo real vacio.
4) memzo.py (ceros, mlock, senales).
5) commands.py + main.py + examples.py.
6) checker.py.
7) session.py al final.

------------------------------------------------------------------
NOTAS SOBRE TU ARCHIVO DE SNIPPETS (corregir)
------------------------------------------------------------------
- Seccion AES-XTS: NO usar ese ejemplo para disco. Tiene padding PKCS7
  (XTS no lo usa), key de 32 bytes (es AES-128), iv aleatorio (debe ser
  el numero de sector) y os.urandom en vez de secrets.
- struct: "4sI16s" sin prefijo usa orden y alineacion nativos. Usar ">4sI16s".
- Fernet / MultiFernet: sirven para mensajes o archivos pequenos, no para
  sectores. Puedes dejarlos como referencia, no van en este proyecto.
- Faltan en el archivo: keywrap (wrap/unwrap/InvalidUnwrap), mlock,
  signal, pread/pwrite, tests.
- memory_cost de Argon2: en argon2-cffi son KiB (65536 = 64 MiB). El
  ejemplo de Fernet usa 2**21 (2 GiB): puede saturar una maquina modesta.

------------------------------------------------------------------
FUENTES
------------------------------------------------------------------
XTS:      https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/
Argon2id: https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/
keywrap:  https://cryptography.io/en/latest/hazmat/primitives/keywrap.html
LUKS2:    https://fossies.org/linux/cryptsetup/docs/on-disk-format-luks2.pdf
LUKS1:    https://clemens.endorphin.org/LUKS-on-disk-format.pdf
XTS sin autenticacion (doc de Go, misma propiedad del modo):
          https://pkg.go.dev/golang.org/x/crypto/xts
Pendiente de leer por tu cuenta ([VERIFICAR]): man 2 mlock, man 7 signal,
docs de Python: signal, ctypes, resource, os (pread/pwrite), struct.
