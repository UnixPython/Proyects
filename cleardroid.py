import subprocess
import os
from colorama import Fore, init

RISH = ["sh", "/storage/01CD-14F2/rish/rish"]

# Path y generacion de logs

def log(msg):
    try:
        with open("log.txt", "a") as f:
            f.write(msg + "\n")
    except Exception as e:
        print("Hubo un error general en la generación de logs.", e)

def verify_path():
    dir_path = "/storage/01CD-14F2/rish/"
    if os.path.exists(dir_path):
        print(f"El directorio {dir_path} existe.")
        log("Verificación de directorio: existe")
    else:
        print(f"El directorio: {dir_path} no existe")
        log("Verificación de directorio: no existe")

def clean():
    try:
        result = subprocess.run(
            RISH + ["-c", "pm trim-caches 1G"],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        log("Se ejecutó limpieza de caché")
    except subprocess.CalledProcessError as e:
        print(f"No se ha podido realizar la limpieza. {e.returncode}")
        print(f"Error: {e.stderr}")
        log(f"Error limpiando caché: {e.stderr}")

def packages():
    try:
        result = subprocess.run(
            RISH + ["-c", "pm list packages"],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        log("Se listaron paquetes")
    except subprocess.CalledProcessError:
        print("No se ejecutó el comando")
        log("Error al listar paquetes")

def delete_dates():
    try:
        package = input("Package: ")
        result = subprocess.run(
            RISH + ["-c", f"pm clear {package}"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        log(f"Se borraron datos del paquete {package}")
    except subprocess.CalledProcessError as e:
        print(f"Paquete no encontrado. {e.returncode}")
        log(f"Error borrando datos del paquete {package}")

def clean_clipboard():
    try:
        result = subprocess.run(
            RISH + ["-c", "am broadcast -a clipper.set --es text ''"],
            capture_output=True,
            text=True,
            check=True,
        )
        log("Clipboard limpiado")
        return result.stdout
    except subprocess.CalledProcessError:
        print("Comando desconocido.")
        log("Error limpiando clipboard")

def disable_packages():
    try:
        disable = input("Package to disable: ")
        result = subprocess.run(
            RISH + ["-c", f"pm disable-user {disable}"],
            capture_output=True,
            text=True,
            check=True,
        )
        log(f"Paquete deshabilitado: {disable}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Hubo un error al ejecutar el comando.")
        print(f"Error to execute. {e.stderr}")
        log(f"Error deshabilitando paquete {disable}")

def dump():
    try:
        dumps = input("App para ver permisos: ")
        result = subprocess.run(
            RISH + ["-c", f"pm dump {dumps} | grep permission"],
            capture_output=True,
            text=True,
            check=True,
        )
        log(f"Dump de permisos ejecutado para {dumps}")
        return result.stdout
    except subprocess.CalledProcessError:
        print("Hubo un error al obtener los dumps.")
        log("Error en dump de permisos")

# funciones para ver sistema

def get_battry_info():
    try:
        result = subprocess.run(
            RISH + ["-c", "dumpsys battery"],
            capture_output=True,
            text=True,
            check=True
        )
        log("Consulta de batería ejecutada")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("No se pudo obtener los datos de batería")
        print(f"Error: {e.stderr}")
        log("Error obteniendo batería")

def get_ram_usage():
    try:
        result = subprocess.run(
            RISH + ["-c", "cat /proc/meminfo"],
            capture_output=True,
            text=True,
            check=True
        )
        log("Consulta de RAM ejecutada")
        print(result.stdout)
    except Exception:
        print("No se pudo obtener los datos")
        log("Error obteniendo RAM")

def get_storage_info():
    try:
        result = subprocess.run(
            RISH + ["-c", "df -h /data"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
        log("Consulta de almacenamiento ejecutada")
    except subprocess.CalledProcessError:
        print("Comando no existe.")
        log("Error obteniendo almacenamiento")

init(autoreset=True)

print(Fore.CYAN + r"""
  ____  _                    _           _     _
 / ___|| | ___  __ _ _ __ __| |_ __ ___ (_) __| |
| |    | |/ _ \/ _` | '__/ _` | '__/ _ \| |/ _` |
| |___ | |  __/ (_| | | | (_| | | | (_) | | (_| |
 \____||_|\___|\__,_|_|  \__,_|_|  \___/|_|\__,_|
""")

while True:
    print("\n[1] Verificar directorio")
    print("[2] Listar paquetes")
    print("[3] Limpiar caché")
    print("[4] Borrar datos de un paquete")
    print("[5] Limpiar clipboard")
    print("[6] Deshabilitar paquete")
    print("[7] Ver permisos de app")
    print("[8] Información de batería")
    print("[9] Uso de RAM")
    print("[10] Almacenamiento")
    print("[0] Salir")

    opcion = input("\nElige una opción: ")

    # Ya imprimen solas — no tocar
    if opcion == "1":
        verify_path()

    elif opcion == "2":
        packages()

    elif opcion == "3":
        clean()

    elif opcion == "4":
        delete_dates()

    elif opcion == "9":
        get_ram_usage()

    elif opcion == "10":
        get_storage_info()

    elif opcion == "5":
        resultado = clean_clipboard()
        print(resultado)

    elif opcion == "6":
        resultado = disable_packages()
        print(resultado)

    elif opcion == "7":
        resultado = dump()
        print(resultado)

    elif opcion == "8":
        resultado = get_battry_info()
        print(resultado)

    elif opcion == "0":
        log("Programa cerrado")
        break
    else:
        print("Opción inválida")


