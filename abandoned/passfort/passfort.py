import json
from pathlib import Path
from core.crypto import firm, verificar, salt
from core.auth import hash_password, login, is_session_valid
from core.vault import encrypt, decrypt_message, atomic_write

if __name__ == "__main__":
    master = input("Crea tu master password: ")
    stored_hash = hash_password(master)

    intento = input("Ingresa tu password: ")

    if login(intento, stored_hash):
        print("Sesión iniciada.")
        service = input("Servicio:  ")
        usr = input("Usuario o correo:  ")
        passwd = input("Contraseña: ")
        data = {"servicio": service, "usuario": usr, "password": passwd}
        datas = json.dumps(data).encode()
        blob, key = encrypt(datas)
        atomic_write(Path("vault.enc"), blob)

    else:
        print("Password incorrecta.")
