**Resumen funcional de cada archivo — LockerPass**

**1. `exceptions.py`**
Define todas las excepciones custom del proyecto. No contiene lógica, solo clases. Cada excepción representa una categoría de fallo (derivación de clave, cifrado, descifrado, integridad, memoria, vault). Es la base que importan todos los demás archivos.

**2. `crypt.py`**
El núcleo criptográfico. Contiene:
- Función que deriva una clave desde el maestro usando Argon2id (recibe maestro + salt, retorna clave).
- Función que cifra un dato con AES-256-GCM (recibe clave + plaintext, genera nonce único, retorna ciphertext + tag).
- Función que descifra (recibe clave + ciphertext + nonce + tag, verifica integridad, retorna plaintext o lanza `IntegrityError`/`DecryptionError`).
No sabe nada de archivos, vault ni interfaz — solo transforma bytes.

**3. `memory.py`**
Manejo seguro de memoria. Contiene:
- Función para bloquear páginas de memoria (`mlockall`) y evitar swap.
- Función para desbloquear (`munlockall`).
- Función para zerar explícitamente un buffer antes de liberarlo (esto es lo que faltaba en tu versión anterior).
No maneja criptografía ni vault, solo el ciclo de vida de la memoria sensible.

**4. `generate.py`**
Generador de contraseñas. Contiene:
- Función que genera contraseñas aleatorias criptográficamente seguras usando `secrets` (no `random`).
- Parámetros configurables: longitud, si incluye símbolos, mayúsculas, números.
No depende de cifrado ni vault, es una utilidad aislada.

**5. `manager.py`**
El orquestador central. Contiene:
- Estructura del vault (versión, salt, nonce, entradas cifradas).
- Leer el vault.enc por el usuario
- Función para agregar/editar/eliminar una entrada de vault.enc (usa `crypt.py` para cifrar cada campo).
- Función para cargar el vault.enc desde disco y descifrarlo (usa `crypt.py` + `memory.py`).
- Función para guardar el vault cifrado a disco.
- Manejo de errores de vault corrupto o versión desconocida (usa `exceptions.py`).
Es el que junta todas las piezas anteriores en un flujo real de "guardar/leer contraseñas".

**6. `autolock.py`**
Control de sesión. Contiene:
- Temporizador que bloquea el vault tras N minutos de inactividad (llama a `manager.py` para cerrar sesión y limpiar memoria vía `memory.py`).
- Función que limpia el portapapeles automáticamente tras copiar una contraseña.
- Manejo de señales (SIGINT/SIGTERM) para asegurar limpieza al cerrar el programa abruptamente — esta vez limpiando el buffer real, no uno decorativo como antes.

**7. 'vault.py'**
- Se genera archivo .enc
- Se almazena las contraseñas dentro del enc
- Contiene inicio de session usando crypt.py para registrarse un usario. Se integrara la session con manager.py

8. commander.py
- Uso de argsparse comandos
- Manual de uso
- Integrar lockrr --help para ver ejemplos

9. Main.py
- Integracion de todos los archivos
- instalar librerias si no andan instaladas
- Verificación

Ese es el mapa completo. Cuando quieras arrancar, empezamos por `exceptions.py`.
