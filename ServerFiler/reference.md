# Referencia: Servidor de transferencia de archivos en Python

Notas de estudio para construir un servidor propio (solo terminal) con auth, navegación de carpetas y multi-cliente.

---

## 1. `socket` — Base del servidor (TCP)

### Servidor (`tcp-server.py`)

```python
import socket

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8080
    totalclient = int(input('Enter number of clients: '))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(totalclient)

    connections = []
    print('Initiating clients')
    for i in range(totalclient):
        conn = sock.accept()
        connections.append(conn)
        print('Connected with client', i + 1)

    fileno = 0
    idx = 0
    for conn in connections:
        idx += 1
        data = conn[0].recv(1024).decode()

        if not data:
            continue

        filename = 'output' + str(fileno) + '.txt'
        fileno += 1
        fo = open(filename, "w")
        while data:
            if not data:
                break
            fo.write(data)
            data = conn[0].recv(1024).decode()

        print('Receiving file from client', idx)
        print('Received successfully! New filename is:', filename)
        fo.close()

    for conn in connections:
        conn[0].close()
```

### Cliente (`tcp-client.py`)

```python
import socket

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8080

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    while True:
        filename = input('Input filename you want to send: ')
        try:
            fi = open(filename, "r")
            data = fi.read()
            if not data:
                break
            while data:
                sock.send(str(data).encode())
                data = fi.read()
            fi.close()
        except IOError:
            print('You entered an invalid filename! Please enter a valid name')
```

**⚠️ Problemas de este ejemplo para tu proyecto (no copiar literal):**
- Usa `.decode()`/texto → rompe con archivos binarios (imágenes, zips). Hay que trabajar en bytes crudos.
- No manda el tamaño del archivo antes de los datos → no se sabe con precisión cuándo parar de leer. Hay que rediseñar el protocolo para mandar tamaño primero.
- Espera a que TODOS los clientes se conecten antes de procesar → lo resuelve `threading` (ver sección 3).

---

## 2. `os` — Listar archivos, carpetas y rutas seguras

| Función | Para qué sirve |
|---|---|
| `os.listdir()` | Listar archivos (comando `LIST`) |
| `os.path.isdir()` | Saber si una entrada es carpeta |
| `os.path.isfile()` | Saber si una entrada es archivo |
| `os.path.join()` | Construir rutas correctamente |
| `os.makedirs()` | Crear carpetas (comando `MKDIR`) |
| `os.path.getsize()` | Obtener tamaño antes de enviar un archivo |
| `os.path.abspath()` | Obtener la ruta absoluta |
| `os.path.commonpath()` | Evitar ataques de Path Traversal |

### `os.listdir(path)`
```python
import os
archivos = os.listdir("docs")
print(archivos)
# ['foto.png', 'notas.txt', 'imagenes']
```

### `os.path.isdir(path)` / `os.path.isfile(path)`
```python
print(os.path.isdir("docs"))          # True
print(os.path.isfile("docs/notas.txt"))  # True
```

### `os.path.join(carpeta, archivo)`
```python
ruta = os.path.join("docs", "notas.txt")
print(ruta)
# Linux:   docs/notas.txt
# Windows: docs\notas.txt
```
Nunca hagas `carpeta + "/" + archivo` a mano.

### `os.makedirs(path)`
```python
os.makedirs("docs/python/socket")
# docs/python/socket/ creado, incluyendo carpetas intermedias
```

### `os.path.getsize(path)`
```python
tam = os.path.getsize("video.mp4")
print(tam)  # 18452341
```
Uso en el protocolo: mandar primero el tamaño del archivo, luego los datos.

### `os.path.abspath(path)`
```python
print(os.path.abspath("docs"))
# /home/usuario/docs
```

### `os.path.commonpath(paths)` — protección contra Path Traversal
```python
base = "/srv/ftp"
archivo = "/srv/ftp/docs/test.txt"
print(os.path.commonpath([base, archivo]))
# /srv/ftp
```

