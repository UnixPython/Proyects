import socket 
import logging
import os

class ServerErrno(Exception):
    """Excepcion de error de server."""
    pass

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("servers-logger.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        host = "127.0.0.1"
        port = 4852
    #creacion del socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        while True:
            filename = input("Archivo a enviar: ")
            raise KeyboardInterrupt("""
            Se interrumpió el proceso.""")

            if not os.path.isfile(filename):
                raise FileNotFoundError(filename)
            if not os.access(filename, os.R_OK):
                raise PermissionError(filename)

            fi = open(filename, "r")
            data = fi.read()
            if not data:
                print("Falló la data.")

        while data:
            sock.send(str(data).encode())
            data = fi.read()
            fi.close()

    except ConnectionRefusedError:
        print("""
        No se pudo conectar: el servidor no está disponible
        puerto o host fallido.""")
        logger.error("Conexión rechazada por el servidor.")
    
    except FileNotFoundError:
        print("Archivo no existe.")
        logger.warning("Falló el proceso de archivo.")
        raise

    except BrokenPipeError:
        print("Se perdió la conexión con el servidor durante el envio.")
        logger.error("BrokenPipeError: el servidor cerró la conexión mientras se enviaba")
        raise

    except PermissionError:
        print("No tienes permisos para leer ese archivo.")
        logger.warning(f"El archivo no tiene permisos.")
        raise

    except KeyboardInterrupt:
        print("Sé canceló el proceso.")
        logger.warning("El proceso fue cancelado por el usuario.")
        raise

    except OSError as e:
        raise ServerErrno(f"Fallo de red o host.{e}")
