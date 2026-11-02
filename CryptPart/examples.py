"""
examples.py — ejemplos de uso sobre un .img de prueba.
Ejecutar: python examples.py
Se crea un archivo temporal y se borra al final.
"""
import os
import secrets
import tempfile
import header
import disks
import cryptos

IMG = "prueba.img"
CLAVE = b"miClaveDePrueba"
SECTORES = 4

def crear_img():
    with open(IMG, "wb") as f:
        f.truncate(header.HEADER_AREA + SECTORES * cryptos.SECTOR)
    print(f"[+] Imagen creada: {IMG}")

def ejemplo_encriptar():
    fd = disks.block(IMG)
    master, header_raw = header.crear_volumen(CLAVE)
    os.pwrite(fd, header_raw, 0)
    datos = secrets.token_bytes(cryptos.SECTOR)
    disks.write_sector(fd, master, 0, datos)
    os.close(fd)
    print("[+] Sector 0 cifrado.")
    return datos

def ejemplo_desencriptar(datos_originales):
    fd = disks.block(IMG)
    header_raw = os.pread(fd, header.HEADER_AREA, 0)
    master = header.abrir_volumen(CLAVE, header_raw)
    recuperado = disks.read_sector(fd, master, 0)
    os.close(fd)
    assert recuperado == datos_originales, "Los datos no coinciden!"
    print("[+] Sector 0 descifrado correctamente.")

def limpiar():
    os.remove(IMG)
    print(f"[+] {IMG} eliminado.")

if __name__ == "__main__":
    crear_img()
    datos = ejemplo_encriptar()
    ejemplo_desencriptar(datos)
    limpiar()
    print("\n[OK] Todo funcionó.")
