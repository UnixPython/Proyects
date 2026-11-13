"""Guardado y carga de la passphrase cifrada y del par de claves EC."""
import getpass
import logging
import os
from logger import base
from exceptions import DecryptErr
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from crypto import private, public
from passwds import decrypt, derive_key, encrypt_passwd, gen

logger = logging.getLogger(__name__)

SALT_LEN = 16
NONCE_LEN = 12


def pedir_clave_usuario():
    """Paso 1 del patrón: pide la clave sin mostrarla al escribir."""
    return getpass.getpass("Passwd to save: ")

@base
def save_passwds(rute, key):
    """Genera una passphrase, la cifra con `key` y la guarda en `rute`."""
    passphrase = gen()
    salt = os.urandom(SALT_LEN)
    val = derive_key(key, salt)
    nonce, ct = encrypt_passwd(val, passphrase.encode("utf-8"))
    try:
        with open(rute, "xb") as f:
            f.write(salt + nonce + ct)
    except FileExistsError:
        logger.error("%s ya existe; no se sobrescribe.", rute)
        raise
    except FileNotFoundError:
        logger.error("La carpeta de %s no existe.", rute)
        raise
    return passphrase

@base
def save_keys(rute_priv, rute_pub, passphrase):
    """Genera el par EC y guarda la privada (cifrada) y la pública."""
    ec_key = ec.generate_private_key(ec.SECP256R1())
    pem_priv = private(ec_key, passphrase.encode("utf-8"))
    pem_pub = public(ec_key)
    with open(rute_priv, "xb") as f:
        f.write(pem_priv)
    with open(rute_pub, "xb") as f:
        f.write(pem_pub)
    return ec_key

@base
def load_passwds(rute, key):
    """Lee `rute`, deriva la clave con `key` y devuelve la passphrase (str)."""
    with open(rute, "rb") as f:
        blob = f.read()
    salt = blob[:SALT_LEN]
    nonce = blob[SALT_LEN:SALT_LEN + NONCE_LEN]
    ct = blob[SALT_LEN + NONCE_LEN:]
    val = derive_key(key, salt)
    return decrypt(val, nonce, ct)

@base
def load_key(rute_priv, passphrase):
    """Carga la clave privada cifrada usando `passphrase`."""
    try:
        with open(rute_priv, "rb") as f:
            return serialization.load_pem_private_key(
                f.read(), password=passphrase.encode("utf-8")
            )
    except TypeError:
        print("Clave no fue cifrada.")


@base
def main():
    key = pedir_clave_usuario()
    try:
        if not os.path.exists("pass.enc"):
            passphrase = save_passwds("pass.enc", key)
            ec_key = save_keys("privada.pem", "publica.pem", passphrase)
        else:
            passphrase = load_passwds("pass.enc", key)
            ec_key = load_key("privada.pem", passphrase)
    except DecryptErr as exc:
        print("Clave incorrecta o pass.enc alterado.")
        raise SystemExit(1) from exc
    except FileExistsError as exc:
        print("Un archivo ya existe; no se sobrescribió nada.")
        raise SystemExit(1) from exc
    except FileNotFoundError as exc:
        print("Falta un archivo (pass.enc o privada.pem).")
        raise SystemExit(1) from exc
    except ValueError as exc:
        print("privada.pem dañado o passphrase incorrecta.")
        raise SystemExit(1) from exc
    except OSError as exc:
        print(f"Error de archivo: {exc.strerror or exc}")
        raise SystemExit(1) from exc
    return ec_key

if __name__ == "__main__":
    main()

