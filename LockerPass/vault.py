import os
import json
import base64
import logging
import getpass
from pathlib import Path
from datetime import datetime, timezone

import crypto
import generate
from memory import memory as SecureBuffer
from exceptions import PassError, DecryptErr, InvalidValue

logger = logging.getLogger(__name__)

VAULT_VERSION = 1


# ------------------------------------------------------------------
# Persistencia del archivo .enc
# ------------------------------------------------------------------

def _write_vault(path: Path, vault: dict) -> None:
    """Escritura atómica: escribe a .tmp y recién reemplaza el archivo final."""
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(vault, indent=2), encoding="utf-8")
    os.replace(tmp_path, path)


def _read_vault(path: Path) -> dict:
    if not path.exists():
        raise InvalidValue(f"El vault {path} no existe.")
    vault = json.loads(path.read_text(encoding="utf-8"))
    if vault.get("version") != VAULT_VERSION:
        raise InvalidValue(f"Versión de vault no soportada: {vault.get('version')}")
    return vault


# ------------------------------------------------------------------
# Registro / Login
# ------------------------------------------------------------------

def register(vault_path: str) -> SecureBuffer:
    """Crea un vault nuevo vacío y devuelve la clave de sesión en un buffer seguro."""
    path = Path(vault_path)
    if path.exists():
        raise InvalidValue(f"Ya existe un vault en {vault_path}.")

    master_password = getpass.getpass("Crea tu contraseña maestra: ")
    confirm = getpass.getpass("Confirma tu contraseña maestra: ")
    if master_password != confirm:
        raise PassError("Las contraseñas maestras no coinciden.")

    salt = os.urandom(16)
    key = crypto.derive_key(master_password, salt)

    vault = {
        "version": VAULT_VERSION,
        "salt": base64.b64encode(salt).decode("ascii"),
        "entries": {}
    }
    _write_vault(path, vault)
    logger.info("Vault creado en %s", vault_path)

    session_key = SecureBuffer(len(key))
    session_key.lock()
    session_key.write(key)
    return session_key


def login(vault_path: str) -> SecureBuffer:
    """Deriva la clave de un vault existente y la devuelve en un buffer seguro.
    No confirma si el password es correcto hasta que se intente descifrar algo."""
    path = Path(vault_path)
    vault = _read_vault(path)

    master_password = getpass.getpass("Contraseña maestra: ")
    salt = base64.b64decode(vault["salt"])
    key = crypto.derive_key(master_password, salt)

    session_key = SecureBuffer(len(key))
    session_key.lock()
    session_key.write(key)
    return session_key


def logout(session_key: SecureBuffer) -> None:
    """Limpia y libera la clave de sesión de memoria."""
    session_key.close()
    logger.info("Sesión cerrada, clave liberada de memoria.")


# ------------------------------------------------------------------
# CRUD de entradas
# ------------------------------------------------------------------

def add_entry(vault_path: str, session_key: SecureBuffer, site: str,
              username: str, password: str = None) -> None:
    path = Path(vault_path)
    vault = _read_vault(path)

    if password is None:
        password = generate.generate_password()

    key = session_key.read()
    aad = username.encode("utf-8")
    nonce, ciphertext = crypto.encrypt_passwd(key, password.encode("utf-8"), aad=aad)

    vault["entries"][site] = {
        "username": username,
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    _write_vault(path, vault)
    logger.info("Entrada agregada: %s", site)


def get_password(vault_path: str, session_key: SecureBuffer, site: str) -> str:
    vault = _read_vault(Path(vault_path))
    entry = vault["entries"].get(site)
    if entry is None:
        raise InvalidValue(f"No existe una entrada para {site}.")

    key = session_key.read()
    nonce = base64.b64decode(entry["nonce"])
    ciphertext = base64.b64decode(entry["ciphertext"])
    aad = entry["username"].encode("utf-8")

    try:
        return crypto.decrypt(key, nonce, ciphertext, aad=aad)
    except DecryptErr:
        logger.error("Fallo al descifrar la entrada %s", site)
        raise


def edit_entry(vault_path: str, session_key: SecureBuffer, site: str,
               new_password: str = None, new_username: str = None) -> None:
    path = Path(vault_path)
    vault = _read_vault(path)
    entry = vault["entries"].get(site)
    if entry is None:
        raise InvalidValue(f"No existe una entrada para {site}.")

    username = new_username if new_username is not None else entry["username"]

    if new_password is not None:
        key = session_key.read()
        aad = username.encode("utf-8")
        nonce, ciphertext = crypto.encrypt_passwd(key, new_password.encode("utf-8"), aad=aad)
        entry["nonce"] = base64.b64encode(nonce).decode("ascii")
        entry["ciphertext"] = base64.b64encode(ciphertext).decode("ascii")

    entry["username"] = username
    vault["entries"][site] = entry
    _write_vault(path, vault)
    logger.info("Entrada editada: %s", site)


def delete_entry(vault_path: str, site: str) -> None:
    path = Path(vault_path)
    vault = _read_vault(path)
    if site not in vault["entries"]:
        raise InvalidValue(f"No existe una entrada para {site}.")
    del vault["entries"][site]
    _write_vault(path, vault)
    logger.info("Entrada eliminada: %s", site)


def delete_field(vault_path: str, site: str, field: str) -> None:
    """Elimina solo 'username' o solo el password (nonce+ciphertext), no la entrada entera."""
    if field not in ("username", "password"):
        raise InvalidValue("field debe ser 'username' o 'password'.")

    path = Path(vault_path)
    vault = _read_vault(path)
    entry = vault["entries"].get(site)
    if entry is None:
        raise InvalidValue(f"No existe una entrada para {site}.")

    if field == "username":
        entry["username"] = ""
    else:
        entry["nonce"] = ""
        entry["ciphertext"] = ""

    vault["entries"][site] = entry
    _write_vault(path, vault)
    logger.info("Campo '%s' eliminado de la entrada %s", field, site)


def list_entries(vault_path: str) -> list:
    vault = _read_vault(Path(vault_path))
    return [
        {"site": site, "username": data["username"], "created_at": data["created_at"]}
        for site, data in vault["entries"].items()
    ]
