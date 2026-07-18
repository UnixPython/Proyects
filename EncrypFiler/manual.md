# EncrypFiler — Manual de Uso

Herramienta de línea de comandos para Termux que permite registrar un usuario,
iniciar sesión, y cifrar/descifrar archivos con AES-GCM + scrypt.

## Requisitos

- Termux con Python instalado
- Acceso al almacenamiento externo habilitado (`termux-setup-storage`)

## 1. Instalación

Coloca todos estos archivos en la misma carpeta:

```
main.py
cli.py
core.py
auth.py
hashing.py
filemanager.py
setup_check.py
```

Instala Python y habilita el acceso al almacenamiento (solo la primera vez):

```bash
pkg install python
termux-setup-storage
```

Instala y verifica las dependencias con el script incluido:

```bash
python setup_check.py
```

Este script instala `pycryptodome` y `bcrypt` si faltan, y confirma que todos
los módulos del proyecto (`core.py`, `auth.py`, `hashing.py`, `filemanager.py`,
`cli.py`) importan correctamente. Si ves `Todo listo.` al final, ya puedes usar
el programa.

## 2. Registrar un usuario

Es el primer paso obligatorio — sin usuario registrado, el login del paso
siguiente nunca va a funcionar.

```bash
python main.py registrar
```

Se te pedirá, en este orden:
- `Escribe la ruta de la partición externa (ej: /storage/6177-1919):` → la
  ruta de tu SD/almacenamiento externo en Termux
- `New user:` → nombre de usuario
- `New password:` → contraseña (no se muestra en pantalla)

Puedes registrar varios usuarios repitiendo este comando con nombres distintos.

## 3. Cifrar un archivo

```bash
python main.py encriptar <archivo> --clave <clave>
```

Ejemplo:

```bash
python main.py encriptar documento.txt --clave miClaveSecreta
```

Antes de cifrar, el programa te pedirá tu usuario y contraseña (los que
registraste en el paso 2). Si el login es correcto:

- Se genera `documento.txt.enc`
- El archivo original (`documento.txt`) se **elimina**

> ⚠️ La `--clave` de cifrado es independiente del usuario/contraseña del
> login. Es la que realmente protege el contenido del archivo — **si la
> pierdes, no hay forma de recuperar el archivo**, ni siquiera con el
> usuario correcto.

## 4. Descifrar un archivo

```bash
python main.py desencriptar <archivo.enc> --clave <clave>
```

Ejemplo:

```bash
python main.py desencriptar documento.txt.enc --clave miClaveSecreta
```

Debes usar exactamente la misma `--clave` con la que se cifró. Si es
incorrecta, verás `Decryptacion invalida` y el archivo original **no** se
recupera ni se sobrescribe nada.

## 5. Intentos de login

Tienes **3 intentos** de usuario/contraseña por ejecución. Al tercer fallo,
el programa se cierra sin dejarte continuar:

```
Too many attempts.
Acceso denegado. No puedes acceder a los archivos.
```

Vuelve a correr el comando para intentar de nuevo.

## Resumen rápido de comandos

| Acción       | Comando                                                  |
|--------------|-----------------------------------------------------------|
| Verificar entorno | `python setup_check.py`                              |
| Registrar    | `python main.py registrar`                               |
| Cifrar       | `python main.py encriptar <archivo> --clave <clave>`      |
| Descifrar    | `python main.py desencriptar <archivo.enc> --clave <clave>` |

## Notas importantes

- Al iniciar cualquier comando, el programa te pedirá escribir la ruta de tu
  partición externa (SD), por ejemplo `/storage/6177-1919`. Ya no se detecta
  sola — escríbela exactamente como aparece en tu Termux. Si no sabes cuál
  es, revisa con `ls /storage/` en una terminal aparte, o usa la carpeta que
  te haya devuelto `termux-setup-storage`.
- Si escribes una ruta que no existe, verás un mensaje de error y el
  programa se detiene sin continuar.
- Al iniciar, se crea automáticamente la carpeta `EncrypFiler` dentro de la
  ruta que escribiste.
- Guarda tus claves de cifrado en un lugar seguro fuera del programa — no
  hay recuperación posible si las pierdes.

