# CryptPart

**Encriptado de particiones en Python — nativo para Linux**            
| | |
|---|---|
| **Versión actual** | 0.8.0 |
| **Roadmap** | v1.0 (release estable) |                               | **Compatibilidad** | Linux |                                         | **Criptografía** | AES-XTS + Argon2id |                              
---

## ¿Qué es CryptPart?

CryptPart es una herramienta de línea de comandos que cifra particiones completas usando el modo de cifrado **AES-XTS** —el mismo empleado por estándares de la industria como BitLocker o LUKS para almacenamiento en bloque— combinado con **Argon2id** como función de derivación de clave a partir de la contraseña del usuario.
                                                                       El objetivo del proyecto no es competir con `dm-crypt`/LUKS en features, sino ofrecer un esquema de cifrado de particiones propio, auditable y minimalista, con reglas de seguridad definidas por el propio diseño en lugar de heredar el formato de un estándar externo.

---
                                                                       ## ¿Qué hace?

Cifra una partición usando una contraseña provista por el usuario. La clave derivada nunca se guarda en disco en texto plano: vive en memoria únicamente durante la operación de cifrado/descifrado, y esa región de memoria está protegida contra swapping y manipulación externa (ver *Protección de memoria*).

### Ejemplo de uso

```
$ python3 main.py encriptar particiones

Detectando sesión...
(-) No existe sesión

Register Session
usuario: kael
contraseña: ********
---
Sesión creada

ID: 1838382929
Fingerprint (SHA256): 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
Archivo de sesión: login.enc
Archivo de fingerprint: fingerprint.sha256

Particiones detectadas:
  [1] /dev/sdb1 (500 GB)

Seleccioná partición a encriptar: 1
Contraseña de encriptado de partición: ********

Cifrando /dev/sdb1...

Partición /dev/sdb1 encriptada correctamente.
```

---

## Arquitectura de seguridad — formalización

Esta sección describe el esquema con la notación estándar de criptografía aplicada. No sustituye una prueba de seguridad formal (eso exigiría un análisis en el modelo de un adversario concreto, IND-CPA/IND-CCA según corresponda); es la especificación matemática del diseño.

### 1. Primitiva de cifrado: AES-XTS

XTS (*XEX-based Tweaked-codebook mode with ciphertext Stealing*, NIST SP 800-38E) es el único modo de los estándar NIST diseñado para **almacenamiento de bloques direccionable aleatoriamente**, a diferencia de CBC/GCM, que asumen un flujo secuencial con estado (IV encadenado o contador).

**Material de clave.** La clave XTS se compone de dos subclaves independientes de la misma longitud:

```
K = K1 ‖ K2,     |K1| = |K2| = 256 bits     →     |K| = 512 bits
```

`K1` es la clave de cifrado de bloque propiamente dicha. `K2` cifra el *tweak*, que ata criptográficamente cada bloque a su posición física, evitando que el mismo texto plano en dos sectores distintos produzca el mismo texto cifrado (lo que rompería la primitiva bajo un modelo ECB).

**Cifrado de un bloque de datos** en el sector `i`, bloque `j` dentro de ese sector:

```
tweak_i     = E(K2, i)                      // cifra el número de sector
α           = tweak_i · a^j    (en GF(2^128))   // "α" desplaza el tweak por bloque
C_{i,j}     = E(K1, P_{i,j} ⊕ α) ⊕ α
```

donde `a` es el elemento primitivo del campo de Galois `GF(2^128)` definido por el polinomio `x^128 + x^7 + x^2 + x + 1` (el mismo campo usado en GCM). Esta multiplicación por `a^j` es lo que hace que bloques sucesivos dentro de un mismo sector, aun compartiendo el mismo `tweak_i`, produzcan salidas distintas.

**Propiedad de seguridad y su límite.** XTS es *tweakable* IND-CPA seguro bajo el supuesto de que AES es una PRP (permutación pseudoaleatoria). Pero — y esto es relevante para tu diseño — **XTS no provee autenticación**: no hay tag de integridad. Un adversario con acceso de escritura al dispositivo puede alterar bloques cifrados sin que el esquema lo detecte; solo obtendrá texto plano corrupto en descifrado, no un error explícito. Esto justifica por qué tu segundo factor (fingerprint) *no* puede cumplir función de integridad de datos — solo identifica el disco, no garantiza que su contenido no fue modificado. Si en algún momento necesitás detectar manipulación del header, la única primitiva de esta lista que provee esa garantía es HMAC.

### 2. Derivación de clave: Argon2id

La contraseña `pw ∈ {0,1}^*` no es la clave de cifrado — se transforma mediante una función de derivación de clave con costo de memoria configurable:

```
K = Argon2id(pw, salt, t, m, p, τ)
```

- `t` ∈ ℕ — costo temporal (número de pasadas sobre la memoria)
- `m` ∈ ℕ — costo de memoria, en KiB
- `p` ∈ ℕ — grado de paralelismo (lanes)
- `τ` — longitud de salida deseada, en bytes (`τ = 64` si `K` alimenta directamente a XTS)
- `salt` — valor aleatorio de al menos 128 bits, único por credencial

**Por qué memory-hardness importa formalmente.** El costo de un atacante que intenta invertir `Argon2id` por fuerza bruta sobre un espacio de contraseñas `𝒟` (diccionario) se modela como:

```
Costo_atacante ≈ |𝒟| · Costo_hw(t, m, p)
```

