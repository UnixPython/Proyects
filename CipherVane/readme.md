# CipherVane: Arquitectura de Túnel Seguro mTLS y Primitivas Criptográficas en Curvas Elípticas

## 1. Visión General del Sistema

CipherVane es una infraestructura de tunelización segura y gestión de identidades criptográficas construida sobre la suite de curvas elípticas SECP256R1 (NIST P-256). El proyecto implementa una Cadena de Confianza de Infraestructura de Clave Pública (PKI) jerárquica de dos niveles (Root CA e Intermediate CA), mecanismos de verificación de firmas digitales ECDSA, negociación de claves de sesión de Forward Secrecy mediante ECDHE con KDF, y un túnel de transporte seguro multiplexado basado en Mutua Autenticación TLS (mTLS 1.3).

El sistema se divide en tres componentes primarios:

1. **Capa Criptográfica Directa (`capa_cripto`):** Implementación de operaciones aritméticas en curvas elípticas, emisión/verificación de certificados X.509 y derivación de material de clave.
2. **Capa de Red y Tunelización (`capa_red`):** Abstracción de sockets SSL/TLS con validación estricta de extensiones (`SERVER_AUTH` / `CLIENT_AUTH`) y multiplexado I/O no bloqueante.
3. **Capa de Aplicación y Orquestación (`capa_app`):** Gestión de configuración, logs estructurados de auditoría y manejo global de excepciones.

---

## 2. Fundamentos Matemáticos y Criptográficos

El sistema basa toda su seguridad asimétrica en la dureza del Problema del Logaritmo Discreto en Grupos de Puntos de Curva Elíptica (ECDLP).

### 2.1 Dominio de la Curva SECP256R1 (NIST P-256)

La curva está definida sobre el cuerpo finito $\mathbb{F}_p$, donde el primo $p$ es:

$$p = 2^{256} - 2^{224} + 2^{192} + 2^{96} - 1$$

La ecuación de Weierstrass corta que rige el grupo de puntos $E(\mathbb{F}_p)$ es:

$$y^2 \equiv x^3 + a x + b \pmod p$$

donde los coeficientes y el orden del grupo $n$ son:

$$a = -3$$

$$b = \text{0x5AC635D8 AA3A93E7 B3EBBD55 769886BC 651D06B0 CC53B0F6 3BCE3C3E 27D2604B}$$

$$n = \text{0xFFFFFFFF 00000001 00000000 00000000 00000000 FFFFFFFF FFFFFFFF FFFFFFFF}$$

Un punto generador $G = (x_G, y_G)$ de orden $n$ define el subgrupo principal. La clave privada se selecciona como un escalar escalar escalar aleatorio $d \in [1, n-1]$, y la clave pública equivalente es el punto $Q$:

$$Q = d \cdot G$$

---

### 2.2 Firma Digital ECDSA (ANSI X9.62)

Dado un mensaje $M \in \{0,1\}^*$:

1. **Generación de Hash:** $e = \text{SHA-256}(M)$, con el entero $z$ derivado de los bits más significativos de $e$.
2. **Generación de Firma:** Se elige un número entero aleatorio efímero $k \in [1, n-1]$ (k-nonce per-message).
   - Se calcula el punto $(x_1, y_1) = k \cdot G$.
   - Se obtiene $r = x_1 \pmod n$. Si $r = 0$, se reintenta con otro $k$.
   - Se calcula $s = k^{-1} (z + r \cdot d) \pmod n$. Si $s = 0$, se reintenta.
   - La firma digital asignada al mensaje es el par $(r, s)$.

3. **Verificación de Firma:** Dado $(r, s)$ y la clave pública $Q$:
   - Se valida que $r, s \in [1, n-1]$.
   - Se calcula $u_1 = z \cdot s^{-1} \pmod n$ y $u_2 = r \cdot s^{-1} \pmod n$.
   - Se calcula el punto $(x_1, y_1) = u_1 \cdot G + u_2 \cdot Q$.
   - La firma es aceptada si y solo si $x_1 \equiv r \pmod n$.

---

### 2.3 Intercambio de Claves ECDHE y Derivación HKDF

Para asegurar Perfect Forward Secrecy (PFS), cada sesión genera pares de claves efímeros $(d_A, Q_A)$ para la Entidad A y $(d_B, Q_B)$ para la Entidad B.

1. **Acuerdo de Secreto ECDH:** Ambos extremos calculan el punto común $K$:

