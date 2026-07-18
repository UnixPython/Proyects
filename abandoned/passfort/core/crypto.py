import hmac
import hashlib
import os

key = os.urandom(32)
person = input("Escriba el codigo para person: ").encode("utf-8")
digest_size = 32

def salt():
    return os.urandom(16)

def hashing(value):
    try:
        h = hashlib.blake2b(key=key, person=person, digest_size=digest_size)
        h.update(value)
        return h.hexdigest()
    except TypeError:
        print("El dato debe ser bytes, no str.")
    except ValueError as e:
        print(f"Se excedió el limite de caracteres. {e}")

def firm(date: bytes, salt: bytes):
    h = hashlib.blake2b(key=key, digest_size=digest_size)
    h.update(date + salt)
    return h.hexdigest()

def verificar(data: bytes, salt: bytes, hash_esperado: str) -> bool:
    print("Se verificará si fue modificado.")
    hash_calculado = firm(data, salt)
    return hmac.compare_digest(hash_calculado, hash_esperado)

