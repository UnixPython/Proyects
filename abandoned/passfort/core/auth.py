import time
import hashlib
import os
import hmac 

# Estado de sesión en memoria (nunca en disco)
_session = {
    "active": False,
    "expires_at": 0.0
}

def hash_password(password: str) -> bytes:
    salt = os.urandom(16)
    dk = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=16384,
        r=8,
        p=2,
        dklen=32
    )
    return salt + dk

def verify_password(stored_password: bytes, provised_password: str) -> bool:
    salt = stored_password[:16]
    stored_key = stored_password[16:]
    key = hashlib.scrypt(
        provised_password.encode(),
        salt=salt,
        n=16384,
        r=8,
        p=2,
        dklen=32
    )
    return hmac.compare_digest(key, stored_key)
        
def start_session() -> None:
    _session["active"] = True
    _session["expires_at"] = time.time() + 30

def is_session_valid() -> bool:
    return _session["active"] and time.time() < _session["expires_at"]

def end_session() -> None:
    _session["active"] = False
    _session["expires_at"] = 0.0

def login(password: str, stored_hash: bytes) -> bool: 
    if verify_password(stored_hash, password):
        start_session()
        return True 
    return False