$$K = d_A \cdot Q_B = d_A \cdot (d_B \cdot G) = d_B \cdot (d_A \cdot G) = d_B \cdot Q_A$$

La coordenada $x_K \in \mathbb{F}_p$ del punto $K$ se extrae como la semilla del secreto compartido $S = \text{bytes}(x_K)$.

2. **Derivación de Claves (HKDF — RFC 5869):**
   El secreto $S$ se procesa mediante una Función Derivadora de Claves basada en HMAC (HKDF-SHA256) en dos etapas:

   - **Extract:**
     $$\text{PRK} = \text{HMAC-SHA256}(\text{salt}, S)$$
     *(Si no se provee salt, se utiliza una cadena de ceros de longitud igual al tamaño del bloque SHA-256).*

   - **Expand:**
     $$T(1) = \text{HMAC-SHA256}(\text{PRK}, \text{info} \parallel \text{0x01})$$
     $$K_{\text{sym}} = \text{OKM} = T(1)[0 \dots L-1]$$
     Donde $L = 32 \text{ bytes}$ (clave simétrica AES-256 resultante).

---

## 3. Especificación de la Arquitectura de Software

La base de código está dividida en módulos de responsabilidad única para garantizar la mantenibilidad y modularidad.

```
CipherVane/
├── capa_cripto/
│   ├── crypto.py      # Generación de par de claves ECC y E/S en formato PEM (PKCS#8)
│   ├── vert_crypt.py  # Operaciones de firma/verificación ECDSA y manejo de excepciones
│   ├── exchange.py    # Handshake ECDH/ECDHE y derivación de clave HKDF-SHA256
│   ├── certs.py       # Motor de emisión de PKI X.509 (Root, Intermediate, Leaf)
│   └── estates.py     # Motor de validación de cadenas de certificados de confianza
├── capa_red/
│   ├── tls_context.py # Fábrica de contextos SSLContext configurados para mTLS
│   ├── socket_srv.py  # Abstracción de conexión de red del Servidor TLS
│   ├── socket_cli.py  # Abstracción de conexión de red del Cliente TLS
│   └── relay.py       # Multiplexado I/O no bloqueante con `select.select`
└── capa_app/
    ├── exceptions.py  # Jerarquía de excepciones personalizadas del sistema
    └── logging.py     # Subsistema de trazabilidad y auditoría
```

---

## 4. Descripción Cuestionada de Módulos y Código de Referencia

### 4.1 Módulo Criptográfico Base (`capa_cripto/crypto.py`)
Encargado del ciclo de vida del par de claves asimétricas. Implementa la serialización en estándar **PKCS#8** para claves privadas y **SubjectPublicKeyInfo (SPKI)** para públicas.

```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

def generar_par_claves():
    clave_privada = ec.generate_private_key(ec.SECP256R1())
    clave_publica = clave_privada.public_key()
    return clave_privada, clave_publica

def exportar_privada_pem(clave_privada, password: bytes = None) -> bytes:
    algoritmo = (
        serialization.BestAvailableEncryption(password)
        if password else serialization.NoEncryption()
    )
    return clave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=algoritmo
    )
```

---

### 4.2 Motor PKI y Jerarquía X.509 (`capa_cripto/certs.py`)
CipherVane impone el cumplimiento estricto de la RFC 5280. La jerarquía asigna los atributos `BasicConstraints` e `IssuerAlternativeName`/`SubjectAlternativeName`:

- **Root CA:** `BasicConstraints(ca=True, path_length=None)`. Autofirmada.
- **Intermediate CA:** `BasicConstraints(ca=True, path_length=0)`. Firmada por Root CA. Restringe la capacidad de emitir CAs subordinadas adicionales.
- **Servidor Leaf:** `BasicConstraints(ca=False)`, `ExtendedKeyUsage([SERVER_AUTH])`, SAN obligatorio con entradas `DNSName` y `IPAddress`.
- **Cliente Leaf:** `BasicConstraints(ca=False)`, `ExtendedKeyUsage([CLIENT_AUTH])`.

