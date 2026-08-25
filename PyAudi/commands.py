"""
DICCIONARIO COMPLETO DE COMANDOS DE SEGURIDAD LINUX
Automatización con Python - Sistema Operativo

Excluye: AUDITD
Incluye: AIDE, LYNIS, CHKROOTKIT, RKHUNTER, TRIPWIRE, COMANDOS INTEGRADOS
"""

class ComandosSeguridad:
    """Base de datos completa de comandos de seguridad Linux"""

    # ==================== AIDE ====================
    AIDE_INIT = [
        "sudo aideinit",
        "sudo aide --init --config=/etc/aide/aide.conf.d/70_aide_custom",
        "sudo aide --init --config=/etc/aide/aide.conf --gzip=no"
    ]

    AIDE_VERIFY = [
        "sudo aide --check",
        "sudo aide --check --gzip=no",
        "sudo aide --check --db=/var/lib/aide/aide.db.gz",
        "sudo aide --check --quiet"
    ]

    AIDE_UPDATE = [
        "sudo aide --update",
        "sudo aide --update --db-out=/var/lib/aide/aide.db.new.gz"
    ]

    AIDE_REPORTS = [
        "sudo aide --check --report=plain",
        "sudo aide --check --report=xml > aide_report.xml",
        "sudo aide --check --report=html > aide_report.html",
        "sudo aide --check > aide_check_$(date +%Y%m%d_%H%M%S).txt"
    ]

    AIDE_ADVANCED = [
        "aide --version",
        "aide --config=/etc/aide/aide.conf --print-config",
        "sudo aide --check-file=/etc/passwd",
        "aide --db=/var/lib/aide/aide.db.old.gz --db-out=/var/lib/aide/aide.db.new.gz --compare"
    ]

    # ==================== LYNIS ====================
    LYNIS_BASIC = [
        "sudo lynis audit system",
        "sudo lynis audit system --quiet",
        "sudo lynis audit system --pause-on-warning",
        "sudo lynis audit system --verbose"
    ]

    LYNIS_CATEGORIES = [
        "sudo lynis audit system --tests-from-group kernel",
        "sudo lynis audit system --tests-from-group authentication",
        "sudo lynis audit system --tests-from-group filesystems",
        "sudo lynis audit system --tests-from-group performance"
    ]

    LYNIS_TOOLS = [
        "sudo lynis show tests",
        "sudo lynis show settings",
        "sudo lynis show os",
        "sudo lynis show categories",
        "sudo lynis show controls"
    ]

    LYNIS_REPORTS = [
        "sudo lynis audit system > lynis_report_$(date +%Y%m%d_%H%M%S).txt",
        "sudo lynis audit system 2>&1 | grep -E 'Warning|Alert|Suggestion'",
        "sudo lynis audit system --no-colors",
        "sudo lynis audit system --quiet --no-colors"
    ]

    # ==================== CHKROOTKIT ====================
    CHKROOTKIT_SCAN = [
        "sudo chkrootkit",
        "sudo chkrootkit -q",
        "sudo chkrootkit -q 2>&1 | grep -v 'nothing found'",
        "sudo chkrootkit -v"
    ]

    CHKROOTKIT_SPECIFIC = [
        "sudo chkproc",
        "sudo chkutmp",
        "sudo chkwtmp",
        "sudo chkrootkit -l"
    ]

    CHKROOTKIT_REPORTS = [
        "sudo chkrootkit > chkrootkit_$(date +%Y%m%d_%H%M%S).log 2>&1",
        "sudo chkrootkit 2>&1 | grep -E 'INFECTED|SUSPICIOUS|WARNING'",
        "chkrootkit -V"
    ]

    CHKROOTKIT_DETAILED = [
        "sudo chkrootkit | grep passwd",
        "sudo chkrootkit | grep shadow",
        "sudo chkrootkit | grep inet",
        "sudo chkrootkit | grep lpd",
        "sudo chkrootkit | grep sniffer"
    ]

    # ==================== RKHUNTER ====================
    RKHUNTER_UPDATE = [
        "sudo rkhunter --update",
        "sudo rkhunter --update --nocolours"
    ]

    RKHUNTER_SCAN = [
        "sudo rkhunter --check",
        "sudo rkhunter --check --report-warnings-only",
        "sudo rkhunter --check --skip-keypress",
        "sudo rkhunter --check --nocolours",
        "sudo rkhunter --check --verbose"
    ]

    RKHUNTER_REPORTS = [
        "sudo rkhunter --check --report-warnings-only --report /tmp/rkhunter_report.txt",
        "sudo rkhunter --check --skip-keypress --nocolours 2>&1 | grep -E 'Warning|Warning:|Infected|Rootkit'",
        "sudo rkhunter --check --skip-keypress --nocolours 2>&1 | grep -c 'Warning'"
    ]

    RKHUNTER_INFO = [
        "rkhunter --version",
        "sudo rkhunter --show-config",
        "sudo rkhunter --show-warnings",
        "sudo rkhunter --list-warnings",
        "sudo rkhunter --enable-all-tests"
    ]

    RKHUNTER_FILES = [
        "sudo rkhunter --check-file /usr/bin/ls",
        "sudo rkhunter --propup",
        "sudo rkhunter --propup --update"
    ]

    # ==================== TRIPWIRE ====================
    TRIPWIRE_INIT = [
        "sudo twadmin -m F -c /etc/tripwire/tw.cfg -S /etc/tripwire/site.key",
        "sudo twadmin -m P -c /etc/tripwire/tw.cfg -p /etc/tripwire/tw.pol -S /etc/tripwire/site.key",
        "sudo tripwire --init",
        "sudo tripwire --init --interactive"
    ]

    TRIPWIRE_CHECK = [
        "sudo tripwire --check",
        "sudo tripwire --check --quiet",
        "sudo tripwire --check --email-report off",
        "sudo tripwire --check --report-level 4"
    ]

    TRIPWIRE_REPORTS = [
        "sudo tripwire --check --report-level 4",
        "sudo tripwire --check --report-level 4 > tripwire_report.txt",
        "sudo twprint -m r -t",
        "sudo twprint -m r -t --detail"
    ]

    TRIPWIRE_ADMIN = [
        "tripwire --version",
        "sudo twadmin -m C",
        "sudo twprint --print-dbfile"
    ]

    # ==================== USUARIOS Y GRUPOS ====================
    USUARIOS_INFO = [
        "cat /etc/passwd",
        "cut -d: -f1 /etc/passwd",
        "lastlog",
        "lastlog -u username",
        "who",
        "w",
        "id username",
        "whoami",
        "id -a",
        "sudo -l",
        "sudo cat /etc/sudoers",
        "sudo ls -la /etc/sudoers.d/"
    ]

    GRUPOS_INFO = [
        "cat /etc/group",
        "cut -d: -f1 /etc/group",
        "groups",
        "groups username",
        "getent group groupname",
        "id -Gn username"
    ]

    SHADOW_INFO = [
        "sudo cat /etc/shadow",
        "sudo cat /etc/shadow | grep -E 'username'",
        "sudo lastchage -l username",
        "sudo lastchage -l",
        "sudo cat /etc/shadow | awk -F: '$2 == \"!\" {print $1}'"
    ]

    # ==================== PERMISOS Y ARCHIVOS ====================
    PERMISOS_BASICOS = [
        "ls -la /path/to/file",
        "stat -c '%a %n' /path/to/file",
        "stat /etc/passwd",
        "df -T"
    ]

    PERMISOS_ESPECIALES = [
        "sudo find / -perm -4000 -type f 2>/dev/null",
        "sudo find / -perm -2000 -type f 2>/dev/null",
        "sudo find / -perm -1000 -type f 2>/dev/null",
        "sudo find / -perm -002 -type f 2>/dev/null"
    ]

    PERMISOS_ACL = [
        "getfacl /path/to/file",
        "setfacl -m u:username:rwx /path/to/file"
    ]

    FILESYSTEM_INFO = [
        "stat /",
        "blkid",
        "blkid -s LABEL",
        "blkid -s UUID"
    ]

    # ==================== PROCESOS Y SERVICIOS ====================
    PROCESOS_INFO = [
        "ps aux",
        "ps -u username",
        "ps aux --forest",
        "pgrep processname",
        "ps -p PID -o pid,ppid,user,stat,cmd",
        "ps eo user,pid,comm",
        "ps aux --sort=-%cpu | head -10",
        "ps aux --sort=-%mem | head -10",
        "ps aux | grep -E 'root|daemon|sys'"
    ]

    PROCESOS_MONITOR = [
        "top",
        "htop",
        "lsof -p PID",
        "lsof -i -P -n | grep LISTEN"
    ]

    SERVICIOS_INFO = [
        "systemctl list-units --type=service --state=running",
        "systemctl list-units --type=service",
        "systemctl list-unit-files --state=enabled",
        "systemctl list-unit-files --state=disabled",
        "systemctl list-dependencies --all"
    ]

    SERVICIOS_STATUS = [
        "systemctl status servicename",
        "systemctl is-enabled servicename",
        "systemctl show -p ExecMainPID servicename",
        "journalctl -u servicename -n 50"
    ]

    # ==================== KERNEL E INFORMACIÓN DEL SISTEMA ====================
    KERNEL_INFO = [
        "uname -a",
        "uname -r",
        "cat /proc/version",
        "cat /proc/cmdline",
        "lsmod",
        "modinfo modulename"
    ]

    KERNEL_MESSAGES = [
        "dmesg",
        "dmesg | grep -i error",
        "dmesg | tail -50",
        "dmesg | grep -i -E 'error|failed|fatal'"
    ]

    KERNEL_PARAMS = [
        "cat /sys/module/modulename/parameters/*"
    ]

    # ==================== LOGS DEL SISTEMA ====================
    LOGS_GENERAL = [
        "sudo cat /var/log/syslog",
        "sudo cat /var/log/auth.log",
        "sudo tail -f /var/log/auth.log",
        "sudo grep 'Failed password' /var/log/auth.log",
        "sudo grep 'sudo' /var/log/auth.log",
        "sudo grep 'ssh' /var/log/auth.log",
        "sudo grep 'su\\[' /var/log/auth.log"
    ]

    LOGS_JOURNALCTL = [
        "journalctl",
        "journalctl -n 50",
        "journalctl -f",
        "journalctl --since today",
        "journalctl --since yesterday",
        "journalctl --since '2 hours ago'",
        "journalctl -u servicename",
        "journalctl _UID=1000",
        "journalctl _PID=1234",
        "journalctl -o json | head -1",
        "journalctl -o verbose",
        "journalctl | wc -l",
        "journalctl -p alert",
        "journalctl -p crit",
        "journalctl -p err",
        "journalctl -p warning"
    ]

    LOGS_ROTACION = [
        "cat /etc/logrotate.conf",
        "cat /etc/logrotate.d/syslog",
        "du -sh /var/log/",
        "ls -lhS /var/log/*.log | head -10",
        "sudo journalctl --vacuum=7d",
        "sudo journalctl --vacuum-size=100M"
    ]

    # ==================== ALMACENAMIENTO Y DISCO ====================
    DISCO_INFO = [
        "lsblk",
        "blkid",
        "mount",
        "fdisk -l",
        "parted -l",
        "df -h",
        "du -sh *",
        "du -sh /* | sort -h"
    ]

    DISCO_ANALISIS = [
        "find / -type f -exec du {} + 2>/dev/null | sort -rh | head -10",
        "du -sh /* | sort -hr"
    ]

    FILESYSTEM_CHECK = [
        "sudo fsck -n /dev/sda1"
    ]

    # ==================== HARDWARE ====================
    HARDWARE_CPU = [
        "cat /proc/cpuinfo",
        "nproc"
    ]

    HARDWARE_MEMORY = [
        "cat /proc/meminfo",
        "free -h",
        "free -h -t -s 5"
    ]

    HARDWARE_SYSTEM = [
        "sudo dmidecode -t bios",
        "sudo dmidecode",
        "lspci",
        "lsusb",
        "cat /proc/scsi/scsi",
        "hdparm -I /dev/sda"
    ]

    # ==================== ARRANQUE Y CARGA ====================
    BOOT_TIME = [
        "systemd-analyze",
        "systemd-analyze blame",
        "systemd-analyze plot > boot.svg",
        "systemd-analyze blame | head -10",
        "systemd-analyze critical-chain"
    ]

    BOOT_INFO = [
        "dmesg | head -50",
        "cat /etc/default/grub"
    ]

    SYSTEM_LOAD = [
        "uptime",
        "cat /proc/uptime",
        "systemctl show -p ActiveEnterTimestamp",
        "last reboot | head -1"
    ]

    # ==================== SEGURIDAD ====================
    SECURITY_UMASK = [
        "umask",
        "cat /etc/login.defs | grep UMASK",
        "grep -E '^USERGROUPS_ENAB' /etc/login.defs"
    ]

    SECURITY_PASSWORD = [
        "sudo cat /etc/pam.d/common-password",
        "cat /etc/login.defs | grep PASS_",
        "sudo cat /var/log/faillog",
        "sudo lastchage -l",
        "sudo cat /etc/shadow | cut -d: -f1"
    ]

    SECURITY_SELINUX = [
        "getenforce",
        "sestatus"
    ]

    SECURITY_APPARMOR = [
        "sudo apparmor_status",
        "sudo apparmor_status | grep modules"
    ]

    # ==================== COMBINACIONES ÚTILES ====================
    QUICK_SECURITY_CHECK = [
        "who | wc -l",
        "sudo grep -c 'Failed password' /var/log/auth.log 2>/dev/null || echo 0",
        "sudo find / -perm -4000 -type f 2>/dev/null | wc -l",
        "sudo find / -perm -002 -type f 2>/dev/null | wc -l",
        "ps -u root | wc -l",
        "uptime | awk -F'load average:' '{print $2}'",
        "df -h / | tail -1 | awk '{print $5}'",
        "free | grep Mem | awk '{print int($3/$2*100)}'",
        "ss -tulpn 2>/dev/null | grep LISTEN | wc -l"
    ]

    # ==================== MÉTODOS PARA ACCEDER ====================
    @classmethod
    def get_all_commands(cls):
        """Retorna todos los comandos como diccionario plano"""
        commands = {}
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and attr_name != 'get_all_commands':
                attr = getattr(cls, attr_name)
                if isinstance(attr, list):
                    commands[attr_name.lower()] = attr
        return commands

    @classmethod
    def get_by_category(cls, category):
        """Retorna comandos de una categoría específica"""
        attr = getattr(cls, category.upper(), None)
        if isinstance(attr, list):
            return attr
        return None


