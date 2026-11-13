import logging
import getpass
from logger import base
from identity import load_passwds
from pathlib import Path
from exceptions import DecryptErr
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

"""
Verificar la firma y cargar
"""

logger = logging.getLogger(__name__)

def verify_archives():
    pub = Path("publica.pem")
    priv = Path("privada.pem")

    if pub.is_file():
        print("[+] publica.pem")
    else:
        print("No se encontró publica.pem")
    if priv.is_file():
        print("[+] privada.pem")
    else:
        print("No se encontró privada.pem")

def verify_pub_public(rute_pub, signature):
    try:
        with open(rute_pub, "rb") as f:
            pubi = serialization.load_pem_public_key(f.read())
        data = getpass.getpass("Message to verify: ")
        encoding = data.encode("utf-8")
        if not isinstance(pubi, ec.EllipticCurvePublicKey):
            raise TypeError("Clave no es EC publica.")
        pubi.verify(signature, encoding, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        print("Datos alterados.")
        return False
    except FileNotFoundError:
        print("No existe archivo para verificar.")
        return False 
    
@base
def private_verify(rute_priv):
    try:
        data_load  = getpass.getpass("Load key to private:   ")
        passphrase = load_passwds("pass.enc", data_load)
        with open(rute_priv, "rb") as f:
            dates = f.read()
            private_key = serialization.load_pem_private_key(dates, password=passphrase.encode("utf-8"))
            mensaje = getpass.getpass("Message to firm: ")
            data = mensaje.encode("utf-8")
            if not isinstance(private_key, ec.EllipticCurvePrivateKey):
                raise TypeError("La clave no es EC")
            signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))
            return signature
    except FileNotFoundError as exc:
        print("Nose encontró el archivo correspondiente")
        raise SystemExit(1) from exc
    except DecryptErr as exc:
        print("Clave incorrecta")
        raise SystemExit(1) from exc
    except ValueError as exc:
        print("Passphrase incorrecta o privada.pem dañado")
        raise SystemExit(1) from exc
    except TypeError as exc:
        print("Tipo de dato incorrecto")
        raise SystemExit(1) from exc
    except KeyboardInterrupt as exc:
        print("Proceso cancelado.")
        raise SystemExit(1) from exc

if __name__ == "__main__":
    verify_archives()
    priva = private_verify("privada.pem")
    print(priva)
    print(verify_pub_public("publica.pem", priva))
