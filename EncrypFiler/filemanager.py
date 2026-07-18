import datetime
import os
from pathlib import Path


#Exceptions
class NotFound(Exception):
    """Error de directorio al telefono"""
    pass


def find_external():
    ruta = input("Escribe la ruta de la partición externa (ej: /storage/6177-1919): ").strip()
    if not ruta:
        print("No escribiste ninguna ruta.")
        return None
    if not os.path.isdir(ruta):
        print(f"La ruta '{ruta}' no existe o no es un directorio.")
        return None
    return ruta


def create_directory(dirs):
    try:
        os.makedirs(dirs, exist_ok=True)
        print("Existe el directorio.")
    except FileNotFoundError as e:
        print(f"Error al crear el directorio: {e}")
        raise NotFound("""
        Se realizó la creación de directorió pero falló.""")

def list_files(base_path):
    p = Path(base_path)
    #iterar archivos
    for item_archives in p.iterdir():
        tipe = "Directorio" if item_archives.is_dir() else "Archivo"
        print(f"{tipe}: {item_archives.name}")


def select_files(base_path):
    try:
        p = Path(base_path)
        items = list(p.iterdir())
        for i, item in enumerate(items, 1):
            print(f"{i}. {item.name}")
        opcion = int(input("Elige: "))
        elegido = items[opcion - 1]
        return elegido
    except Exception as e:
        print(f"Error: {e}")


def write_bytes(base_path):
    try:
        archive_path = os.path.join(base_path, "EncrypFiler", "archive.txt")
        with open(archive_path, "rb") as f:
            dates = f.read()  #lee archivo
            return dates
    except FileNotFoundError:
        print("Archivo no encontrado")


def writer_bytes(base_path, wrdates):
    enc_path = os.path.join(base_path, "EncrypFiler", "date.enc")
    with open(enc_path, "wb") as f:
        f.write(wrdates)


def delete_archive(base_path):
    archive = Path(base_path) / "EncrypFiler" / "archive.txt"
    archive.unlink(missing_ok=True)
    return archive


def metadata(base_path):
    info = Path(base_path) / "EncrypFiler" / "archive.txt"

    if info.exists():
        stats = info.stat()
        print(f"File Size: {stats.st_size} bytes")
        print(f"Last Modified: {datetime.datetime.fromtimestamp(stats.st_mtime)}")
        print(f"Last Accessed: {datetime.datetime.fromtimestamp(stats.st_atime)}")
        print(f"Creation Time: {datetime.datetime.fromtimestamp(stats.st_ctime)}")


