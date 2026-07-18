#Librarys
import os
import logging 
import time
#------------------------
#Class Erros 
class ErrCode(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code 
#-----------------------------------
#Logger 
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
#---------------------------------
#Funtions
#----------------------------------
def enumeration():
    print("Se obtendrá información del sistema.")
    time.sleep(4)
    logger.info("Se ejecutó comandos desde shell.")

    kernel = os.popen("uname -a").read().strip()
    if not kernel:
        print("[-] uname no disponible.")
    else:
        print(kernel)

    os_release = os.popen("cat /etc/os-release").read().strip()
    if not os_release:
        print("[-] /etc/os-release no disponible.")
    else:
        print(os_release)

    hostname = os.popen("hostname").read().strip()
    if not hostname:
        print("[-] hostname no disponible.")
    else:
        print(hostname)

def privileges():
    print("Se obtendrá la información de usuarios y grupos.")
    time.sleep(5)
    comandos = [
        "cat /etc/hostname",
        "cat /etc/passwd",
        "cat /etc/group",
        "sudo -l",
        "env"
    ]
    with open("comandos.txt", "w") as archivo:
        for cmd in comandos:
            salida = os.popen(cmd).read()
            archivo.write(f"$ {cmd}\n")
            archivo.write(salida)
            archivo.write("\n")
            archivo.write("-" * 40)
            archivo.write("\n")
            print(f"$ {cmd}")
            print(salida)

if __name__ == "__main__":
    enumeration()
    privileges()
