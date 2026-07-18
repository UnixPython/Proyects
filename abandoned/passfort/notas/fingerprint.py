## Fragmentos para `fingerprint.py`

---

### Fragmento 1 — `uuid.getnode()`

```python
import uuid

# Devuelve la MAC address como un entero
mac_int = uuid.getnode()

# Lo convertís a string para poder usarlo
mac_str = str(mac_int)

print(mac_str)  # "140234698456231"
```

**Adaptalo:** en tu proyecto no vas a printearlo, lo vas a guardar en una variable para combinarlo con otros valores.

---

### Fragmento 2 — `platform`

```python
import platform

cpu   = platform.processor()   # "Intel64 Family 6..."
arch  = platform.machine()     # "x86_64"
host  = platform.node()        # "mi-pc"

print(cpu, arch, host)
```

**Adaptalo:** combiná los tres en un solo string con un separador, por ejemplo `|`.

---

### Fragmento 3 — `subprocess` con fallback

```python
import subprocess

try:
    resultado = subprocess.check_output(
        ["cat", "/etc/machine-id"],
        stderr=subprocess.DEVNULL
    ).decode().strip()

except subprocess.CalledProcessError:
    resultado = "unknown"

print(resultado)  # "a3f2c1d4e5b6..."
```

**Adaptalo:** hacé lo mismo para `lsblk -dno SERIAL`. Cambiá el comando dentro de la lista y el fallback si falla.

---

### Fragmento 4 — combinar strings

```python
partes = ["valor1", "valor2", "valor3"]

combinado = "|".join(partes)

print(combinado)  # "valor1|valor2|valor3"
```

**Adaptalo:** en lugar de strings hardcodeados, usá las variables que recolectaste arriba.

---

### Fragmento 5 — hashear con `hashlib`

```python
import hashlib

dato = "texto-a-hashear"

resultado = hashlib.sha256(dato.encode()).hexdigest()

print(resultado)  # "2cf24dba5fb0a3..."
```

**Adaptalo:** el `dato` va a ser tu string combinado del fragmento 4. El `.hexdigest()` te da un string hexadecimal de 64 chars — ese es tu fingerprint final.

---

Con esos 5 fragmentos podés armar `fingerprint.py` completo. La función principal debería llamarse `get_fingerprint()` y devolver el hash final.
