import logging
import subprocess

from exceptions import InvalidProcess

logger = logging.getLogger(__name__)

def execute(command: str, lists: list[str]) -> tuple[list[str], list[InvalidProcess]]:
    resultados = []
    errores = []
    for cmd in lists:
        logger.info(f"[{command}] Ejecutando: {cmd}")
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                text=True,
                capture_output=True,
                check=True,
            )
            resultados.append(result.stdout)
        except subprocess.CalledProcessError as e:
            errores.append(InvalidProcess(e.returncode, e.cmd))
            logger.error(f"[{command}] Falló: {cmd} (código {e.returncode})")
    return resultados, errores
