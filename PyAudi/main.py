import sys
import logging
from audit import execute
from commands import COMANDOS
from exceptions import InvalidProcess

logger = logging.getLogger(__name__)

def run_categoria(categoria: str) -> None:
    lista = COMANDOS.get(categoria)
    if lista is None:
        print(f"[!] Categoría '{categoria}' no existe.")
        print("Disponibles:", ", ".join(sorted(COMANDOS.keys())))
        return

    try:
        for salida in execute(categoria, lista):
            print(salida)
    except InvalidProcess as e:
        print(f"[!] Falló: {e.cmd} (código {e.returncode})")
    except KeyboardInterrupt:
        print("Se canceló el proceso")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python main.py <categoria>")
        print("Disponibles:", ", ".join(sorted(COMANDOS.keys())))
        sys.exit(1)

    run_categoria(sys.argv[1])