```python
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

def construir_certificado_leaf(subject_cn: str, clave_pub_leaf, cert_emisor, clave_priv_emisor, es_servidor: bool):
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject_cn)]))
    builder = builder.issuer_name(cert_emisor.subject)
    builder = builder.public_key(clave_pub_leaf)
    builder = builder.serial_number(x509.random_serial_number())
    
    now = datetime.datetime.now(datetime.timezone.utc)
    builder = builder.not_valid_before(now).not_valid_after(now + datetime.timedelta(days=365))
    
    # Restricciones básicas
    builder = builder.add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
    
    # Propósito de clave extendido
    eku = [x509.ExtendedKeyUsageOID.SERVER_AUTH] if es_servidor else [x509.ExtendedKeyUsageOID.CLIENT_AUTH]
    builder = builder.add_extension(x509.ExtendedKeyUsage(eku), critical=False)
    
    return builder.sign(clave_priv_emisor, hashes.SHA256())
```

---

### 4.3 Validación Criptográfica de la Cadena (`capa_cripto/estates.py`)
Mecanismo de validación estática de certificados utilizando el motor `cryptography.x509.verification.PolicyBuilder`. Evalúa la firma de la cadena, fechas de validez y restricciones de políticas sin depender del stack SSL del sistema operativo.

```python
from cryptography.x509.verification import PolicyBuilder, Store
from cryptography.x509 import DNSName

def validar_certificado_servidor(cert_root, cert_intermedio, cert_servidor, hostname: str):
    almacen_confianza = Store([cert_root])
    builder = PolicyBuilder().store(almacen_confianza)
    verificador = builder.build_server_verifier(DNSName(hostname))
    
    # Lanza InvalidChain / CertificateVerificationError si no satisface la política
    cadena_validada = verificador.verify(cert_servidor, [cert_intermedio])
    return cadena_validada
```

---

### 4.4 Capa de Transporte Mutuamente Autenticada (`capa_red/`)
La seguridad a nivel de red exige que tanto el cliente como el servidor se autentiquen mediante certificados X.509 antes de establecer el túnel TCP.

#### Contexto de Red (`tls_context.py`):
```python
import ssl

def obtener_contexto_mtls_servidor(certfile: str, keyfile: str, cafile: str) -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile=certfile, keyfile=keyfile)
    ctx.load_verify_locations(cafile=cafile)
    ctx.verify_mode = ssl.CERT_REQUIRED  # Fuerza la presentación de certificado de cliente válido
    return ctx
```

#### Bucle de Relay Multiplexado (`relay.py`):
Para evitar el costo de gestión de hilos por conexión, el traspaso de bytes entre la red mTLS y el socket local utiliza el mecanismo I/O Multiplexing por selección síncrona.

```python
import select
import socket

def retransmitir_tráfico(socket_a: socket.socket, socket_b: socket.socket, buffer_size: int = 4096):
    sockets = [socket_a, socket_b]
    while True:
        lectura_lista, _, _ = select.select(sockets, [], [])
        for src in lectura_lista:
            dst = socket_b if src is socket_a else socket_a
            datos = src.recv(buffer_size)
            if not datos:
                return  # EOF detectado, cierre de conexión por la contraparte
            dst.sendall(datos)
```

---

## 5. Requisitos e Instalación

### Prerrequisitos
- **Python:** 3.10+
- **Librerías principales:** `cryptography >= 41.0.0`

### Instalación de dependencias
```bash
python -m venv venv
source venv/bin/activate  # En Linux/macOS
# venv\Scripts\activate   # En Windows

pip install cryptography
```

---

## 6. Diagrama de Flujo del Handshake mTLS

```
   Cliente Leaf                                           Servidor Leaf
   [Certific. Cliente]                                  [Certific. Servidor]
        │                                                        │
        │────────────────────── ClientHello ────────────────────>│
        │                                                        │
        │<── ServerHello + Certificado Servidor + CertificateRequest ──│
        │                                                        │
        │ [Valida Cert Servidor contra CA]                        │
        │                                                        │
        │── Certificado Cliente + ClientKeyExchange + CertificateVerify ──>│
        │                                                        │
        │                        [Valida Cert Cliente contra CA] │
        │                                                        │
        │<────────────── Intercambio de Claves ECDHE ───────────>│
        │<────────────── Derivación de Clave de Sesión ─────────>│
        │                                                        │
        │================= TÚNEL ENCRIPTADO (mTLS) =============│
```

---

## 7. Licencia y Consideraciones de Seguridad
Este software se distribuye únicamente con fines educativos y de arquitectura de sistemas de seguridad. Toda generación de material criptográfico en memoria debe ser depurada adecuadamente al finalizar el contexto del túnel mediante el borrado explícito de buffers o la gestión de garbage collection.