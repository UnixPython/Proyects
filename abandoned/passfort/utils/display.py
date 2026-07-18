import os

RED   = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

def show_password(password: str) -> None:
    print(f"Contraseña: {password}")

def show_vault(entries: list) -> None:
    clear_screen()
    titulo = "VAULT"
    print(f"{GREEN}{titulo.center(60, '=')}{RESET}")
    print("Gestión de credenciales".center(60))
    for correo, password in entries:
        print(f"correo: {correo:<25} contraseña: {password}")
    
def show_error(message: str) -> None:
    print(f"{RED}[!] {message}{RESET}")

def show_success(message: str) -> None:
    print(f"{GREEN}[+] {message}{RESET}")              

def clear_screen() -> None:
    command = "cls" if os.name == "nt" else "clear"
    os.system(command)
