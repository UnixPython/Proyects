import os
import logging
from datetime import datetime

LOG = "enum_output.txt"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("enum.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run(cmd: str) -> str:
    out = os.popen(cmd).read().strip()
    with open(LOG, "a") as f:
        f.write(f"\n[{datetime.now()}] $ {cmd}\n{out}\n{'─'*40}\n")
    print(out)
    return out


def enum_cronjobs():
    logger.info("[*] Enumerando Cron Jobs...")
    cmds = [
        "cat /etc/crontab",
        "ls -la /etc/cron.d/",
        "cat /etc/cron.d/*",
        "ls -la /etc/cron.hourly/",
        "ls -la /etc/cron.daily/",
        "ls -la /etc/cron.weekly/",
        "ls -la /etc/cron.monthly/",
        "crontab -l",
        "ls -la /var/spool/cron/",
        "ls -la /var/spool/cron/crontabs/",
        "cat /var/spool/cron/crontabs/* 2>/dev/null",
        # scripts ejecutados por root escribibles por otros
        "grep -r 'CRON' /var/log/syslog 2>/dev/null | tail -20",
        "grep -r 'CMD' /var/log/cron.log 2>/dev/null | tail -20",
    ]
    for cmd in cmds:
        run(cmd)


def enum_writable():
    logger.info("[*] Enumerando Writable Paths...")
    cmds = [
        # archivos escribibles excluyendo ruido
        "find / -writable -type f -not -path '/proc/*' -not -path '/sys/*' -not -path '/dev/*' 2>/dev/null",
        # directorios escribibles
        "find / -writable -type d -not -path '/proc/*' -not -path '/sys/*' -not -path '/dev/*' 2>/dev/null",
        # SUID y escribible al mismo tiempo → vector directo
        "find / -writable -perm -4000 -not -path '/proc/*' 2>/dev/null",
        # scripts de cron que son escribibles
        "find /etc/cron* -writable -type f 2>/dev/null",
        "find /var/spool/cron -writable -type f 2>/dev/null",
        # PATH actual y dirs escribibles dentro de él
        "echo $PATH",
        "find $(echo $PATH | tr ':' ' ') -writable -type f 2>/dev/null",
    ]
    for cmd in cmds:
        run(cmd)


if __name__ == "__main__":
    print("1) Cron Jobs\n2) Writable Paths\n3) Ambos")
    opt = input("> ").strip()

    if opt == "1":
        enum_cronjobs()
    elif opt == "2":
        enum_writable()
    elif opt == "3":
        enum_cronjobs()
        enum_writable()

    print(f"\n[+] Output guardado en: {LOG}")
