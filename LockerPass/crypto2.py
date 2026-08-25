import logging
import os
import getpass  # Evita que se vea la contraseña en pantalla
from argon2.low_level import hash_secret_raw, Type
from argon2.exceptions import HashingError
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.exceptions import UnsupportedAlgorithm, InvalidTag
# Asegúrate de tener estos errores definidos en tu archivo exceptions.py
from exceptions import DecryptErr, PassError, EncryptErrno

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("cryps.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def derive_key(master_password: str, salt: bytes) -> bytes:
    try:
        return hash_secret_raw(
            secret=master_password.encode("utf-8"),
            salt=salt,
            time_cost=3,
            memory_cost=98304,  # 96 MB
            parallelism=2,
            hash_len=32,
            type=Type.ID
        )
    except HashingError as e:
        logger.warning("Derivación fallada. Revisar parámetros de Argon2.")
        raise PassError("Fallo en la derivación de la clave") from e

def encrypt_passwd(master_password: str, password_to_hide: str, aad: bytes = b"") -> tuple[bytes, bytes, bytes]:
    """Cifra una contraseña usando parámetros limpios y seguros."""
    try:
        salt = os.urandom(16)
        nonce = os.urandom(12)
        
        key = derive_key(master_password, salt)
        chacha = ChaCha20Poly1305(key)
        
        ct = chacha.encrypt(nonce, password_to_hide.encode("utf-8"), aad)
        return salt, nonce, ct
    except UnsupportedAlgorithm as e:
        logger.error("Versión de OpenSSL obsoleta.")
        raise EncryptErrno("ChaCha20Poly1305 no soportado por OpenSSL.") from e

def decrypt(ct: bytes, nonce: bytes, salt: bytes, master_password: str, aad: bytes = b"") -> str:
    """Desencripta verificando la integridad del contenido."""
    try:
        key = derive_key(master_password, salt)
        chacha = ChaCha20Poly1305(key)
        
        pt = chacha.decrypt(nonce, ct, aad)
        return pt.decode("utf-8")
    except InvalidTag as e:
        logger.error("Falló la autenticación: Datos alterados o contraseña incorrecta.")
        raise DecryptErr("Fallo de autenticación.") from e

# --- EJEMPLO DE USO CORRECTO EN INTERFAZ ---
if __name__ == "__main__":
    print("--- REGISTRO DE NUEVA CONTRASEÑA ---")
    # getpass oculta la escritura en la terminal
    m_pass = getpass.getpass("Crea tu Master Password: ")
    secret = getpass.getpass("Introduce la contraseña que deseas guardar: ")
    contexto = b"Metadata_Usuario_1" # El AAD puede ser fijo o público, no secreto.

    # Encriptamos
    salt, nonce, ciphertext = encrypt_passwd(m_pass, secret, contexto)
    print("\n✓ Contraseña cifrada exitosamente.")
    
    print("\n--- INTENTO DE DESENCRIPTACIÓN ---")
    m_pass_intent = getpass.getpass("Introduce tu Master Password para desbloquear: ")
    
    try:
        decrypted_password = decrypt(ciphertext, nonce, salt, m_pass_intent, contexto)
        print(f"✓ Éxito. Tu contraseña guardada es: {decrypted_password}")
    except DecryptErr:
        print("✗ No se pudo desencriptar. Contraseña incorrecta.")

