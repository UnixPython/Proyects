encryptpass/
│
├── core/
│   ├── memory.py          → bloqueo/desbloqueo RAM, wipe de buffers, mmap seguro
│   ├── kill_switch.py     → captura SIGINT/SIGTERM, limpia memoria y cierra limpio
│   └── exceptions.py      → todas las excepciones base del proyecto centralizadas
│
├── auth/
│   ├── login.py           → crea y valida sesión en /tmp, nunca toca disco permanente
│   ├── timing.py          → comparación segura con hmac.compare_digest, evita timing attacks
│   ├── rate_limit.py      → limita intentos fallidos con backoff exponencial
│   ├── tokens.py          → genera y valida tokens efímeros de sesión
│   ├── session.py         → controla expiración automática de sesión activa
│   ├── duplicate.py       → detecta si hay dos sesiones activas simultáneas
│   └── reauth.py          → re-autenticación silenciosa sin interrumpir al usuario
│
├── identity/
│   ├── fingerprint.py     → genera hash único del hardware (machine-id, MAC, disco, UUID)
│   └── alerts.py          → dispara alerta si el fingerprint cambia entre sesiones
│
├── crypto/
│   ├── policies.py        → aplica políticas criptográficas del sistema Linux
│   ├── shamir.py          → fragmenta y reconstruye claves con Shamir Secret Sharing
│   └── secure_delete.py   → sobreescribe y elimina archivos si algo toca disco
│
├── detection/
│   ├── vm_detect.py       → detecta si el proceso corre dentro de VM o sandbox
│   ├── debugger.py        → detecta si hay un debugger activo en el proceso
│   ├── canary.py          → coloca tokens trampa que delatan acceso no autorizado
│   ├── honeypot.py        → campos falsos que registran quién intenta explotarlos
│   └── forensic.py        → activa modo solo lectura para análisis post-incidente
│
├── audit/
│   ├── log.py             → log cifrado e inmutable, no editable después de escrito
│   └── emergency.py       → modo emergencia, bloquea escritura y congela el estado
│
├── network/
│   ├── e2e.py             → cifrado extremo a extremo entre nodos de la red local
│   ├── zero_trust.py      → verifica identidad en cada operación, sin confianza implícita
│   └── multiparty.py      → requiere autorización de múltiples partes para operar
│
├── future/
│   ├── c_module/          → módulo externo en C/ASM, formato propietario, vive fuera del paquete
│   ├── ai_server.py       → cliente que habla con servidor IA externo de detección de anomalías
│   ├── faceid.py          → verificación de presencia física en tiempo real, sin datos persistidos
│   ├── autogen_pass.py    → genera contraseña efímera por sesión, elimina vector keylogger
│   ├── esp32.py           → interfaz con ESP32 para seguridad en hardware a bajo nivel
│   ├── raspi.py           → interfaz remota con Raspberry Pi basada en huella única
│   └── mfa.py             → múltiples formas simultáneas de inicio de sesión
│
├── config/
│   └── settings.py        → configuración global del proyecto, rutas, constantes, flags
│
├── main.py                → punto de entrada, orquesta arranque, señales y ciclo principal
├── requirements.txt       → dependencias del proyecto
└── README.md              → documentación del proyecto
