import argparse
import os
from core import encrypt, decrypt
from auth import login_flow, register_user
from filemanager import find_external, create_directory, NotFound

def run():
    storage = find_external()
    if storage is None:
        raise NotFound("No se detectó almacenamiento externo.")

    create_directory(os.path.join(storage, "EncrypFiler"))

    parser = argparse.ArgumentParser(description="Encriptar y desencriptar archivos. Se requiere analizar la partición externa e interna antes de encriptar.")
    subparsers = parser.add_subparsers(dest="accion", required=True)

    subparsers.add_parser("registrar", help="Registrar nuevo usuario")

    encriptar_parser = subparsers.add_parser("encriptar", help="Encriptar archivo")
    encriptar_parser.add_argument("archivo", help="archivo a encriptar")
    encriptar_parser.add_argument("--clave", required=True, help="Clave de encryptacion. Ejemplo --clave 123")

    desencryptar_parser = subparsers.add_parser("desencriptar", help="Desencriptar archivo")
    desencryptar_parser.add_argument("archivo", help="Archivo a desencriptar")
    desencryptar_parser.add_argument("--clave", required=True, help="Clave de decifrado.")

    args = parser.parse_args()

    # "registrar" no requiere login (para poder crear el primer usuario)
    if args.accion == "registrar":
        register_user()
        return

    # AUTH OBLIGATORIO PARA ENCRIPTAR/DESENCRIPTAR
    if not login_flow():
        print("Acceso denegado. No puedes acceder a los archivos.")
        return

    if args.accion == "encriptar":
        encrypt(args.archivo, args.clave) #argumento
        print(f"Archivo: {args.archivo} encriptado con exito.")
    elif args.accion == "desencriptar":
        if decrypt(args.archivo, args.clave):
            print(f"Archivo: {args.archivo} desencriptado como original.")

if __name__ == "__main__":
    run()


