import json
import os
import stat
from pathlib import Path
from Crypto.Cipher import AES 
from Crypto.Random import get_random_bytes
import time 

def dictbytes():
    try:
        data = {"user": "anonym", "pass": "1234"}
        jsons = json.dumps(data).encode("utf-8")
        return jsons

    except json.JSONDecodeError:
        raise
    
def recovery_dict():
    raw = b'{"user": "anonym", "pass": "1234"}' #convierte dict a bytes
    data = json.loads(raw)
    print(data["user"]) #usuario anonym

def encrypt(data: bytes) -> tuple[bytes, bytes] | None:
    try:
        print("Cifrado.")
        key = get_random_bytes(32) #key de 32 bytes
        cipher = AES.new(key, AES.MODE_GCM)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(data) #encriptacion
        blob = nonce + tag + ciphertext 
        return blob, key
    except ValueError:
        print("La encriptación falló.") 
        return None

def decrypt_message(blob, key):
    if len(blob) < 32:
        raise ValueError(f"Blob inválido: se esperan al menos 32 bytes, se recibieron {len(blob)}")
    try:  
        nonce = blob[:16]
        tag = blob[16:32] 
        ciphertext = blob[32:] 
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce) 
        #decifra el ciphertext 
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return json.loads(plaintext.decode())
    except ValueError:
        return "Error: La verificación del tag"

def archive(): 
    try:
        with open('vault.enc', 'rb', encoding='utf-8') as archivo:
            contenido = archivo.read()                
            print(contenido)

    except FileNotFoundError:
        print("El archivo no existe en la ruta.")
    except PermissionError:
        print("No existen permisos de escriturar ni lectura.")
    except OSError as e:
        print(f"Error del sistema de archivos: {e.strerror}")

def atomic_write(path: Path, data: bytes):
    try:
        tmp = path.with_suffix(".tmp")
        tmp.write_bytes(data)
        os.replace(tmp, path)
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)

    except OSError as e:
        print(f"Write atómico falló: {e.strerror} — ruta: {e.filename}")
    
def permissions():
    mode = os.stat("vault.db").st_mode & 0o777
    time.sleep(5)
    print("Verificando vault.db..")
    if mode != 0o600:
        print(f"Permisos inseguros: {oct(mode)}")
    print(oct(os.stat("vault.db").st_mode))

if __name__ == "__main__":
    atomic_write(Path("vault.enc"), b"datos cifrados")
    mensaje = dictbytes()
    resultado = encrypt(mensaje)
    if resultado is None:
        print("No se pudo cifrar el mensaje.")
    else:
        blob, key = resultado
        print("Blob cifrado: ", blob.hex())
        decrypts = decrypt_message(blob, key)
        print("Mensaje descifrado: ", decrypts)
