# Módulo `secrets` en Python — Generación de Contraseñas y Tokens

## 1. Generación de Contraseñas Alfanuméricas

```python
import string
import secrets

# Se definen los caracteres permitidos: letras y números
alfabeto = string.ascii_letters + string.digits

# Se eligen 8 caracteres al azar y se unen en una cadena
password = ''.join(secrets.choice(alfabeto) for i in range(8))
```

## 2. Contraseñas con Requisitos de Complejidad

```python
import string
import secrets

alfabeto = string.ascii_letters + string.digits
while True:
    password = ''.join(secrets.choice(alfabeto) for i in range(10))
    # Valida que tenga al menos una minúscula, una mayúscula y tres dígitos
    if (any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3):
        break
```

## 3. Generación de Frases de Seguridad (Passphrases)

```python
import secrets

# Suponiendo un archivo de palabras en el sistema
with open('/usr/share/dict/words') as f:
    palabras = [word.strip() for word in f]
    # Selecciona 4 palabras al azar y las une con espacios
    frase = ' '.join(secrets.choice(palabras) for i in range(4))
```

## 4. Generación de Tokens de Seguridad

```python
token_reset = secrets.token_urlsafe(32)  # Genera un token seguro de 32 bytes
url = 'https://example.com/reset=' + token_reset
```

- `token_bytes(n)`: Devuelve una cadena de bytes aleatorios.
- `token_hex(n)`: Devuelve una cadena en formato hexadecimal.
- `token_urlsafe(n)`: Devuelve una cadena codificada en Base64 segura para URLs.

## 5. Comparación Segura de Secretos

```python
import secrets

# Compara dos cadenas en tiempo constante para mayor seguridad
es_valido = secrets.compare_digest("token_esperado", "token_recibido")
```

## 6. Formateo y Plantillas de Cadenas

```python
from string import Template

# Uso de plantillas para mensajes de seguridad
t = Template('Hola $usuario, tu token ha sido generado.')
mensaje = t.substitute(usuario='Admin')
```

- `string.Template`: sustituciones simples mediante el signo `$`.
- `str.format()`: formateo complejo (binario, hex, etc.).
- `string.capwords()`: capitaliza cada palabra de una cadena.

## 7. `secrets.randbelow(n)` — Índices y PINs numéricos

```python
import secrets

# PIN numérico de 6 dígitos
pin = ''.join(str(secrets.randbelow(10)) for _ in range(6))
```

## 8. `secrets.SystemRandom` — API tipo `random`, criptográficamente segura

```python
import secrets

sr = secrets.SystemRandom()
sr.shuffle(lista_de_palabras)      # shuffle seguro
valor = sr.randint(1, 100)         # randint seguro
```

## 9. Longitud mínima recomendada en tokens

```python
token = secrets.token_hex(32)  # 64 caracteres hex, 256 bits de entropía
```

Documentación oficial recomienda un mínimo de 32 bytes (256 bits) para tokens de sesión o reset de contraseña.

---

## Tabla comparativa rápida

| Método | Salida | Uso típico |
|---|---|---|
| `token_bytes(n)` | `bytes` | Claves criptográficas crudas |
| `token_hex(n)` | `str` hex | IDs de sesión, API keys |
| `token_urlsafe(n)` | `str` base64 URL-safe | Links de reset, verificación email |
| `randbelow(n)` | `int` | PINs, índices |
| `choice(seq)` | elemento | Contraseñas, passphrases |
| `SystemRandom` | objeto | Reemplazo seguro de `random` (shuffle, randint, sample) |
| `compare_digest(a,b)` | `bool` | Validación anti-timing attack |

**Documentación oficial:** https://docs.python.org/3/library/secrets.html
