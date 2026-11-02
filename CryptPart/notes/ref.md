# EncryptPart — Referencias de librerías y buenas prácticas

Documento de estudio. No contiene código de solución — solo enlaces, interpretación breve y patrones a estudiar por tu cuenta, según el método POP.

---

## 1. `cryptography` (pyca) — núcleo criptográfico

- Sitio/docs: https://cryptography.io/
- Cifrado simétrico (incluye modo XTS, el que necesitás para bloques de disco):
  https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/
- Funciones de derivación de clave (KDFs, alternativa a argon2 si en algún punto necesitás scrypt):
  https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/

**Qué leer primero:** la sección "hazmat" (bajo nivel) es la que usás para disco. La API alta (`Fernet`) no soporta XTS ni acceso por bloque — solo sirve para blobs completos, no para dispositivos.

---

## 2. `argon2-cffi` — derivación de clave desde password

- Docs: https://argon2-cffi.readthedocs.io/
- Implementación estándar de Argon2, ganador de la Password Hashing Competition, con API de alto nivel `PasswordHasher` para hashear y verificar contraseñas.

**Patrón a estudiar:** `check_needs_rehash()` — permite subir el costo del KDF con el tiempo sin romper compatibilidad con hashes ya generados. Es el patrón correcto para un proyecto pensado para durar años.

---

## 3. `pyudev` — detección de dispositivos/particiones

- Docs: https://pyudev.readthedocs.io/
- Binding puro en Python para libudev. Permite enumerar dispositivos, consultar propiedades/atributos, o monitorearlos (incluyendo monitoreo asíncrono con threads).
- Objeto central: `Context` — necesario para casi cualquier operación. Con él enumerás dispositivos filtrados por subsistema.

**Patrón a estudiar:** filtrar por `subsystem='block', DEVTYPE='partition'` — es exactamente lo que necesitás para tu paso de "detectando dispositivos/registro".

---

## 4. `psutil` — verificación de montaje

- Docs: https://psutil.readthedocs.io/
- Método clave: `psutil.disk_partitions()` — devuelve lo que está montado actualmente. Compará contra esto antes de abrir el device node, nunca cifres algo montado.

---

## 5. Librerías estándar (stdlib)

| Librería | Uso en tu proyecto | Docs |
|---|---|---|
| `os` | Abrir el device node en binario, flags `O_DIRECT`/`O_SYNC` | https://docs.python.org/3/library/os.html |
| `fcntl` | Control fino de flags de archivo/dispositivo en Linux | https://docs.python.org/3/library/fcntl.html |
| `hashlib` | Fingerprint SHA256 del sistema, hash de verificación | https://docs.python.org/3/library/hashlib.html |
| `hmac` | Firmar el header (salt/IV/fingerprint), no solo cifrarlo | https://docs.python.org/3/library/hmac.html |
| `struct` | Empaquetar el header binario de tamaño fijo | https://docs.python.org/3/library/struct.html |
| `secrets` | Generar salt/IV/nonce — nunca `random` | https://docs.python.org/3/library/secrets.html |
| `json` | Solo para el contenido de `register.enc` ya desencriptado en memoria, no para el header de la partición | https://docs.python.org/3/library/json.html |

---

## 6. Proyectos reales con patrones análogos

pyluks: https://github.com/Laniakea-elixir-it/pyluks

fbind (Android, pero el flujo de detección/montaje de volúmenes LUKS/LUKS2 es igual de aplicable): https://github.com/VR-25/fbind

buscar mas: https://repos.ecosyste.ms/topics/cryptsetup

---

## 7. Buenas prácticas — resumen final

1. **KDF con memoria alta** (Argon2id, no PBKDF2) para todo lo que derive de una contraseña humana.
2. **XTS, no CBC/GCM**, para cifrado de bloques de disco — acceso aleatorio por sector sin romper cifrado de bloques vecinos.
3. **Nunca reutilizar IV/nonce** — generar con `secrets`, nunca `random` ni derivado de timestamp.
4. **Autenticar el header con HMAC**, no solo cifrarlo — si alguien lo modifica bit a bit, tenés que poder detectarlo antes de intentar desencriptar el resto.
5. **Verificar desmontaje** antes de tocar el device node — cifrar una partición montada corrompe el filesystem activo.
6. **Nunca loguear la contraseña ni el password de partición** en texto plano, ni siquiera en modo debug.
7. **Zeroizar la clave en memoria** después de usarla, en la medida que Python lo permite (no hay garantías fuertes como en C, pero evitá dejarla viva en variables de larga duración).

---

*Documento de estudio para el proyecto EncryptPart. Definí el diseño (paso 1 del método POP) antes de escribir la primera línea de implementación real.*
