import subprocess
import hashlib 
import platform 

def mac_addres() -> str:
    try:
        disk_id = subprocess.check_output(
    ["getprop", "ro.serialno"],
    stderr=subprocess.DEVNULL
).decode().strip()
        arch = platform.machine()
        combined = "|".join([disk_id, arch])
        signature = hashlib.sha256(combined.encode()).hexdigest()
        return signature
    except subprocess.CalledProcessError:
        return "unknown"

if __name__ == "__main__":
    print(mac_addres())