# ==================== DICCIONARIO OPTIMIZADO PARA MAIN.PY ====================
COMANDOS = {
    # AIDE
    "aide_init": ComandosSeguridad.AIDE_INIT,
    "aide_verify": ComandosSeguridad.AIDE_VERIFY,
    "aide_update": ComandosSeguridad.AIDE_UPDATE,
    "aide_reports": ComandosSeguridad.AIDE_REPORTS,
    "aide_advanced": ComandosSeguridad.AIDE_ADVANCED,

    # LYNIS
    "lynis_basic": ComandosSeguridad.LYNIS_BASIC,
    "lynis_categories": ComandosSeguridad.LYNIS_CATEGORIES,
    "lynis_tools": ComandosSeguridad.LYNIS_TOOLS,
    "lynis_reports": ComandosSeguridad.LYNIS_REPORTS,

    # CHKROOTKIT
    "chkrootkit_scan": ComandosSeguridad.CHKROOTKIT_SCAN,
    "chkrootkit_specific": ComandosSeguridad.CHKROOTKIT_SPECIFIC,
    "chkrootkit_reports": ComandosSeguridad.CHKROOTKIT_REPORTS,
    "chkrootkit_detailed": ComandosSeguridad.CHKROOTKIT_DETAILED,

    # RKHUNTER
    "rkhunter_update": ComandosSeguridad.RKHUNTER_UPDATE,
    "rkhunter_scan": ComandosSeguridad.RKHUNTER_SCAN,
    "rkhunter_reports": ComandosSeguridad.RKHUNTER_REPORTS,
    "rkhunter_info": ComandosSeguridad.RKHUNTER_INFO,
    "rkhunter_files": ComandosSeguridad.RKHUNTER_FILES,

    # TRIPWIRE
    "tripwire_init": ComandosSeguridad.TRIPWIRE_INIT,
    "tripwire_check": ComandosSeguridad.TRIPWIRE_CHECK,
    "tripwire_reports": ComandosSeguridad.TRIPWIRE_REPORTS,
    "tripwire_admin": ComandosSeguridad.TRIPWIRE_ADMIN,

    # USUARIOS Y GRUPOS
    "usuarios_info": ComandosSeguridad.USUARIOS_INFO,
    "grupos_info": ComandosSeguridad.GRUPOS_INFO,
    "shadow_info": ComandosSeguridad.SHADOW_INFO,

    # PERMISOS
    "permisos_basicos": ComandosSeguridad.PERMISOS_BASICOS,
    "permisos_especiales": ComandosSeguridad.PERMISOS_ESPECIALES,
    "permisos_acl": ComandosSeguridad.PERMISOS_ACL,
    "filesystem_info": ComandosSeguridad.FILESYSTEM_INFO,

    # PROCESOS Y SERVICIOS
    "procesos_info": ComandosSeguridad.PROCESOS_INFO,
    "procesos_monitor": ComandosSeguridad.PROCESOS_MONITOR,
    "servicios_info": ComandosSeguridad.SERVICIOS_INFO,
    "servicios_status": ComandosSeguridad.SERVICIOS_STATUS,

    # KERNEL
    "kernel_info": ComandosSeguridad.KERNEL_INFO,
    "kernel_messages": ComandosSeguridad.KERNEL_MESSAGES,
    "kernel_params": ComandosSeguridad.KERNEL_PARAMS,

    # LOGS
    "logs_general": ComandosSeguridad.LOGS_GENERAL,
    "logs_journalctl": ComandosSeguridad.LOGS_JOURNALCTL,
    "logs_rotacion": ComandosSeguridad.LOGS_ROTACION,

    # DISCO Y ALMACENAMIENTO
    "disco_info": ComandosSeguridad.DISCO_INFO,
    "disco_analisis": ComandosSeguridad.DISCO_ANALISIS,
    "filesystem_check": ComandosSeguridad.FILESYSTEM_CHECK,

    # HARDWARE
    "hardware_cpu": ComandosSeguridad.HARDWARE_CPU,
    "hardware_memory": ComandosSeguridad.HARDWARE_MEMORY,
    "hardware_system": ComandosSeguridad.HARDWARE_SYSTEM,

    # BOOT
    "boot_time": ComandosSeguridad.BOOT_TIME,
    "boot_info": ComandosSeguridad.BOOT_INFO,
    "system_load": ComandosSeguridad.SYSTEM_LOAD,

    # SEGURIDAD
    "security_umask": ComandosSeguridad.SECURITY_UMASK,
    "security_password": ComandosSeguridad.SECURITY_PASSWORD,
    "security_selinux": ComandosSeguridad.SECURITY_SELINUX,
    "security_apparmor": ComandosSeguridad.SECURITY_APPARMOR,

    # QUICK CHECKS
    "quick_check": ComandosSeguridad.QUICK_SECURITY_CHECK,
}


if __name__ == "__main__":
    # Mostrar todas las categorías disponibles
    print("CATEGORÍAS DE COMANDOS DISPONIBLES:")
    print("=" * 60)
    for key in sorted(COMANDOS.keys()):
        cantidad = len(COMANDOS[key])
        print(f"  • {key:<30} [{cantidad} comandos]")

    print("\n" + "=" * 60)
    print(f"TOTAL: {len(COMANDOS)} categorías")
    print(f"TOTAL COMANDOS: {sum(len(v) for v in COMANDOS.values())}")

