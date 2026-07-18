import time
import sys
from permises    import permises, commands
from enumeration import enumeration, privileges
from privileges  import enum_sudo, run_all, try_custom_cmd
from lists       import enum_cronjobs, enum_writable

def rainbow_banner():
    colors = [
        "\033[91m", "\033[93m", "\033[92m",
        "\033[96m", "\033[94m", "\033[95m",
    ]
    reset = "\033[0m"
    bold  = "\033[1m"

    banner = [
        "  __  ___     ____           __  ____              __  ",
        " /  |/  /_ __/ __ \\__ _____ / / / __ \\___  ___  / /_  ",
        "/ /|_/ / // / /_/ / // (_-</ /_/ /_/ / _ \\/ _ \\/ __/  ",
        "/_/  /_/\\_, /\\____/\\_,_/___/\\____\\____/\\___/\\___/\\__/  ",
        "       /___/          Root!                             ",
    ]

    print()
    for i, line in enumerate(banner):
        color = colors[i % len(colors)]
        print(bold + color + line + reset)
        time.sleep(0.05)

    bar = ""
    for i in range(55):
        bar += colors[i % len(colors)] + "─"
    print(bold + bar + reset)
    print()


def menu():
    options = {
        "1": ("System Info",     enumeration),
        "2": ("Users & Groups",  privileges),
        "3": ("Permisos & SUID", permises),
        "4": ("Capabilities",    commands),
        "5": ("Sudo Enum",       enum_sudo),
        "6": ("Cron Jobs",       enum_cronjobs),
        "7": ("Writable Paths",  enum_writable),
        "8": ("Auto PrivEsc",    run_all),
        "9": ("Shell Manual",    try_custom_cmd),
        "0": ("Run ALL",         None),
    }

    colors = [
        "\033[91m", "\033[93m", "\033[92m",
        "\033[96m", "\033[94m", "\033[95m",
    ]
    reset = "\033[0m"
    bold  = "\033[1m"

    for i, (k, (name, _)) in enumerate(options.items()):
        color = colors[i % len(colors)]
        print(bold + color + f"  [{k}] {name}" + reset)

    print()
    opt = input("\033[1m\033[97m> \033[0m").strip()

    if opt == "0":
        for k, (name, fn) in options.items():
            if fn and k != "0":
                print(f"\n\033[1m\033[92m[*] {name}\033[0m")
                time.sleep(0.5)
                fn()
    elif opt in options:
        name, fn = options[opt]
        if fn:
            print(f"\n\033[1m\033[92m[*] {name}\033[0m\n")
            fn()
    else:
        print("\033[91m[-] Opción inválida.\033[0m")


def main():
    rainbow_banner()
    menu()

if __name__ == "__main__":
    enumeration()
    privileges()