Con PBKDF2, `Costo_hw` depende solo de `t`, y un ASIC puede paralelizar miles de instancias simultáneas a bajo costo marginal, porque no hay requerimiento de memoria por instancia. Con Argon2id, cada instancia de evaluación exige `m` KiB de memoria *dedicada* — el atacante no puede compartir esa memoria entre instancias paralelas sin degradar el rendimiento de cada una proporcionalmente. Esto convierte el costo de atacar en un problema de **área de silicio**, no solo de tiempo de cómputo, lo cual es la propiedad central que hace a Argon2id superior a PBKDF2/bcrypt frente a atacantes con hardware dedicado (ASIC/FPGA).

### 3. Composición de los dos factores

Definimos dos secretos/valores independientes:

```
F_conocimiento  = Argon2id(pw, salt_sesión, ...)        →  valida "login.enc"
F_identidad     = SHA256(atributos_del_disco)           →  fingerprint.sha256
```

`F_conocimiento` es un factor de **conocimiento** (algo que el usuario sabe). `F_identidad` es un factor de **posesión/identidad** ligado al medio físico (algo que el disco *es*, no algo que el usuario recuerda) — por eso viaja con el dispositivo y es independiente de en qué equipo se ejecuta el proceso.

Formalmente, la sesión se considera válida solo bajo la conjunción de ambos predicados:

```
Válida(sesión) = Verificar(F_conocimiento) ∧ Coincide(F_identidad, disco_actual)
```

Ninguno de los dos factores es reducible al otro: comprometer la contraseña sin tener el disco físico (o su fingerprint) no basta, y viceversa — tener el disco sin la contraseña tampoco permite derivar `K`. Esto es lo que técnicamente justifica llamarlo *dos factores* y no una single capa disfrazada de dos.

**Advertencia formal:** `SHA256` aquí actúa como función de identificación (huella), no como función de derivación de clave — no tiene memory-hardness ni costo ajustable. Si en algún momento el fingerprint pasara a participar en la derivación de `K` (por ejemplo, `K = Argon2id(pw ‖ fingerprint, ...)`), estarías fusionando ambos factores en una sola clave, lo cual cambia el modelo de seguridad: ya no serían dos factores independientes verificables por separado, sino un único secreto compuesto. Mantenerlos desacoplados, como está descrito arriba, es la decisión correcta para preservar la propiedad de "dos factores" en sentido estricto.

### 4. Protección de memoria en tiempo de ejecución

La clave `K`, una vez derivada, existe como material sensible en el espacio de direcciones del proceso durante la ventana de la operación de cifrado/descifrado. El objetivo de bloquear esa región es reducir la superficie de exposición ante dos vectores concretos: volcado a swap (la clave terminando en disco, fuera del control del proceso) y lectura por otro proceso con privilegios suficientes. Ninguna protección a nivel de aplicación elimina el riesgo de un atacante con acceso root o físico a la RAM (cold boot attack) — eso excede lo que cualquier biblioteca en espacio de usuario puede garantizar.

---

## ¿Es confiable?

CryptPart está construido con un diseño deliberadamente liviano: menos superficie de código significa menos lugares donde puede existir un error. Esa filosofía —minimizar complejidad para minimizar riesgo— es la misma que sostiene proyectos como `age` frente a formatos más complejos como OpenPGP.

Dicho esto, ningún software es inmune a vulnerabilidades de día cero que el autor no haya detectado durante el desarrollo. "Confiable por diseño" no es sinónimo de "invulnerable" — es una afirmación sobre la intención arquitectónica, no una garantía absoluta.

---

## Perdí mi contraseña. ¿Qué hago?

**No hay recuperación.** Esto es intencional, no una limitación técnica pendiente de resolver: cualquier mecanismo de recuperación es, por definición, una puerta trasera hacia las credenciales. Un esquema que promete "cifrado seguro" y a la vez "recuperación de contraseña" está, en la práctica, debilitando su propio modelo de amenaza.

Si perdés la contraseña, los datos de la partición cifrada son irrecuperables.

---

## Preguntas frecuentes

**¿Puedo mover el disco cifrado a otra PC?**
Sí. El fingerprint está atado al disco, no a la máquina donde corre CryptPart, así que viaja con el dispositivo. La sesión (factor de conocimiento) se sigue validando de forma independiente en el nuevo equipo.

**¿Por qué XTS y no un modo más simple como CBC?**
Porque CBC exige acceso secuencial y no tolera bien el acceso aleatorio por sector que exige un disco. XTS fue diseñado por el NIST específicamente para este caso de uso (SP 800-38E).

**¿Por qué Argon2id y no bcrypt/scrypt?**
Argon2id es el ganador de la competencia de referencia de la industria y el recomendado actual por RFC 9106 para nuevos sistemas. bcrypt y scrypt siguen siendo válidos, pero Argon2id ofrece mejor resistencia combinada a ataques de canal lateral y de hardware dedicado.

---

## Roadmap hacia v1.0

- [ ] Documentar el formato exacto del header de la partición
- [ ] Definir política de reintentos fallidos de contraseña
- [ ] Auditoría externa de la implementación de protección de memoria
---

*CryptPart es un proyecto personal en desarrollo activo. Esta documentación describe el diseño previsto — la implementación puede no cubrir aún el 100% de lo aquí descrito hasta alcanzar v1.0.*
