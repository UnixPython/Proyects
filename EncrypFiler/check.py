#!/usr/bin/env python3
"""
setup_check.py

Instala las dependencias necesarias para EncrypFiler (pycryptodome, bcrypt)
y verifica que todos los módulos del proyecto se puedan importar sin errores.

Uso:
    python setup_check.py
"""

import subprocess
import sys
import importlib

# --- Dependencias externas requeridas ---
# (nombre del paquete en pip, nombre del módulo a importar)
DEPENDENCIAS = [
    ("pycryptodome", "Crypto"),
    ("bcrypt", "bcrypt"),
]

# --- Módulos propios del proyecto ---
MODULOS_PROYECTO = [
    "core",
    "auth",
    "hashing",
    "filemanager",
    "cli",
]


def instalar_paquete(pip_name):
    print(f"  Instalando {pip_name} ...")
    resultado = subprocess.run(
        [sys.executable, "-m", "pip", "install", pip_name, "--break-system-packages"],
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        print(f"  [ERROR] No se pudo instalar {pip_name}:")
        print(resultado.stderr.strip())
        return False
    print(f"  [OK] {pip_name} instalado.")
    return True


def verificar_dependencias():
    print("=== 1. Verificando dependencias externas ===")
    todo_ok = True
    for pip_name, modulo in DEPENDENCIAS:
        try:
            importlib.import_module(modulo)
            print(f"  [OK] {modulo} ya está disponible.")
        except ImportError:
            print(f"  [FALTA] {modulo} no está instalado.")
            if not instalar_paquete(pip_name):
                todo_ok = False
                continue
            # reintentar el import tras instalar
            try:
                importlib.invalidate_caches()
                importlib.import_module(modulo)
                print(f"  [OK] {modulo} importado correctamente tras instalar.")
            except ImportError as e:
                print(f"  [ERROR] {modulo} sigue sin poder importarse: {e}")
                todo_ok = False
    return todo_ok


def verificar_modulos_proyecto():
    print("\n=== 2. Verificando módulos propios del proyecto ===")
    todo_ok = True
    for nombre in MODULOS_PROYECTO:
        try:
            importlib.import_module(nombre)
            print(f"  [OK] {nombre}.py importa sin errores.")
        except Exception as e:
            print(f"  [ERROR] {nombre}.py falló al importar: {type(e).__name__}: {e}")
            todo_ok = False
    return todo_ok


def main():
    print("Verificación de entorno para EncrypFiler\n")

    deps_ok = verificar_dependencias()
    modulos_ok = verificar_modulos_proyecto()

    print("\n=== Resumen ===")
    if deps_ok and modulos_ok:
        print("Todo listo. Puedes ejecutar: python main.py registrar")
        sys.exit(0)
    else:
        print("Hay problemas pendientes. Revisa los mensajes [ERROR] / [FALTA] arriba.")
        sys.exit(1)


if __name__ == "__main__":
    main()
