# ──────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────
import hashlib
import logging 
import os 
import subprocess
import uuid 
import pyudev  

# ──────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────
logger = logging.getLogger(__name__)
#___________________________________________
#Class
class GetDisksError(Exception):
    """Manejo de errir al obtener datos en disco."""
    pass 
#__________________________________________ 

# ──────────────────────────────────────────
# FUNCIONES
# ──────────────────────────────────────────
def machine() -> str:
    """Obtiene el machine-id del sistema."""
    try:
        fp = "/etc/machine-id"
        if os.path.isfile(fp):
            print("Archivo machine-id existe.")
            with open(fp) as f:
                return f.read().strip()
            logger.info("El archivo se leyó.")
        else:
            print("El archivo no existe.")
            return ""
    except IOError as e:
        print(f"El archivo tiene un error de lectura. Revisar la distribución de linux.{e}")
        logger.warning("Se detectó falla en el archivo.")
        return ""

def get_system_uuid():
    """Obtiene el UUID SMBIOS mediante dmidecode."""
    try:
        result = subprocess.run(
            ["dmidecode", "-s", "system-uuid"],
            capture_output=True,
            text=True,
            check=True
        )
        uuid_system = result.stdout.strip()
    except subprocess.SubprocessError:
        print("Hubo un fallo en la ejecución del comando. Intente de nuevo.")
    except KeyboardInterrupt as e:
        print(f"Se canceló el proceso al obtener el UUID. {e}")


def get_mac_address():
    """Obtiene la mac"""
    mac = uuid.getnode()
    mac_str = ":".join(
        f"{(mac >> ele) & 0xff:02x}"
        for ele in range(40, -1, -8)
    )
    print(mac_str)

def get_disk_serial():
    """Obtiene el serial del disco principal."""
    context = pyudev.Context()
    for device in context.list_devices(subsystem='block', DEVTYPE='disk'):

        print("----")
        print("NODE:", device.device_node)
        print("MODEL:", device.get("ID_MODEL"))
        print("VENDOR:", device.get("ID_VENDOR"))
        print("SERIAL:", device.get("ID_SERIAL_SHORT"))
        print("UUID:", device.get("ID_PART_TABLE_UUID"))
        print("----")

    raise GetDisksError("Hubo un fallo al obtener datos de los discos.")
   
def build_fingerprint(components: dict) -> str:
    """Genera el fingerprint SHA-256."""

