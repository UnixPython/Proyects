**Librerías por archivo — LockerPass**

**1. `exceptions.py`**
- Nada externo. Solo `Exception` nativo de Python.
- Docs: https://docs.python.org/3/tutorial/errors.html

**2. `crypt.py`**
- `argon2-cffi` — derivación de clave (Argon2id)
  Docs: https://argon2-cffi.readthedocs.io/en/stable/
- `cryptography` (módulo `cryptography.hazmat.primitives.ciphers.aead`) — AES-256-GCM
  Docs: https://cryptography.io/en/latest/hazmat/primitives/aead/
- `secrets` (nativo) — generación de nonce/salt
  Docs: https://docs.python.org/3/library/secrets.html

**3. `memory.py`**
- `ctypes` (nativo) — llamadas a `libc` para `mlockall`/`munlockall`
  Docs: https://docs.python.org/3/library/ctypes.html
- `mmap` (nativo) — buffers de memoria anónimos
  Docs: https://docs.python.org/3/library/mmap.html
- Referencia hombre de Linux para `mlockall` (no es Python pero es la fuente de verdad de la syscall):
  https://man7.org/linux/man-pages/man2/mlock.2.html

**4. `generate.py`**
- `secrets` (nativo) — nunca `random` para esto
  Docs: https://docs.python.org/3/library/secrets.html
- `string` (nativo) — conjuntos de caracteres (letras, dígitos, puntuación)
  Docs: https://docs.python.org/3/library/string.html

**5. `manager.py`**
- `json` (nativo) — serialización del formato de vault
  Docs: https://docs.python.org/3/library/json.html
- `pathlib` (nativo) — manejo de rutas de archivo del vault
  Docs: https://docs.python.org/3/library/pathlib.html
- `base64` (nativo) — codificar bytes cifrados para guardar en JSON/texto
  Docs: https://docs.python.org/3/library/base64.html
- Importa internamente `crypt.py`, `memory.py`, `exceptions.py` — no librerías externas nuevas.

**6. `autolock.py`**
- `signal` (nativo) — manejo de SIGINT/SIGTERM
  Docs: https://docs.python.org/3/library/signal.html
- `threading` (nativo) — temporizador de inactividad sin bloquear el programa principal
  Docs: https://docs.python.org/3/library/threading.html
- `pyperclip` (externa, opcional) — limpieza de portapapeles multiplataforma
  Docs: https://pypi.org/project/pyperclip/

**Instalación de las dos únicas dependencias externas reales:**
```
pip install argon2-cffi cryptography
```
(`pyperclip` solo si decides que el auto-clear de portapapeles vale la complejidad extra — es opcional, no crítico para la seguridad del vault en sí).
