import sys
import argparse
import logging
import getpass

import vault
from autolock import GracefulKiller, VaultLockTimer
from exceptions import InvalidValue, PassError, DecryptErr

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_MINUTES = 5


def check_venv() -> None:
    """Verifica que el proceso corra dentro de un entorno virtual aislado."""
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        print("Advertencia: no estás corriendo dentro de un entorno virtual (venv).")
        respuesta = input("¿Continuar de todas formas? [y/N]: ")
        if respuesta.lower() != "y":
            sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lockr",
        description="LockerPass — gestor de contraseñas local. Sin subcomando, abre el menú interactivo."
    )
    parser.add_argument(
        "--vault", default="vault.enc",
        help="Ruta al archivo del vault (.enc). Default: vault.enc"
    )
    parser.add_argument(
        "--timeout", type=int, default=DEFAULT_TIMEOUT_MINUTES,
        help=f"Minutos de inactividad antes de bloquear el vault. Default: {DEFAULT_TIMEOUT_MINUTES}"
    )
    return parser


def start_session(vault_path: str):
    """Pregunta si registrar un vault nuevo o hacer login a uno existente."""
    from pathlib import Path
    if Path(vault_path).exists():
        print(f"Vault encontrado en {vault_path}.")
        return vault.login(vault_path)
    else:
        print(f"No existe un vault en {vault_path}. Creando uno nuevo.")
        return vault.register(vault_path)


def print_menu() -> None:
    print("\n[1] Agregar entrada")
    print("[2] Listar entradas")
    print("[3] Ver contraseña de una entrada")
    print("[4] Editar entrada")
    print("[5] Eliminar entrada")
    print("[6] Eliminar solo un campo (usuario o password)")
    print("[7] Salir")


def run_menu(vault_path: str, session_key, timer: VaultLockTimer) -> None:
    while True:
        print_menu()
        opcion = input("> ").strip()
        timer.touch()

        try:
            if opcion == "1":
                site = input("Sitio: ").strip()
                username = input("Usuario: ").strip()
                pw_input = getpass.getpass("Password (vacío para generar uno): ")
                password = pw_input if pw_input else None
                vault.add_entry(vault_path, session_key, site, username, password)
                print("Entrada guardada.")

            elif opcion == "2":
                for entry in vault.list_entries(vault_path):
                    print(f"- {entry['site']} ({entry['username']}) — {entry['created_at']}")

            elif opcion == "3":
                site = input("Sitio: ").strip()
                pw = vault.get_password(vault_path, session_key, site)
                print(f"Password: {pw}")

            elif opcion == "4":
                site = input("Sitio a editar: ").strip()
                new_username = input("Nuevo usuario (vacío para no cambiar): ").strip() or None
                new_pw = getpass.getpass("Nueva password (vacío para no cambiar): ")
                new_pw = new_pw if new_pw else None
                vault.edit_entry(vault_path, session_key, site,
                                  new_password=new_pw, new_username=new_username)
                print("Entrada actualizada.")

            elif opcion == "5":
                site = input("Sitio a eliminar: ").strip()
                vault.delete_entry(vault_path, site)
                print("Entrada eliminada.")

            elif opcion == "6":
                site = input("Sitio: ").strip()
                field = input("Campo a eliminar ('username' o 'password'): ").strip()
                vault.delete_field(vault_path, site, field)
                print("Campo eliminado.")

            elif opcion == "7":
                break

            else:
                print("Opción inválida.")

        except (InvalidValue, PassError, DecryptErr) as e:
            print(f"Error: {e}")
            logger.warning("Error manejado en el menú: %s", e)


def main() -> None:
    check_venv()
    parser = build_parser()
    args = parser.parse_args()

    session_key = start_session(args.vault)

    # SIGINT/SIGTERM limpian la clave de memoria al cerrar abruptamente
    killer = GracefulKiller(session_key)

    # Bloqueo automático por inactividad
    def on_lock():
        print("\n[!] Vault bloqueado por inactividad.")
        vault.logout(session_key)
        sys.exit(0)

    timer = VaultLockTimer(args.timeout, on_lock)
    timer.touch()

    try:
        run_menu(args.vault, session_key, timer)
    finally:
        if not killer.kill_now:
            vault.logout(session_key)
            print("Sesión cerrada.")


if __name__ == "__main__":
    main()

