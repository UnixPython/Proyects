import logging 
import os

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(
            filename="connect.log",
            encoding="utf-8"
        )
    ]
)

logger = logging.getLogger(__name__)

def find_external():
    try:
        rute = input("""
        Escribe la ruta ruta de la partición interna o externa.
        ej: /storage/6177-1919/   """).strip()
        if not rute:
            print("No escribiste ninguna ruta.")
        if not os.path.isdir(rute):
            print(f"La ruta '{rute}' no existe o no es un directorio.") 
    except KeyboardInterrupt as e:
        print("Se canceló el proceso.", e)
        logger.warning("Se canceló el procesó de busqueda.")

def browse():
    try:
        rutef = input("Directorio shizuku: ").strip()
        if rutef and os.path.isdir(rutef):
            print(os.listdir(rutef))
            return rutef
        else:
            print("No existe la carpeta de adb shizuku o rish")
    except KeyboardInterrupt as e:
        print("Se canceló el proceso.", e)

def execute():
    try:
        ru = browse()
        if ru:
            os.system(f'sh "{ru}/rish"')
        else: 
            print("no existe el binario")
    except KeyboardInterrupt as e:
        print("Se canceló el proceso.", e) 

find_external()
execute()