### Ejemplo combinado: listar con tipo y chequeo de ruta segura
```python
import os

carpeta = "/home/tu_usuario/compartido"

for item in os.listdir(carpeta):
    ruta_completa = os.path.join(carpeta, item)
    if os.path.isdir(ruta_completa):
        print(f"[DIR]  {item}")
    else:
        tamano = os.path.getsize(ruta_completa)
        print(f"[FILE] {item} - {tamano} bytes")

def es_ruta_segura(base, ruta_pedida):
    base = os.path.abspath(base)
    objetivo = os.path.abspath(os.path.join(base, ruta_pedida))
    return objetivo.startswith(base)

print(es_ruta_segura(carpeta, "archivo.txt"))       # True
print(es_ruta_segura(carpeta, "../../etc/passwd"))  # False
```

---

## 3. `hashlib` — Autenticación con salt

### Hash simple
```python
import hashlib
texto = "hola"
hash_valor = hashlib.sha256(texto.encode()).hexdigest()
print(hash_valor)
# 2cf24dba5fb0...
```

### Con salt (recomendado)
Un **salt** es un texto aleatorio agregado a la contraseña antes de hashear. Evita ataques con rainbow tables y que dos usuarios con la misma clave tengan el mismo hash. Nunca guardes `SHA256(password)` solo.

```python
import hashlib

salt = "MiSalt"
password = "123456"
hash_valor = hashlib.sha256((salt + password).encode()).hexdigest()
```

### Ejemplo completo: crear usuario y verificar login
```python
import hashlib
import os

def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()
    hash_resultado = hashlib.sha256((salt + password).encode()).hexdigest()
    return salt, hash_resultado

def verificar_password(password_intento, salt_guardado, hash_guardado):
    _, hash_intento = hash_password(password_intento, salt_guardado)
    return hash_intento == hash_guardado

# Al crear el usuario
salt, hash_guardado = hash_password("miClave123")
print("Guardar en archivo de usuarios:", salt, hash_guardado)

# Al hacer login
print(verificar_password("miClave123", salt, hash_guardado))  # True
print(verificar_password("claveMala", salt, hash_guardado))   # False
```

---

## 4. `threading` — Atender varios clientes/archivos a la vez

### Crear e iniciar un hilo
```python
import threading

def saludar(nombre):
    print("Hola", nombre)

hilo = threading.Thread(target=saludar, args=("Ana",))
hilo.start()
# Hola Ana
```

### Patrón típico en un servidor de sockets
```python
import threading

while True:
    conn, addr = servidor.accept()
    threading.Thread(target=atender_cliente, args=(conn,)).start()
```
Cada cliente se atiende en un hilo distinto, sin bloquear al servidor mientras otro cliente transfiere un archivo.

### Ejemplo aislado (simulado, sin sockets)
```python
import threading
import time

def atender_cliente(id_cliente):
    print(f"Cliente {id_cliente} conectado")
    time.sleep(2)  # simula tiempo transfiriendo un archivo
    print(f"Cliente {id_cliente} terminó su transferencia")

# Con threading (corren en paralelo)
hilos = []
for i in range(1, 4):
    hilo = threading.Thread(target=atender_cliente, args=(i,))
    hilo.start()
    hilos.append(hilo)

for hilo in hilos:
    hilo.join()  # esperar a que todos terminen antes de seguir

print("Todos los clientes fueron atendidos")
```

---

## 5. Ruta de construcción sugerida

1. Servidor socket básico: acepta conexión y responde "hola".
2. Servidor que lee un comando de texto y responde (diseñar protocolo propio: `LOGIN`, `LIST`, `GET`, `PUT`).
3. Comando `LIST` usando `os.listdir` + `os.path.isdir`.
4. Comando `GET`: mandar tamaño con `os.path.getsize`, luego los bytes en chunks.
5. Comando `PUT`: recibir tamaño primero, luego leer en loop hasta completarlo (bytes, no texto).
6. `LOGIN` con `hashlib` + salt, usuarios en un archivo de texto o SQLite.
7. `threading.Thread` por cada conexión aceptada, para manejar varios clientes en paralelo.
8. Validar cada ruta pedida con `os.path.abspath` + `commonpath` antes de leer/escribir (anti path traversal).

**Consejo directo:** no mezcles las 4 piezas hasta que cada una funcione aislada como en los ejemplos de arriba. El socket sin auth ni threading primero, y le vas agregando capas.
