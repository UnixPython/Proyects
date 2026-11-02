"""
Uso:
    python check.py
"""
import logging
import subprocess
import sys
import importlib
from exceptions import base, FailedModule

logger = logging.getLogger(__name__)

DEPENDENCIAS = [
    ("cryptography", "cryptography"),   # AES-XTS
    ("argon2-cffi", "argon2"),          # Argon2 (sesión)
]

# --- Módulos propios del proyecto ---
MODULOS_PROYECTO = [
    "cryptos",
    "session",
    "header",
    "disks",
    "memory",
    "commands",
    "check",
    "internal",
    "exceptions",
]

@base
def instalar_paquete(pip_name):
    """Instala un paquete de pip y retorna True si fue exitoso."""
    try:
        print(f"  Instalando {pip_name} ...")
        logger.info("Se realizó la acción de instalacion del paquete.")
        resultado = subprocess.run(
            [sys.executable, "-m", "pip", "install", pip_name, "--break-system-packages"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
        if resultado.returncode == 0:
            print("[+] librerias instalada con exito.")
            logger.info("Se instalaron: %s con exito.", pip_name)
            return True
        return False
    except FileNotFoundError:
        print("[!] No se encontró el binario pip.")
        logger.critical("Proceso cancelado por error de pip.")
        return False
    except subprocess.TimeoutExpired:
        print("[!] Tiempo de espera agotado.")
        return False

@base
def verificar_dependencias():
    """Verifica e instala dependencias externas. Retorna False si alguna falla."""
    print("=== 1. Verificando dependencias externas ===")
    todo_ok = True
    for pip_name, modulo in DEPENDENCIAS:
        try:
            importlib.import_module(modulo)
            print(f"[OK] {modulo} ya está disponible.")
        except ImportError:
            print(f"[FALTA] {modulo} no está instalado.")
            if not instalar_paquete(pip_name):
                print("No se pudo instalar el paquete.")
                todo_ok = False
                continue
            # reintentar el import tras instalar
            try:
                importlib.invalidate_caches()
                importlib.import_module(modulo)
                print(f"[OK] {modulo} importado correctamente tras instalar.")
            except ImportError as e:
                print(f"[ERROR] {modulo} sigue sin poder importarse: {e}")
                todo_ok = False
    return todo_ok

@base
def verificar_modulos_proyecto():
    """Verifica que los módulos locales se importen bien. Retorna True si todo pasa."""
    print("\n=== 2. Verificando módulos propios del proyecto ===")
    for nombre in MODULOS_PROYECTO:
        try:
            importlib.import_module(nombre)
            print(f"[OK] {nombre}.py importa sin errores.")
        except ModuleNotFoundError as e:
            raise FailedModule(f"[ERROR] {nombre}.py falló al importar: {type(e).__name__}: {e}") from e
    return True

@base
def main():
    """Función principal del script."""
    try:
        print("Verificación de entorno para EncrypFiler")
        deps_ok = verificar_dependencias()
        modulos_ok = verificar_modulos_proyecto()
        
        if deps_ok and modulos_ok:
            print("\n  [+] Verificación finalizada: python main.py registrar")
            sys.exit(0)
        else:
            print("\n[!] La verificación falló debido a problemas con las dependencias.")
            sys.exit(1)
    except RuntimeError:
        print("[!] Verificación ha fallado.")
        logger.warning("El proceso de verificación falló inesperadamente.")
        sys.exit(1)


if __name__ == "__main__":
    main()

